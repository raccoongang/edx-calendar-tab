import logging

from django.conf import settings

from path import Path as path

log = logging.getLogger(__name__)

DEFAULT_VENV_ROOT = settings.ENV_ROOT / 'venvs/edxapp'
VENV_ROOT = path(settings.ENV_TOKENS.get('VENV_ROOT', DEFAULT_VENV_ROOT))

settings.MAKO_TEMPLATES['main'].extend([
    VENV_ROOT / 'src/edx-calendar-tab/calendar_tab/templates',
])

log.debug('MAKO_TEMPLATES["main"]: {}'.format(settings.MAKO_TEMPLATES['main']))

settings.PIPELINE_CSS.update({
    'style-calendar-tab': {
        'source_filenames': [
            VENV_ROOT / 'src/edx-calendar-tab/calendar_tab/static/calendar_tab/css/vendor/scheduler/dhtmlxscheduler.css',
        ],
        'output_filename': 'css/calendar-tab.css',
    }
})

log.debug('PIPELINE_CSS["style-calendar-tab"]: {}'.format(settings.PIPELINE_CSS["style-calendar-tab"]))

settings.PIPELINE_JS.update({
    'calendar_tab': {
        'source_filenames': [
            VENV_ROOT / 'src/edx-calendar-tab/calendar_tab/static/calendar_tab/js/calendar-tab.js',
        ],
        'output_filename': 'js/calendar_tab.js',
    },
    'calendar_tab_vendor': {
        'source_filenames': [
            VENV_ROOT / 'src/edx-calendar-tab/calendar_tab/static/calendar_tab/js/vendor/scheduler/_dhtmlxscheduler.js',
            VENV_ROOT / 'src/edx-calendar-tab/calendar_tab/static/calendar_tab/js/vendor/scheduler/dhtmlxscheduler_readonly.js',
        ],
        'output_filename': 'js/calendar_tab_vendor.js',
    },
})

log.debug('PIPELINE_JS["calendar_tab"]: {}'.format(settings.PIPELINE_JS["calendar_tab"]))
log.debug('PIPELINE_JS["calendar_tab_vendor"]: {}'.format(settings.PIPELINE_JS["calendar_tab_vendor"]))
