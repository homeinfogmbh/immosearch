#! /usr/bin/env python3
"""WSGI main program for ImmoSearch"""

from immosearch.wsgi import WSGI

def application(environ, start_response):
    """Main WSGI method"""
    wsgi_result = WSGI(environ['PATH_INFO'], environ['QUERY_STRING']).run()
    status, response_body, content_type, charset = wsgi_result
    response_headers = [('Content-Type',
                         '; '.join([content_type,
                                    '='.join(['charset', charset])])),
                       ('Content-Length', str(len(response_body))),
                       ('Access-Control-Allow-Origin', '*')]
    start_response(status, response_headers)
    return [response_body]
