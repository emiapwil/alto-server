from .. import Backend
from . import mimetypes

import mimeparse

def not_implemented(response):
    response.status = 501 # Not implemented
    return ''


def not_acceptable(response):
    response.status = 406 # Not acceptable
    return ''


def not_allowed(response, allow):
    response.status = 405 # Method not allowed
    response.set_header('Allow', ','.join(allow))
    return ''


def not_supported(response):
    response.status = 415 # media type unsupported
    return ''


def mime_matches(provides, required):
    return len(mimeparse.best_match(provides, required)) > 0

def process(request, response, do_process):
    if do_process is None:
        return not_implemented(response)
    return do_process(request, response)


class BasicIRDBackend(Backend):

    PROVIDES = [ mimetypes.IRD, mimetypes.ERROR ]

    def __init__(self):
        Backend.__init__(self)


    def get(self, request, response, actual_get = None):
        provides = BasicIRDBackend.PROVIDES
        if not mime_matches(provides, request.get_header('accept')):
            return not_acceptable(response)

        response.set_header('content-type', mimetypes.IRD)
        return process(request, response, actual_get)


    def post(self, request, response, actual_post = None):
        return not_allowed(response, ['GET'])


    def put(self, request, response, actual_put = None):
        return not_allowed(response, ['GET'])


    def delete(self, request, response, actual_delete = None):
        return not_allowed(response, ['GET'])


class FilterableMapBackend(Backend):

    def __init__(self, provides, consumes, filtered = False):
        Backend.__init__(self)
        self.provides = provides
        self.consumes = consumes
        self.filtered = filtered

    def get(self, request, response, actual_get = None):
        if not mime_matches(self.provides, request.get_header('accept')):
            return not_acceptable(response)

        response.set_header('content-type', self.provides[0])
        return process(request, response, actual_get)

    def post(self, request, response, actual_post = None):
        if not self.filtered:
            return not_allowed(response, ['GET'])

        if not mime_matches(self.consumes, request.get_header('content-type')):
            return not_supported(response)

        response.set_header('content-type', self.provides[0])
        return process(request, response, actual_post)

    def put(self, request, response, actual_put = None):
        return not_allowed(response, ['GET'] + (['POST'] if self.filtered else []))

    def delete(self, request, response, actual_delete = None):
        return not_allowed(response, ['GET'] + (['POST'] if self.filtered else []))


class BasicNetworkMapBackend(FilterableMapBackend):

    CONSUMES = [ mimetypes.NETWORK_MAP_FILTER ]
    PROVIDES = [ mimetypes.NETWORK_MAP, mimetypes.ERROR ]

    def __init__(self, filtered = False):
        provides = BasicNetworkMapBackend.PROVIDES
        consumes = BasicNetworkMapBackend.CONSUMES
        FilterableMapBackend.__init__(self, provides, consumes, filtered)


class BasicCostMapBackend(FilterableMapBackend):

    PROVIDES = [ mimetypes.COST_MAP, mimetypes.ERROR ]
    CONSUMES = [ mimetypes.COST_MAP_FILTER ]

    def __init__(self, filtered = False):
        provides = BasicCostMapBackend.PROVIDES
        consumes = BasicCostMapBackend.CONSUMES
        FilterableMapBackend.__init__(self, provides, consumes, filtered)

