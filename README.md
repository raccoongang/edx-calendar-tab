**NOTE:** this is a draft README for not fully implemented yet feature.

# edx-calendar-tab
Shared calendar for Open edX Courseware


Django application that allows course staff enable new "Calendar" tab from CMS (studio).
From LMS side appears new "Calendar" tab with google calendar associated with current course.
New calendar events may be created by any enrolled student.
Calendar may be shared by stuff personal with provided google accounts (with update permission).

1) Install Package

installing manually for evaluation and testing:

    sudo su - edxapp -s /bin/bash
    . edxapp_env
    pip install --upgrade https://github.com/raccoongang/edx-calendar-tab/tarball/master


2) Configure edx-platform

Add "edx-calendat-tab" to installed Django apps

In /edx/app/edxapp/lms.env.json [and /edx/app/edxapp/cms.env.json], add

    "ADDL_INSTALLED_APPS": ["calendar_tab"],

In /edx/app/edxapp/lms.envs.json, add to the list of FEATURES:

    "ENABLE_CALENDAR": true,
    "GOOGLE_CALENDAR_TAB_PRIVATE_KEY_URL": "/edx/app/edxapp/edx-calendar-tab-google-api-private-key.json"





3) BASIC USAGE

    From the very beginning after calendar tab is enabled, there is no any google calendar associated with current course,
so staff has to initialize one at first time.
    After initialization new google calendar is rendered on the tab.
    Students can create/update/delete events.
    Staff can share course calendar with other google accounts.