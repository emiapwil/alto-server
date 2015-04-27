from . import palto_config
import configparser
import glob
import sys

def load_providers(provider_list):
    providers = {}
    for provider in provider_list:
        try:
            m = __import__(provider)
            m.test()
            providers[provider] = m
        except ImportError:
            print("Failed to load module {}".format(provider))
            continue
        print(providers)

    return providers

def get_providers(config):
    if palto_config.has_missing_options(config, 'backend', ['providers']):
        return None

    provider_list = [x.strip() for x in config['backend']['providers'].split(',')]
    print(provider_list)
    providers = load_providers(provider_list)
    return providers

def get_instances(config, providers):
    if palto_config.has_missing_options(config, 'backend', ['resources']):
        return None

    resources = config['backend']['resources']
    resources = [x.strip() for x in resources.split(',')]
    print(resources)

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
                print('Instance with the same resource-id {} has exists'.format(rid))
                continue

            clazz = config['basic']['provider']
            if not clazz in providers:
                print("Provider *{}* not found.".format(clazz))
                continue
            provider = providers[clazz]

            _create_instance = getattr(provider, 'create_instance')
            instances[rid] = _create_instance(config)
        except Exception as e:
            print('Failed to parse backend instance: {} : {}'.format(f, e))

    return instances

class Backend():

    def __init__(self):
        pass

    def get(self, request, response):
        raise NotImplementedError()

    def post(self, request, response):
        raise NotImplementedError()

    def put(self, request, response):
        raise NotImplementedError()

    def delete(self, request, response):
        raise NotImplementedError()
