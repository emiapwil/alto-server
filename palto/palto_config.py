#!/usr/bin/env python3

import configparser
import logging

def has_missing_options(config, section, options, ignore = False):
    NO_SECTION_FOUND = 'No *{}* section is found in the configuration'
    NO_OPTION_FOUND = 'No *{}* option found in *{}* section'

    missing = False

    if not config.has_section(section):
        logging.warn(NO_SECTION_FOUND.format(section))
        missing = True

    for option in options:
        if not config.has_option(section, option):
            logging.warn(NO_OPTION_FOUND.format(option, section))
            missing = True

    return missing

def parse(file_path):
    logging.debug('config: {}'.format(file_path))
    config = configparser.ConfigParser()
    config.read_file(open(file_path))
    return config

def genereate_ird_config(mountpoint):
    config = configparser.ConfigParser()
    config['basic'] = { 'resource-id' : mountpoint , 'type' : 'directory' }
    config['ird'] = { 'mountpoints' : '' }
    return config

def get_server_info(config):
    try:
        frontend = config['frontend']
        return { "host" : frontend['host'], "port" : frontend['port'] }
    except Error:
        return None
