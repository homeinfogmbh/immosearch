#! /usr/bin/env python3
"""WSGI main program for ImmoSearch"""

from immosearch.wsgi import Controller

def application(environ, start_response):
    """Main WSGI method"""
    ctrl = Controller(environ.get('PATH_INFO', ''),
                      environ.get('QUERY_STRING', ''))
    status, response_headers, response_body = ctrl.run()
    start_response(status, response_headers)
    return [response_body]
