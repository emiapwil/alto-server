#!/usr/bin/env python3

"""
See http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html for a list of status code
"""

from .rfc7285 import mimetypes
import logging
import traceback
import bottle

def is_error(code):
    return not code in [200, 204]

def format_error(response = bottle.response, message='', exception = None):
    """
    TODO: format message in application/alto-error+json
    """
    response.set_header('content-type', mimetypes.ERROR)
    if exception is not None:
        traceback.print_tb(exception.__traceback__)
    print('hello')
    return message

def bad_request(response = bottle.response, **kargs):
    response.status = 400 # Bad request
    return format_error(response, **kargs)

def unauthorized(response = bottle.response, auth_method = 'basic', **kargs):
    response.status = 401 # unauthorized
    response.set_header('WWW-Authenticate', auth_method)
    return format_error(response, **kargs)

def not_found(response = bottle.response, service=None):
    response.status = 404 # Not found
    if service is not None:
        logging.info('Failed to find service %s', service)
    return format_error(response)

def not_allowed(response = bottle.response, allow = [], **kargs):
    response.status = 405 # Method not allowed
    response.set_header('Allow', ','.join(allow))
    return format_error(response, **kargs)

def not_acceptable(response = bottle.response, **kargs):
    response.status = 406 # Not acceptable
    return format_error(response, **kargs)

def not_supported(response = bottle.response, **kargs):
    response.status = 415 # media type unsupported
    return format_error(response, **kargs)

def server_error(response = bottle.response, cause = '', **kargs):
    response.status = 500 # Internal Server Error
    exception = kargs.get('exception')
    if exception is not None:
        logging.error('Server error %s', exception)
        cause = '{}: {}'.format(type(exception), exception)

    kargs.pop('message', '')
    return format_error(response, message=cause, **kargs)

def not_implemented(response = bottle.response, **kargs):
    response.status = 501 # Not implemented
    return format_error(response, **kargs)

