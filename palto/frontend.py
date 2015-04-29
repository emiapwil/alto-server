#!/usr/bin/env python3

from . import palto_config

def get_server_info(config):
    if palto_config.has_missing_options(config, 'frontend', ['host', 'port']):
        return None

    frontend = config['frontend']
    return { "host" : frontend['host'], "port" : frontend['port'] }

def get_base_url(config):
    server_info = get_server_info(config)

    return 'http://{}:{}/'.format(server_info['host'], server_info['port'])
