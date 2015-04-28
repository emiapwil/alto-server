#!/usr/bin/env python3

from . import palto_config
import configparser
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

def get_instances(config, providers):
    if palto_config.has_missing_options(config, 'backend', ['resources']):
        return None

    resources = config['backend']['resources']
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
            instances[rid] = _create_instance(config)
        except Exception as e:
            logging.warn('Failed to parse backend instance: %s : %s', f, e)

    return instances

class Backend():

    def __init__(self):
        pass

    def get_ird_meta(self):
        return None

    def get(self, request, response):
        raise NotImplementedError()

    def post(self, request, response):
        raise NotImplementedError()

    def put(self, request, response):
        raise NotImplementedError()

    def delete(self, request, response):
        raise NotImplementedError()
