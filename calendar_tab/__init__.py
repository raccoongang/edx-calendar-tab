import logging

from django.conf import settings

from path import Path as path

log = logging.getLogger(__name__)

APP_ROOT = path(__file__).abspath().dirname()

settings.MAKO_TEMPLATES['main'].extend([
    APP_ROOT / 'templates',
])

log.debug('MAKO_TEMPLATES["main"]: {}'.format(settings.MAKO_TEMPLATES['main']))

settings.PIPELINE_CSS.update({
    'style-calendar-tab': {
        'source_filenames': [
            APP_ROOT / 'static/calendar_tab/css/vendor/scheduler/dhtmlxscheduler.css',
        ],
        'output_filename': 'css/calendar-tab.css',
    }
})

log.debug('PIPELINE_CSS["style-calendar-tab"]: {}'.format(settings.PIPELINE_CSS["style-calendar-tab"]))

settings.PIPELINE_JS.update({
    'calendar_tab': {
        'source_filenames': [
            APP_ROOT / 'static/calendar_tab/js/calendar-tab.js',
        ],
        'output_filename': 'js/calendar_tab.js',
    },
    'calendar_tab_vendor': {
        'source_filenames': [
            APP_ROOT / 'static/calendar_tab/js/vendor/scheduler/_dhtmlxscheduler.js',
            APP_ROOT / 'static/calendar_tab/js/vendor/scheduler/dhtmlxscheduler_readonly.js',
        ],
        'output_filename': 'js/calendar_tab_vendor.js',
    },
})

log.debug('PIPELINE_JS["calendar_tab"]: {}'.format(settings.PIPELINE_JS["calendar_tab"]))
log.debug('PIPELINE_JS["calendar_tab_vendor"]: {}'.format(settings.PIPELINE_JS["calendar_tab_vendor"]))
