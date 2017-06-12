import logging

from django.conf import settings

from path import Path as path

log = logging.getLogger(__name__)

DEFAULT_VENV_ROOT = settings.ENV_ROOT / 'venvs/edxapp'
VENV_ROOT = path(settings.ENV_TOKENS.get('VENV_ROOT', DEFAULT_VENV_ROOT))

settings.MAKO_TEMPLATES['main'].extend([
    VENV_ROOT / 'src/edx-calendar-tab/calendar_tab/templates',
])

log.warn('MAKO_TEMPLATES["main"]: {}'.format(settings.MAKO_TEMPLATES['main']))
