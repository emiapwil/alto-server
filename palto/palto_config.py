#!/usr/bin/env python3

import configparser
import logging

def has_missing_options(config, section, options, ignore = False):
    NO_SECTION_FOUND = 'No *%s* section is found in the configuration'
    NO_OPTION_FOUND = 'No *%s* option found in *%s* section'

    missing = False

    if not config.has_section(section):
        logging.warning(NO_SECTION_FOUND, section)
        missing = True

    for option in options:
        if not config.has_option(section, option):
            logging.warning(NO_OPTION_FOUND, option, section)
            missing = True

    return missing

def parse(file_path):
    logging.debug('config: {}'.format(file_path))
    config = configparser.ConfigParser()
    config.read_file(open(file_path))
    return config

def genereate_ird_config(mountpoint, provider = 'palto.simpleird'):
    config = configparser.ConfigParser()
    config['basic'] = { 'resource-id' : mountpoint , 'type' : 'directory', 'provider': provider }
    config['ird'] = { 'mountpoints' : '' }
    return config

def get_server_info(config):
    try:
        frontend = config['frontend']
        return { "host" : frontend['host'], "port" : frontend['port'] }
    except Error:
        return None
