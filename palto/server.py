import argparse
import bottle
import json
import sys
from . import palto_config, frontend, backend

@bottle.route('/test')
def test():
    bottle.response.set_header('Content-type', 'applicatoin/test+json')
    return json.dumps({ 'a' : 1, 'b' : 2})

class PaltoServer():

    def __init__(self, config_file):
        config = palto_config.parse(config_file)

        # check the setting for the frontend
        server_info = frontend.get_server_info(config)
        if (server_info is None):
            raise Exception("Missing fields in config file")

        # check the settings for the backend
        providers = backend.get_providers(config)
        backends = backend.get_instances(config, providers)

        self.config = config
        self.server_info = server_info
        self.providers = providers
        self.backends = backends
        pass

    def run(self):
        server_info = self.server_info
        bottle.run(host=server_info['host'], port=server_info['port'], debug=True)

def get_backend(name):
    if name in server.backends:
        return server.backends[name]
    return None

@bottle.get('/<name:re:.+>')
def dispatch(name):
    backend = get_backend(name)
    if backend is not None:
        try:
            reply = backend.get(bottle.request, bottle.response)
            return reply
        except Exception as e:
            return e
    bottle.response.status = 404
    return "No such service"

parser = argparse.ArgumentParser(description='Python ALTO server')
parser.add_argument('-c', '--config', default='palto.conf',
                help='Configuration file for palto.py, default to "palto.conf"')

args = parser.parse_args(sys.argv[1:])

server = PaltoServer(args.config)

server.run()
