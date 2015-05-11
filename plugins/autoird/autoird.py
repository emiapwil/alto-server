#!/usr/bin/env python3

import bottle
import logging

import palto.utils
import palto.paltomanager
import palto.palto_config
from .basicird import SimpleIRD

def can_autogenerate(backend):
    try:
        config = backend.config
        if not config.has_section('ird'):
            return False
        return True
    except Exception as e:
        logging.warning('Error reading config from backend %s', backend)
        return False

def get_mountpoints(backend):
    mountpoints = backend.config.get('ird', 'mountpoints', fallback='')
    mountpoints = { x.strip() for x in mountpoints.split(',') }
    return mountpoints

def generate_ird_resource(backend):
    if not hasattr(backend, 'get_meta'):
        logging.error('AutoIRDPlugin requires get_meta to generate ird')
        return None
    args = {}
    for func in ['get_meta', 'get_capabilities', 'get_uses']:
        if hasattr(backend, func):
            args[func] = getattr(backend, func)
    return SimpleIRD(**args)

def get_ird_provider(config):
    return config.get('autoird', 'provider', fallback='palto.simpleird')

class AutoIRDPlugin():
    """
    """

    name = 'auto_ird'
    api = 2

    def __init__(self):
        self.backends = {}

    def matches(self, context):
        if not hasattr(context, 'name'):
            return False
        return context.name in ['add-backend','remove-backend']

    def get_ird_backend(self, mountpoint, **kargs):
        if mountpoint in self.backends:
            return self.backends[mountpoint]
        try:
            if self.server.get_backend(mountpoint) is not None:
                logging.warning('Mountpoint %s already registered', mountpoint)
                return None

            provider = kargs.pop('provider', get_ird_provider(self.manager.config))
            config = palto.palto_config.genereate_ird_config(mountpoint, provider)
            self.manager.add_backend_route(mountpoint, config)

            instance = self.server.get_backend(mountpoint)
            self.backends[mountpoint] = instance
            self.generate_ird(mountpoint, instance)
            return instance
        except Exception as e:
            logging.warning('Failed to create IRD backend %s: %s', mountpoint, e)
            return None

    def generate_ird(self, name, backend):
        if not can_autogenerate(backend):
            return
        try:
            mountpoints = get_mountpoints(backend)
            resource = generate_ird_resource(backend)
        except Exception as e:
            logging.warning('Failed to generate IRD resource for %s: %s', name, e)
            return

        for mp in mountpoints:
            try:
                if mp == name:
                    continue
                instance = self.get_ird_backend(mp)
                if instance is None:
                    logging.warning('Failed to get IRD backend %s, skipping', mp)
                if instance.register(name, resource):
                    logging.info('Register %s to mountpoint %s', name, mp)
            except Exception as e:
                logging.warning('Failed to register %s to mountpoint %s: %s', name, mp, e)

    def remove_ird(self, name, backend):
        if not can_autogenerate(backend):
            return

        mountpoints = get_mountpoints(backend)

        for mp in mountpoints:
            try:
                instance = self.get_ird_backend(mp)
                if instance is None:
                    continue
                instance.unregister(name)
            except Exception as e:
                logging.warning('Error while unregistering %s from %s', name, mp)

    def setup(self, app):
        if not palto.utils.no_plugin_instance(app.plugins, AutoIRDPlugin):
            raise bottle.PluginError('AutoIRDPlugin already installed')

        if app.server is None:
            raise bottle.PluginError('PaltoServer must not be None')

        self.manager, self.server = app, app.server
        backends = dict.copy(app.server.get_backends())
        for name, backend in backends.items():
            self.generate_ird(name, backend)

    def apply(self, callback, context):
        if not self.matches(context):
            return callback

        def wrapper(*args, **kwargs):
            out = callback(*args, **kwargs)
            try:
                name = kwargs.get('name')
                backend = self.server.get_backend(name)

                if context.name == 'add-backend':
                    self.generate_ird(name, backend)
                elif context.name == 'remove-backend':
                    self.remove_ird(name, backend)
            except Exception as e:
                logging.error('Error while handling %s route: %s', context.name, e)
            return out

        return wrapper

    def close(self):
        for name in self.backends:
            self.manager.remove_backend_route(name)
        self.backends = {}

def create_instance(name, config, environ):
    return AutoIRDPlugin()
