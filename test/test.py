from palto.rfc7285.basic import BasicNetworkMapBackend
import json
import mimeparse

class TestBackend(BasicNetworkMapBackend):

    def __init__(self):
        BasicNetworkMapBackend.__init__(self, filtered = True)

    def accept(self, expected, accept):
        return mimeparse.best_match(expected, accept)

    def _get(self, request, response):
        return json.dumps({ 'hello' : 'world' })

    def get(self, request, response):
        actual_get = lambda request, response: self._get(request, response)
        BasicNetworkMapBackend.get(self, request, response, actual_get)

    def _post(self, request, response):
        return self._get(request, response)

    def post(self, request, response):
        actual_post = lambda req, rep: self._post(req, rep)
        BasicNetworkMapBackend.post(self, request, response, actual_post)

def create_instance(config):
    return TestBackend()
