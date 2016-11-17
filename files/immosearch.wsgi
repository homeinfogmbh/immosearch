#! /usr/bin/env python3
"""WSGI main program for ImmoSearch"""

from homeinfo.lib.wsgi import WsgiApp
from immosearch.wsgi import ImmoSearchHandler

application = WsgiApp(ImmoSearchHandler, cors=True)
