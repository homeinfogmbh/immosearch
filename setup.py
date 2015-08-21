#! /usr/bin/env python3

from distutils.core import setup

setup(name='immosearch',
      version='1.0.0',
      author='Richard Neumann',
      author_email='mail@richard-neumann.de',
      requires=['openimmo',
                'homeinfo.crm',
                'openimmodb2',
                'pyxb',
                'pyqrcode',
                'png'],
      packages=['immosearch'],
      data_files=[('/etc', ['files/immosearch.conf']),
                  ('/usr/share/immosearch',
                   ['files/realestates.wsgi',
                    'files/attachments.wsgi']),
                  ('/etc/uwsgi/apps-available',
                   ['files/realestates.ini',
                    'files/attachments.ini'])],
      license=open('LICENSE.txt').read(),
      description='Real estate search engine',
      long_description=open('README.txt').read(),
      )
