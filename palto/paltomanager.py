#!/usr/bin/env python3

import base64
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

def load_backend_config(callback):
    def wrapper(*args, **kargs):
        try:
            config_str = bottle.request.body.getvalue().decode()
            config = configparser.ConfigParser()
            config.read_string(config_str)

            kargs['config'] = config
            return callback(*args, **kargs)
        except Exception as e:
            return errors.server_error(bottle.response, exception = e)

    return wrapper

class SimpleAuthenticationPlugin():
    """
    """

    name = 'simple_auth'
    api = 2

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def setup(self, app):
        for other in app.plugins:
            if not isinstance(other, SimpleAuthenticationPlugin):
                continue
            raise PluginError('Found another SimpleAuthenticationPlugin')

    def apply(self, callback, context):
        def wrapper(*args, **kwargs):
            try:
                auth_hdr = bottle.request.get_header('authorization', '').split(' ')
                method, key = auth_hdr[0], ' '.join(auth_hdr[1:])
                if method.lower() != 'basic':
                    return errors.unauthorized(bottle.response, 'Basic')
                username, password = base64.b64decode(key).decode().split(':')
                if username != self.username or password != self.password:
                    return errors.unauthorized(bottle.response, 'Basic')
                return callback(*args, **kwargs)
            except Exception as e:
                return errors.server_error(bottle.response, exception=e)

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
        self.setup_routes(**kargs)

    def setup_routes(self, **kargs):
        plugin = lambda callback: load_backend_config(callback)
        add_backend = lambda name, config=None: self.add_backend_route(name, config)
        remove_backend = lambda name, config=None: self.remove_backend_route(name)

        callbacks = {'add-backend' : add_backend, 'remove-backend' : remove_backend}
        for prefix, callback in callbacks.items():
            path = '/admin/{}/{}'.format(prefix, paltoserver.BACKEND_NAME_PATTERN)
            r = bottle.Route(self, path, 'POST', callback, plugins=[plugin])
            self.add_route(r)

        auth_plugin = kargs.pop('auth', None)
        if auth_plugin is not None:
            self.install(auth_plugin)

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

    auth_plugin = SimpleAuthenticationPlugin('test', 'test')
    pserver = PaltoServer()
    pmanager = PaltoManager(pserver, auth=auth_plugin, catchall=False)

    pmanager.mount('/alto/', pserver)
    pmanager.run(host='localhost', port=3400, debug=True)
