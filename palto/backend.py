#!/usr/bin/env python3

from . import palto_config
from .ird import BasicIRD
import glob
import sys
import logging
import importlib

def load_providers(provider_list):
    providers = {}
    for provider in provider_list:
        try:
            m = importlib.import_module(provider)
            if not hasattr(m, 'create_instance'):
                logging.error('provider %s doesn\' have a *create_instance* method', provider)
                continue
            providers[provider] = m
        except ImportError:
            logging.error("Failed to load module %s", provider)
            continue
        logging.debug(providers)

    return providers

def get_providers(config):
    if palto_config.has_missing_options(config, 'backend', ['providers']):
        return None

    provider_list = [x.strip() for x in config['backend']['providers'].split(',')]
    logging.debug(provider_list)
    providers = load_providers(provider_list)
    return providers

def get_instances(global_config, providers):
    if palto_config.has_missing_options(global_config, 'backend', ['resources']):
        return None

    resources = global_config['backend']['resources']
    resources = [x.strip() for x in resources.split(',')]
    logging.debug(resources)

    files = set()
    for resource in resources:
        files = files | { x for x in glob.glob(resource) }

    instances = {}
    for f in files:
        try:
            config = palto_config.parse(f)
            required = ['resource-id', 'provider']
            if palto_config.has_missing_options(config, 'basic', required):
                continue
            rid = config['basic']['resource-id']

            if rid in instances:
                logging.warn('Instance with the same resource-id %s exists', rid)
                continue

            clazz = config['basic']['provider']
            if not clazz in providers:
                logging.warn("Provider *%s* not found.", clazz)
                continue
            provider = providers[clazz]

            _create_instance = getattr(provider, 'create_instance')
            instance = _create_instance(rid, config, global_config)
            if instance is not None:
                instances[rid] = instance
        except Exception as e:
            logging.warn('Failed to parse backend instance: %s : %s', f, e)

    return instances

def is_ird_resource(instance):
    if instance is None:
        return False
    if not instance.config.has_section('ird'):
        return False
    if not hasattr(instance, 'get_meta'):
        return False
    return True

def get_irdbackend(provider, mountpoint, global_config):
    _create_instance = getattr(provider, 'create_instance')
    config = palto_config.genereate_ird_config(mountpoint)
    instance = _create_instance(mountpoint, config, global_config)
    for attr in BasicIRD.BASIC_ATTR:
        if hasattr(instance, attr):
            continue
        logging.error('Failed to create ird for mountpoint %s', mountpoint)
        logging.error('IRD instance doesn\'t have %s method', attr)
        return None
    return instance

def generate_ird(global_config, providers, instances):
    name = global_config.get('ird', 'provider', fallback='palto.simpleird')
    providers.update({} if name in providers else load_providers([name]))
    provider = providers.get(name)
    if provider is None:
        logging.error('Failed to load ird provider class %s', name)
        return

    root = get_irdbackend(provider, '', global_config)
    if root is None:
        return
    irds = { '' : root }
    for rid, instance in instances.items():
        if not is_ird_resource(instance):
            continue
        config = instance.config
        mountpoints = config.get('ird', 'mountpoints', fallback='')
        mountpoints = { x.strip() for x in mountpoints.split(',') }

        for mountpoint in mountpoints:
            if mountpoint in instances:
                logging.warn('Mountpoint %s is designated already', mountpoint)
                continue
            if not mountpoint in irds:
                ird = get_irdbackend(provider, mountpoint, global_config)
                if ird is not None:
                    root.register(mountpoint, ird)
                    irds[mountpoint] = ird

            ird = irds[mountpoint]
            ird.register(rid, instance)

    instances.update(irds)

class Backend():
    """
    """

    def __init__(self, config):
        self.config = config

    def get(self, request, response):
        raise NotImplementedError()

    def post(self, request, response):
        raise NotImplementedError()

    def put(self, request, response):
        raise NotImplementedError()

    def delete(self, request, response):
        raise NotImplementedError()
