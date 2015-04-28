#!/usr/bin/env python3

from . import palto_config
import glob
import sys
import logging

def load_providers(provider_list):
    providers = {}
    for provider in provider_list:
        try:
            m = __import__(provider)
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
            instances[rid] = _create_instance(config, global_config)
        except Exception as e:
            logging.warn('Failed to parse backend instance: %s : %s', f, e)

    return instances

def is_ird_resource(instance):
    if instance is None:
        return False
    if not instance.config.has_section('ird'):
        return False
    if not hasattr(instance, 'register'):
        return False
    return True

def generate_ird(instances):
    root_ird = SimpleIRDBackend(palto_config.genereate_ird_config(''))
    irds = {}
    for instance in instances:
        if not is_ird_resource(instance):
            continue
        config = instance.config
        mountpoints = config.get('ird', 'mountpoints', fallback='')
        mountpoints = { x.strip() for x in mountpoints.split(',') }

        for mountpoint in mountpoints:
            if not mountpoint in irds:
                ird_config = palto_config.genereate_ird_config(mountpoint)
                irds[mountpoint] = SimpleIRDBackend(ird_config)
                ird.register(root_ird)
            
            ird = irds[mountpoint]
            instance.register(ird)

class Backend():
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
