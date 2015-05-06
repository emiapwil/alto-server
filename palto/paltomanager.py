#!/usr/bin/env python3

import bottle
import configparser
import json
import importlib
import logging
from . import errors, paltoserver

PROVIDER_FUNC = ['create_instance']

def load_provider(provider_module):
    module = importlib.import_module(provider_module)
    for func in PROVIDER_FUNC:
        if hasattr(module, func):
            continue
        raise Exception('Provider module %s must have method %s()', provider_module, func)
    return module

def create_instance(provider, *args):
    _create_instance = getattr(provider, 'create_instance')
    try:
        return _create_instance(*args)
    except Exception as e:
        raise Exception('Error while creating instance: %s', e)

def load_config_from_request(callback):
    def wrapper(name):
        try:
            config_str = bottle.request.body.getvalue().decode()
            config = configparser.ConfigParser()
            config.read_string(config_str)

            callback(name, config)
        except Exception as e:
            return errors.server_error(bottle.response, exception = e)

    return wrapper


class PaltoManager(bottle.Bottle):
    """
    """

    def __init__(self, server, **kargs):
        args = { x: kargs.pop(x, True) for x in ['catchall', 'autojson'] }
        bottle.Bottle.__init__(self, **args)

        self.server = server
        self.providers = {}
        self.config = kargs.pop('config', configparser.ConfigParser())
        self.setup_routes()

    def setup_routes(self):
        plugin = lambda callback: load_config_from_request(callback)
        add_backend = lambda name, config: self.add_backend_route(name, config)
        remove_backend = lambda name, config: self.remove_backend_route(name)

        callbacks = {'add-backend' : add_backend, 'remove-backend' : remove_backend}
        for prefix, callback in callbacks.items():
            path = '/{}/{}'.format(prefix, paltoserver.BACKEND_NAME_PATTERN)
            r = bottle.Route(self, path, 'POST', callback, plugins=[plugin])
            self.add_route(r)

    def install_route(self, plugin_name, **kargs):
        pass

    def uninstall_route(self, plugin_name):
        pass

    def add_backend_route(self, name, config):
        if self.server.get_backend(name) is not None:
            raise Exception('Backend %s already exists')
        provider = config.get('basic', 'provider')
        if provider is None:
            raise Exception('Must specify the provider')

        if not provider in self.providers:
            module = load_provider(provider)
            self.providers[provider] = module

        _provider = self.providers[provider]
        instance = create_instance(_provider, name, config, self.config)

        self.server.add_backend(name, instance)

    def remove_backend_route(self, name):
        self.server.remove_backend(name)

if __name__ == '__main__':
    from .paltoserver import PaltoServer

    pserver = PaltoServer()
    pmanager = PaltoManager(pserver, catchall=False)

    pmanager.mount('/alto/', pserver)
    pmanager.run(host='localhost', port=3400, debug=True)
