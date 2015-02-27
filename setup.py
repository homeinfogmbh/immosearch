#! /usr/bin/env python3

from distutils.core import setup

setup(name='immosearch',
      version='1.0.0',
      author='Richard Neumann',
      author_email='mail@richard-neumann.de',
      requires=['openimmo',
                'openimmodb2',
                'homeinfo.crm'
                'pyxb'],
      packages=['immosearch'],
      data_files=[('/usr/local/etc', ['files/immosearch.conf']),
                  ('/usr/local/lib/immosearch', ['files/immosearch.wsgi'])],
      license=open('LICENSE.txt').read(),
      description='Real estate search engine',
      long_description=open('README.txt').read(),
      )
