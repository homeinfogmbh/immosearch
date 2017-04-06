#! /usr/bin/env python3
"""WSGI main program for ImmoSearch"""

from wsgilib import WsgiApp
from immosearch.wsgi import ImmoSearchHandler

application = WsgiApp(ImmoSearchHandler, cors=True)
