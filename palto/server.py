#!/usr/bin/env python3

import argparse
import bottle
import json
import sys
import logging
import traceback
from . import palto_config, frontend, backend
from .rfc7285 import mimetypes

@bottle.route('/test')
def test():
    bottle.response.set_header('Content-type', 'applicatoin/test+json')
    return json.dumps({ 'a' : 1, 'b' : 2})

class PaltoServer():
    """
    """

    instance = None

    def __init__(self, **args):
        config_file = args.pop('config', None)
        config = palto_config.parse(config_file)

        # check the setting for the frontend
        server_info = frontend.get_server_info(config)
        if (server_info is None):
            raise Exception("Missing fields in config file")

        # check the settings for the backend
        providers = backend.get_providers(config)
        providers.update(args.pop('providers', {}))
        backends = backend.get_instances(config, providers)
        backends.update(args.pop('backends', {}))

        backend.generate_ird(config, providers, backends)

        self.config = config
        self.server_info = server_info
        self.providers = providers
        self.backends = backends

    def run(self):
        server_info = self.server_info
        bottle.run(debug=True, **server_info)

    def get_instance():
        return PaltoServer.instance

    def set_instance(instance):
        PaltoServer.instance = instance

def get_backend(name):
    server = PaltoServer.get_instance()
    if name in server.backends:
        return server.backends[name]
    return None

def dispatch(name, task_template):
    backend = get_backend(name)
    if backend is not None:
        try:
            reply = task_template(backend, bottle.request, bottle.response)
            return reply
        except Exception as e:
            bottle.response.status = 500
            traceback.print_tb(e.__traceback__)
            logging.warning(e)
            return '{}'.format(e)
    bottle.response.status = 404
    return "No such service"

@bottle.get('/<name:re:.*>')
def palto_get(name):
    get = lambda backend, request, response: backend.get(request, response)
    return dispatch(name, get)

@bottle.post('/<name:re:.*>')
def palto_post(name):
    post = lambda backend, request, response: backend.post(request, response)
    return dispatch(name, post)

@bottle.put('/<name:re:.*>')
def palto_put(name):
    put = lambda backend, request, response: backend.put(request, response)
    return dispatch(name, put)

@bottle.delete('/<name:re:.*>')
def palto_delete(name):
    delete = lambda backend, request, response: backend.delete(request, response)
    return dispatch(name, delete)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Python ALTO server')
    parser.add_argument('-c', '--config', default='palto.conf',
                    help='Configuration file for palto.py, default to "palto.conf"')

    args = parser.parse_args(sys.argv[1:])

    server = PaltoServer(config = args.config)
    PaltoServer.set_instance(server)

    server.run()
