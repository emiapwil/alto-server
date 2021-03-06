#!/usr/bin/env python3

from .. import Backend
from . import mimetypes

import mimeparse
import logging
import distutils.util
from .. import errors

def mime_matches(provides, required):
    return len(mimeparse.best_match(provides, required)) > 0

def check_and_run(do_process, request, response):
    if do_process is None:
        return errors.not_implemented(response)
    return do_process(request, response)

class BasicAbstractBackend(Backend):
    """
    """

    def __init__(self, config, allowed):
        Backend.__init__(self, config)
        self.allowed = allowed

    def get(self, request, response, actual_get = None):
        return errors.not_allowed(response, self.allowed)

    def post(self, request, response, actual_post = None):
        return errors.not_allowed(response, self.allowed)

    def put(self, request, response, actual_put = None):
        return errors.not_allowed(response, self.allowed)

    def delete(self, request, response, actual_delete = None):
        return errors.not_allowed(response, self.allowed)

class MIMEHelper():
    """
    """

    def __init__(self, consumes, provides):
        self._consumes = consumes
        self._provides = provides

    def can_provide(self, mime):
        return mime_matches(self._provides, mime)

    def provides(self, index):
        return self._provides[index]

    def can_consume(self, mime):
        return mime_matches(self._consumes, mime)

class AbstractIRDBackend(BasicAbstractBackend):
    """
    """

    PROVIDES = [ mimetypes.IRD, mimetypes.ERROR ]

    def __init__(self, config):
        BasicAbstractBackend.__init__(self, config, ['GET'])

    def get(self, request, response, actual_get = None):
        provides = AbstractIRDBackend.PROVIDES
        if not mime_matches(provides, request.get_header('accept')):
            return errors.not_acceptable(response)

        response.set_header('content-type', mimetypes.IRD)
        return check_and_run(actual_get, request, response)

class FilterableMapBackend(BasicAbstractBackend):
    """
    """

    def __init__(self, config, consumes, provides, filtered = False):
        try:
            _filtered = distutils.util.strtobool(config.get('basic', 'filtered', fallback='False'))
            filtered = filtered or (_filtered == 1)
        except Exception as e:
            logging.warning('Invalid value for filtered option: %s', e)
            raise e
        allowed = ['GET', 'POST'] if filtered else ['GET']
        BasicAbstractBackend.__init__(self, config, allowed)
        self.mime = MIMEHelper(consumes, provides)
        self.filtered = filtered

    def get(self, request, response, actual_get = None):
        if not self.mime.can_provide(request.get_header('accept')):
            return errors.not_acceptable(response)

        response.set_header('content-type', self.mime.provides(0))
        return check_and_run(actual_get, request, response)

    def post(self, request, response, actual_post = None):
        if not self.filtered:
            return errors.not_allowed(response, ['GET'])

        if not self.mime.can_consume(request.get_header('content-type')):
            return errors.not_supported(response)

        response.set_header('content-type', self.mime.provides(0))
        return check_and_run(actual_post, request, response)

class AbstractNetworkMapBackend(FilterableMapBackend):
    """
    """

    CONSUMES = [ mimetypes.NETWORK_MAP_FILTER ]
    PROVIDES = [ mimetypes.NETWORK_MAP, mimetypes.ERROR ]

    def __init__(self, config, filtered = False):
        consumes = AbstractNetworkMapBackend.CONSUMES
        provides = AbstractNetworkMapBackend.PROVIDES
        FilterableMapBackend.__init__(self, config, consumes, provides, filtered)

class AbstractCostMapBackend(FilterableMapBackend):
    """
    """

    CONSUMES = [ mimetypes.COST_MAP_FILTER ]
    PROVIDES = [ mimetypes.COST_MAP, mimetypes.ERROR ]

    def __init__(self, config, filtered = False):
        consumes = AbstractCostMapBackend.CONSUMES
        provides = AbstractCostMapBackend.PROVIDES
        FilterableMapBackend.__init__(self, config, consumes, provides, filtered)

class AbstractEndpointXXXMapBackend(BasicAbstractBackend):
    """
    """
    def __init__(self, config, consumes, provides):
        BasicAbstractBackend.__init__(self, config, ['POST'])
        self.mime = MIMEHelper(consumes, provides)

    def post(self, request, response, actual_post = None):
        if not self.mime.can_consume(request.get_header('content-type')):
            return errors.not_supported(response)

        response.set_header('content-type', self.mime.provides(0))
        return check_and_run(actual_post, request, response)

class AbstractEndpointPropMapBackend(AbstractEndpointXXXMapBackend):
    """
    """

    CONSUMES = [ mimetypes.ENDPOINT_PROP_PARAMS ]
    PROVIDES = [ mimetypes.ENDPOINT_PROP_MAP, mimetypes.ERROR ]

    def __init__(self, config):
        consumes = AbstractEndpointPropMapBackend.CONSUMES
        provides = AbstractEndpointPropMapBackend.PROVIDES
        AbstractEndpointXXXMapBackend.__init__(self, config, consumes, provides)

class AbstractEndpointCostMapBackend(AbstractEndpointXXXMapBackend):
    """
    """

    CONSUMES = [ mimetypes.ENDPOINT_COST_PARAMS ]
    PROVIDES = [ mimetypes.ENDPOINT_COST, mimetypes.ERROR ]

    def __init__(self, config):
        consumes = AbstractEndpointCostMapBackend.CONSUMES
        provides = AbstractEndpointCostMapBackend.PROVIDES
        AbstractEndpointXXXMapBackend.__init__(self, config, consumes, provides)
