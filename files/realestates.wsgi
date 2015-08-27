#! /usr/bin/env python3
"""WSGI main program for ImmoSearch"""

from immosearch.wsgi import RealEstateController

def application(environ, start_response):
    """Main WSGI method"""
    ctrl = RealEstateController(environ)
    status, response_headers, response_body = ctrl.run()
    start_response(status, response_headers)
    return [response_body]
