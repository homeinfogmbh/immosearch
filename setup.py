#! /usr/bin/env python3

from distutils.core import setup

setup(
    name='immosearch',
    version='latest',
    author='Richard Neumann',
    packages=['immosearch'],
    scripts=['files/immosearchd'],
    data_files=[('/usr/lib/systemd/system', ['files/immosearch.service'])],
    license=open('LICENSE.txt').read(),
    description='Real estate search engine.')
