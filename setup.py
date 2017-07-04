import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="edx-calendar-tab",
    version="0.1",
    install_requires=[
        "setuptools",
        "google-api-python-client==1.6.2",
        "pytz==2016.7",
        "python-dateutil==2.1",
        "web-fragments==0.2.2",
    ],
    requires=[],
    packages=["calendar_tab"],
    description='Open Edx Calendar tab (based on Google Calendar service)',
    long_description=README,
    entry_points={
        "openedx.course_tab": [
            "calendar = calendar_tab.plugins:CalendarTab"
        ],
    }
)
