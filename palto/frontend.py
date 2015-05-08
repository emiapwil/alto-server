#!/usr/bin/env python3

from . import palto_config

_server_info = ['host', 'port', 'server']

def get_server_info(config):
    if palto_config.has_missing_options(config, 'frontend', ['host', 'port']):
        return None

    frontend = config['frontend']
    info = { key: frontend[key] for key in ['host', 'port'] }
    info['server'] = config.get('frontend', 'server', fallback='wsgiref')
    return info

def get_base_url(config):
    server_info = get_server_info(config)

    return 'http://{}:{}/'.format(server_info['host'], server_info['port'])

def get_url(config, name):
    return '{}{}'.format(get_base_url(config), name)
