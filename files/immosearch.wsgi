#! /usr/bin/env python3
"""WSGI main program for ImmoSearch"""

from immosearch.wsgi import Controller

def application(environ, start_response):
    """Main WSGI method"""
    wsgi = Controller(environ.get('PATH_INFO', ''),
                      environ.get('QUERY_STRING', ''))
    status, response_body, content_type, charset = wsgi.run()
    response_headers = [('Content-Type',
                         '; '.join([content_type,
                                    '='.join(['charset', charset])])),
                       ('Content-Length', str(len(response_body))),
                       ('Access-Control-Allow-Origin', '*')]
    start_response(status, response_headers)
    return [response_body]
