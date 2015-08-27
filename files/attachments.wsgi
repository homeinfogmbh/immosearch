#! /usr/bin/env python3
"""WSGI main program for ImmoSearch"""

from immosearch.wsgi import AttachmentController

application = AttachmentController()
