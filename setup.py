import re
import sys
import os
from codecs import open
from setuptools import setup

tests_require = ['nose', 'mock', 'testfixtures', 'blinker']

DJANGO_VERSION = os.environ.get('DJANGO_VERSION', None)
FLASK_VERSION  = os.environ.get('FLASK_VERSION', None)

# For some reason, Django 2.2.5 gets installed for Python 3.4, but breaks.
# Python 3.4 is not officially supported by the 2.2 series, so not sure what's going on here.
# Work-around is to force Django 1.11 to be installed for Python 3.4
if sys.version_info[0:2] == (3, 4):
    DJANGO_VERSION = '1.11'

if DJANGO_VERSION:
    tests_require.append('django=={}'.format(DJANGO_VERSION))
else:
    tests_require.append('django>=1.11')

if FLASK_VERSION:
    tests_require.append('Flask=={}'.format(FLASK_VERSION))
else:
    tests_require.append('Flask>=1.0')

    
def get_version():
    with open('honeybadger/version.py', encoding='utf-8') as f:
        return re.search(r'^__version__ = [\'"]([^\'"]+)[\'"]', f.read(), re.M).group(1)


setup(
    name='honeybadger',
    version=get_version(),
    description='Send Python and Django errors to Honeybadger',
    url='https://github.com/honeybadger-io/honeybadger-python',
    author='Dave Sullivan',
    author_email='dave@davesullivan.ca',
    license='MIT',
    packages=['honeybadger', 'honeybadger.contrib'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: System :: Monitoring'
    ],
    install_requires=[
        'psutil',
        'six'
    ],
    test_suite='nose.collector',
    tests_require=tests_require
)
