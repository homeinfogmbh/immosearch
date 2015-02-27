#! /usr/bin/env python3

from distutils.core import setup

setup(name='immosearch',
      version='0.0.1',
      author='Richard Neumann',
      author_email='mail@richard-neumann.de',
      requires=['openimmo',
                'pyxb'],
      packages=['immosearch'],
      data_files=[('/usr/local/etc', ['files/immosearch.conf']),
                  ('/usr/local/lib/immosearch', ['files/immosearch.wsgi'])],
      license=open('LICENSE.txt').read(),
      description='Real estate browser',
      long_description=open('README.txt').read(),
      )
