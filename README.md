
# edx-calendar-tab

Shared calendar for Open edX Courseware

Django application that allows course staff enable new "Calendar" tab
from CMS (studio).
From LMS side appears new "Calendar" tab with google calendar
associated with current course.
New calendar events may be created by any enrolled student.
Calendar may be shared by stuff personal with provided google accounts
(with update permission).

# Installation

## Install Package

Installing manually for evaluation and testing:

    sudo -sHu edxapp
    . edxapp_env
    pip install -e git+https://github.com/raccoongang/edx-calendar-tab.git@wowkalucky/event_permissions#egg=edx-calendar-tab


## Production installation

 TBD

# Configuration

## Configure google service account

Google service accounts [documentation](https://developers.google.com/identity/protocols/OAuth2ServiceAccount).

In general process consists of these steps:

* create new Project in [developers console](https://console.developers.google.com/projectselector/iam-admin/serviceaccounts);
* create new Service Account via Project (with "Owner" role);
* [enable](https://console.developers.google.com/apis/dashboard)
Google Calendar API via Project;
* [create](https://console.developers.google.com/apis/credentials)
credentials for Service Account (service account key) and save json-api-private-key -
_you'll need to put it on your server into "/edx/app/edxapp/", for example_;

## Configure edx-platform

Add "edx-calendar-tab" to installed Django apps

In "/edx/app/edxapp/lms.env.json" add

    "ADDL_INSTALLED_APPS": ["calendar_tab"],

In "/edx/app/edxapp/edx-platform/lms/envs/common.py" add

    MAKO_TEMPLATES['main']: [
        ...
        '/edx/app/edxapp/venvs/edxapp/src/edx-calendar-tab/calendar_tab/templates',
    ]

    PIPELINE_CSS = {
        ...
        'style-calendar-tab': {
            'source_filenames': [
                '/edx/app/edxapp/venvs/edxapp/src/edx-calendar-tab/calendar_tab/static/calendar_tab/css/vendor/scheduler/dhtmlxscheduler.css',
            ],
            'output_filename': 'css/calendar-tab.css',
        }
    }

    PIPELINE_JS = {
        ...
        'calendar_tab': {
            'source_filenames': [
                '/edx/app/edxapp/venvs/edxapp/src/edx-calendar-tab/calendar_tab/static/calendar_tab/js/calendar-tab.js',
            ],
            'output_filename': 'js/calendar_tab.js',
        },
        'calendar_tab_vendor': {
            'source_filenames': [
                '/edx/app/edxapp/venvs/edxapp/src/edx-calendar-tab/calendar_tab/static/calendar_tab/js/vendor/scheduler/_dhtmlxscheduler.js',
                '/edx/app/edxapp/venvs/edxapp/src/edx-calendar-tab/calendar_tab/static/calendar_tab/js/vendor/scheduler/dhtmlxscheduler_readonly.js',
            ],
            'output_filename': 'js/calendar_tab_vendor.js',
        },
    }

In "/edx/app/edxapp/edx-platform/lms/urls.py" add __before__ static_tab urls:

    if settings.FEATURES.get('ENABLE_CALENDAR'):
        urlpatterns += (
           url(
               r'^courses/{}/tab/calendar/'.format(
                   settings.COURSE_ID_PATTERN,
               ),
               include('calendar_tab.urls'),
               name='calendar_tab_endpoints',
           ),
        )

In "/edx/app/edxapp/lms.envs.json", add to the list of FEATURES:

    "ENABLE_CALENDAR": true,
    "GOOGLE_CALENDAR_TAB_PRIVATE_KEY_URL": "/edx/app/edxapp/edx-calendar-tab-google-api-private-key.json"

# Basic usage

  From the very beginning after calendar tab is enabled, there is no
  any google calendar associated with current course, so staff has to
  initialize one at first time by submitting "Initiate course google
  calendar" button.

  Application then creates new Google Calendar (from behalf of Google
  service account) and associates it with the current Course.
  This Calendar is private and can't be seen out of service account.

  After initialization new google calendar is rendered on the tab.

  Students and Staff can create/update/delete events.
  Students can't update/delete event they don't own.
  Staff can.

  Events may be edited via dialog box(on double click), by dragging
  (whole event or its start/end border).

ADDITIONAL NOTES:

  As the OpenEdx [documentation](https://openedx.atlassian.net/wiki/display/AC/Adding+a+new+course+tab) says:

    The course stores a static list of its tabs in the database, and
    this list is only updated when one of the following actions take place:
    - You create a new course.
    - You update the advanced settings for your course.
    This means that if you have a pre-existing course then it won't
    immediately show a tab even after you've registered the new entry point.
