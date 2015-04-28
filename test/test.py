#!/usr/bin/env python3

from palto.rfc7285.basic import AbstractNetworkMapBackend
import json
import mimeparse

class TestBackend(AbstractNetworkMapBackend):

    def __init__(self, config):
        AbstractNetworkMapBackend.__init__(self, config, filtered = True)

    def accept(self, expected, accept):
        return mimeparse.best_match(expected, accept)

    def _get(self, request, response):
        return json.dumps({ 'hello' : 'world' })

    def get(self, request, response):
        actual_get = lambda request, response: self._get(request, response)
        return AbstractNetworkMapBackend.get(self, request, response, actual_get)

    def _post(self, request, response):
        return self._get(request, response)

    def post(self, request, response):
        actual_post = lambda req, rep: self._post(req, rep)
        return AbstractNetworkMapBackend.post(self, request, response, actual_post)

def create_instance(config, global_config):
    return TestBackend(config)
