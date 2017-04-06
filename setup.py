#! /usr/bin/env python3

from distutils.core import setup

setup(
    name='immosearch',
    version='latest',
    author='Richard Neumann',
    packages=['immosearch'],
    data_files=[
        ('/etc', ['files/immosearch.conf']),
        ('/usr/share', ['files/immosearch.wsgi']),
        ('/etc/uwsgi/apps-available', ['files/immosearch.ini'])],
    license=open('LICENSE.txt').read(),
    description='Real estate search engine')
