"""
Models for Calendar Tab.
"""
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class CourseCalendar(models.Model):
    """
    Mapping: Edx course - Google calendar.
    """
    course_id = models.CharField(max_length=255)
    calendar_id = models.CharField(max_length=255, primary_key=True)

    class Meta(object):
        app_label = "calendar_tab"
        unique_together = ('course_id', 'calendar_id')

    def __str__(self):
        return self.calendar_id


@python_2_unicode_compatible
class CourseCalendarEvent(models.Model):
    """
    Model to control events ownership.
    """
    course_calendar = models.ForeignKey(CourseCalendar,
                                        on_delete=models.CASCADE)
    event_id = models.CharField(max_length=255)
    edx_user = models.CharField(max_length=255)

    class Meta(object):
        app_label = "calendar_tab"
        unique_together = ('course_calendar', 'event_id')

    def __str__(self):
        return self.event_id
