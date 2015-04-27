from palto import Backend
import json
import mimeparse

class TestBackend(Backend):

    def __init__(self):
        Backend.__init__(self)

    def accept(self, expected, accept):
        return mimeparse.best_match(expected, accept)

    def get(self, request, response):
        accepts = self.accept(['application/json'], request.get_header('accept'))
        if len(accepts) == 0:
            response.status = 406
            return "error"
        return json.dumps({ 'hello' : 'world' })

def create_instance(config):
    return TestBackend()
