#!/usr/bin/env python3

"""
See http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html for a list of status code
"""

from .rfc7285 import mimetypes
import logging
import traceback

def format_error(response, message=''):
    """
    TODO: format message in application/alto-error+json
    """
    response.set_header('content-type', mimetypes.ERROR)
    return message

def bad_request(response, **kargs):
    response.status = 400 # Bad request
    return format_error(response, **kargs)

def unauthorized(response, auth_method, **kargs):
    response.status = 401 # unauthorized
    response.set_header('WWW-Authenticate', auth_method)
    return format_error(response, **kargs)

def not_found(response, service=None):
    response.status = 404 # Not found
    if service is not None:
        logging.info('Failed to find service %s', service)
    return format_error(response)

def not_allowed(response, allow, **kargs):
    response.status = 405 # Method not allowed
    response.set_header('Allow', ','.join(allow))
    return format_error(response, **kargs)

def not_acceptable(response, **kargs):
    response.status = 406 # Not acceptable
    return format_error(response, **kargs)

def not_supported(response, **kargs):
    response.status = 415 # media type unsupported
    return format_error(response, **kargs)

def server_error(response, cause = '', exception = None, **kargs):
    response.status = 500 # Internal Server Error
    if exception is not None:
        logging.error('Server error %s', exception)
        traceback.print_tb(exception.__traceback__)
        message = '{}: {}'.format(type(exception), exception)

        return format_error(response, message = message, **kargs)
    kargs.pop('message', '')
    return format_error(response, message=cause, **kargs)

def not_implemented(response, **kargs):
    response.status = 501 # Not implemented
    return format_error(response, **kargs)

