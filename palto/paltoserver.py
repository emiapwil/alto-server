#!/usr/bin/env python3

import bottle
from . import errors

BACKEND_NAME_PATTERN='<name:re:.*>'

class PaltoServer(bottle.Bottle):
    """
    """

    def __init__(self, **kargs):
        bottle.Bottle.__init__(self, **kargs)

        self.backends = kargs.pop('backends', {})
        self.setup_routes()

    def setup_routes(self):
        root_callback = lambda : self.get_route('')
        self.add_route(bottle.Route(self, '/', 'GET', root_callback, name='alto-service'))

        get = lambda name: self.get_route(name)
        post = lambda name: self.post_route(name)
        put = lambda name: self.put_route(name)
        delete = lambda name: self.delete_route(name)
        callbacks = {'GET' : get, 'POST' : post, 'PUT' : put, 'DELETE' : delete }
        for method, callback in callbacks.items():
            path = '/{}'.format(BACKEND_NAME_PATTERN)
            self.add_route(bottle.Route(self, path, method, callback))

    def add_backend(self, name, backend):
        if name in self.backends:
            raise Exception('The name %s has been registered'.format(name))
        self.backends[name] = backend

    def get_backends(self):
        return self.backends

    def get_backend(self, name):
        return self.backends.get(name)

    def remove_backend(self, name):
        self.backends.pop(name)

    def dispatch(self, name, task_template):
        backend = self.get_backend(name)
        if backend is None:
            return errors.not_found(bottle.response, service=name)

        try:
            return task_template(backend, bottle.request, bottle.response)
        except Exception as e:
            return errors.server_error(bottle.response, exception=e)

    def get_route(self, name):
        get = lambda backend, request, response: backend.get(request, response)
        return self.dispatch(name, get)

    def post_route(self, name):
        post = lambda backend, request, response: backend.post(request, response)
        return self.dispatch(name, post)

    def put_route(self, name):
        put = lambda backend, request, response: backend.put(request, response)
        return self.dispatch(name, put)

    def delete_route(self, name):
        delete = lambda backend, request, response: backend.delete(request, response)
        return self.dispatch(name, delete)

def test():
    from .rfc7285 import AbstractNetworkMapBackend
    import configparser
    nmb = AbstractNetworkMapBackend(configparser.ConfigParser(), False)

    server = PaltoServer()
    server.add_backend('test', nmb)

    get_url = lambda : 'base url: {}'.format(server.get_url('alto-service'))
    server.add_route(bottle.Route(server, '/get_baseurl', 'GET', get_url))

    server.run(host='localhost', port=3400, debug=True)

if __name__ == '__main__':
    test()
