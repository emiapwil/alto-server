import configparser

def print_message(message, ignore = False):
    if ignore:
        return
    print(message)

def has_missing_options(config, section, options, ignore = False):
    NO_SECTION_FOUND = 'No *{}* section is found in the configuration'
    NO_OPTION_FOUND = 'No *{}* option found in *{}* section'

    missing = False

    if not config.has_section(section):
        print_message(NO_SECTION_FOUND.format(section), ignore)
        missing = True

    for option in options:
        if not config.has_option(section, option):
            print_message(NO_OPTION_FOUND.format(option, section), ignore)
            missing = True

    return missing

def parse(file_path):
    print('config: {}'.format(file_path))
    config = configparser.ConfigParser()
    config.read_file(open(file_path))
    return config

def get_server_info(config):
    try:
        frontend = config['frontend']
        return { "host" : frontend['host'], "port" : frontend['port'] }
    except Error:
        return None
