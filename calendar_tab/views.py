from datetime import datetime
import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from opaque_keys.edx.keys import CourseKey
from courseware.access import has_access
from courseware.courses import get_course_with_access
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView
from web_fragments.fragment import Fragment

import pytz
from dateutil import parser

from .models import CourseCalendar, CourseCalendarEvent
from .utils import gcal_service

log = logging.getLogger(__name__)


def from_google_datetime(g_datetime):
    """
    Formats google calendar API datetime string to dhxscheduler
    datetime string.
    Example: "2017-04-25T16:00:00-04:00" >> "04/25/2017 16:00"
    """
    dt = parser.parse(g_datetime)
    local_dt = dt.astimezone(pytz.timezone(settings.TIME_ZONE))
    return local_dt.strftime("%m/%d/%Y %H:%M")


def to_google_datetime(dhx_datetime):
    """
    Formats google dhxscheduler datetime string to calendar API
    datetime string.
    Example: "04/25/2017 16:00" >> "2017-04-25T16:00:00-04:00"
    """
    dt_unaware = datetime.strptime(dhx_datetime, "%m/%d/%Y %H:%M")
    dt_aware = timezone.make_aware(dt_unaware, timezone.get_current_timezone())
    return dt_aware.isoformat()


def get_calendar_id_by_course_id(course_id):
    """
    Returns google calendar ID by given course key.
    """
    course_calendar_data = CourseCalendar.objects.filter(
        course_id=course_id).values('course_id', 'calendar_id').first()
    calendar_id = course_calendar_data.get(
        'calendar_id') if course_calendar_data else ''
    return calendar_id


def _create_base_calendar_view_context(request, course_id):
    """
    Returns the default template context for rendering calendar view.
    """
    user = request.user
    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(user, 'load', course_key,
                                    check_if_enrolled=True)
    return {
        'csrf': csrf(request)['csrf_token'],
        'course': course,
        'user': user,
        'is_staff': is_staff(user, course_id),
        'calendar_id': get_calendar_id_by_course_id(course_id),
    }


def has_permission(user, api_event):
    """
    Has given User the permission to edit given Event?
    """
    try:
        db_event = CourseCalendarEvent.objects.get(event_id=api_event['id'])
        return user.username == db_event.edx_user or is_staff(
            user, db_event.course_calendar.course_id)
    except (ObjectDoesNotExist, KeyError) as e:
        log.warn(e)
        return False


def is_staff(user, course_id):
    """
    Is this User the Personnel of the Course with this ID?
    """
    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(user, 'load', course_key,
                                    check_if_enrolled=True)
    return bool(has_access(user, 'staff', course, course_id))


class CalendarTabFragmentView(EdxFragmentView):
    """
    Component implementation of the calendar tab.
    """
    def render_to_fragment(self, request, course_id=None, **kwargs):
        """
        Render the calendar tab to a fragment.
        Args:
            request: The Django request.
            course_id: The id of the course.

        Returns:
            Fragment: The fragment representing the calendar tab.
        """
        try:
            context = _create_base_calendar_view_context(request, course_id)
            log.debug(context)
            html = render_to_string('calendar_tab/calendar_tab_fragment.html',
                                    context)
            fragment = Fragment(html)
            self.add_fragment_resource_urls(fragment)

            inline_js = render_to_string(
                'calendar_tab/calendar_tab_js.template', context)
            fragment.add_javascript(inline_js)
            return fragment

        except Exception as e:
            log.exception(e)
            html = render_to_string('calendar_tab/500_fragment.html')
            return Fragment(html)

    def vendor_js_dependencies(self):
        """
        Returns list of vendor JS files that this view depends on.
        The helper function that it uses to obtain the list of vendor JS files
        works in conjunction with the Django pipeline to ensure that
        in development mode the files are loaded individually,
        but in production just the single bundle is loaded.
        """
        dependencies = set(self.get_js_dependencies('calendar_tab_vendor'))
        return list(dependencies)

    def js_dependencies(self):
        """
        Returns list of JS files that this view depends on.
        The helper function that it uses to obtain the list of JS files
        works in conjunction with the Django pipeline to ensure that
        in development mode the files are loaded individually,
        but in production just the single bundle is loaded.
        """
        return self.get_js_dependencies('calendar_tab')

    def css_dependencies(self):
        """
        Returns list of CSS files that this view depends on.
        The helper function that it uses to obtain the list of CSS files
        works in conjunction with the Django pipeline to ensure that
        in development mode the files are loaded individually, but in
        production just the single bundle is loaded.
        """
        return self.get_css_dependencies('style-calendar-tab')


def events_view(request, course_id):
    """
    Returns all google calendar events for given course.
    """
    calendar_id = get_calendar_id_by_course_id(course_id)
    try:
        response = gcal_service.events().list(calendarId=calendar_id,
                                              pageToken=None).execute()
        events = [{
            "id": api_event["id"],
            "text": api_event["summary"],
            "start_date": from_google_datetime(api_event["start"]["dateTime"]),
            "end_date": from_google_datetime(api_event["end"]["dateTime"]),
            "readonly": not has_permission(request.user, api_event)
        } for api_event in response['items']]
    except Exception as e:
        log.exception(e)
        return JsonResponse(data={'errors': e}, status=500, safe=False)
    else:
        return JsonResponse(data=events, status=200, safe=False)


def _get_event_data(post_data, course_id):
    event = {
        'id': post_data.get('id'),
        'summary': post_data['text'],
        'location': post_data.get('description', ''),
        'description': post_data.get('description', ''),
        'start': {
            'dateTime': to_google_datetime(post_data['start_date']),
        },
        'end': {
            'dateTime': to_google_datetime(post_data['end_date']),
        },
        'course_id': course_id,
    }
    return event


def _create_event(request, course_id, response):
    """
    Creates new event in google calendar and returns feedback.
    """
    calendar_id = get_calendar_id_by_course_id(course_id)
    event = _get_event_data(request.POST, course_id)
    try:
        new_event = gcal_service.events().insert(calendarId=calendar_id,
                                                 body=event).execute()
    except Exception as e:
        log.exception(e)
        status = 500
    else:
        cc_event = CourseCalendarEvent(course_calendar_id=calendar_id,
                                       event_id=new_event['id'],
                                       edx_user=request.user)
        cc_event.save()

        status = 201
        response.update({"action": "inserted",
                         "tid": new_event['id']})

    return status, response


def _update_event(request, course_id, response):
    """
    Updates given event in google calendar and returns feedback.
    """
    calendar_id = get_calendar_id_by_course_id(course_id)
    event = _get_event_data(request.POST, course_id)
    try:
        if has_permission(request.user, event):
            updated_event = gcal_service.events()\
                                        .update(calendarId=calendar_id,
                                                eventId=event['id'],
                                                body=event).execute()
            status = 200
            response.update({"action": "updated",
                             "sid": event["id"],
                             "tid": updated_event["id"]})
        else:
            status = 403
            response["tid"] = event["id"]

    except Exception as e:
        log.exception(e)
        status = 500

    return status, response


def _delete_event(request, course_id, response):
    """
    Deletes given event in google calendar and returns feedback.
    """
    calendar_id = get_calendar_id_by_course_id(course_id)
    event = _get_event_data(request.POST, course_id)
    try:
        if has_permission(request.user, event):
            gcal_service.events().delete(calendarId=calendar_id,
                                         eventId=event['id']).execute()
            try:
                CourseCalendarEvent.objects.get(event_id=event['id']).delete()
            except ObjectDoesNotExist as e:
                log.warn(e)

            status = 200
            response.update({"action": "deleted",
                             "sid": event["id"]})
        else:
            status = 403
            response["tid"] = event["id"]

    except Exception as e:
        log.exception(e)
        status = 500

    return status, response


@csrf_exempt
def dataprocessor_view(request, course_id):
    """
    Processes insert/update/delete event requests.
    """
    status = 401
    response = {'action': 'error',
                'sid': request.POST['id'],
                'tid': '0'}

    if request.method == 'POST':
        command = request.POST['!nativeeditor_status']

        if command == 'inserted':
            status, response = _create_event(request, course_id, response)
        elif command == 'updated':
            status, response = _update_event(request, course_id, response)
        elif command == 'deleted':
            status, response = _delete_event(request, course_id, response)

    return JsonResponse(data=response, status=status, safe=False)


class InitCalendarView(View):
    """
    Creates google calendar and associates it with course.
    """
    def post(self, request, *args, **kwargs):
        course_id = request.POST.get('courseId')
        if course_id is None:
            return HttpResponse("Provide courseID", status=400)

        calendar_data = {
            'summary': request.POST.get('courseId'),
            'timeZone': settings.TIME_ZONE}

        try:
            created_calendar = gcal_service.calendars().insert(
                body=calendar_data).execute()
        except Exception as e:
            log.exception(e)
            return JsonResponse(data={'errors': e}, status=500, safe=False)
        else:
            CourseCalendar.objects.create(course_id=course_id,
                                          calendar_id=created_calendar['id'])
            return JsonResponse({"calendarId": created_calendar['id']},
                                status=201)
