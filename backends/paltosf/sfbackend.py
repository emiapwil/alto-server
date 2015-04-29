#!/usr/bin/env python3

from palto import Backend
from palto.ird import BasicIRDResource
from palto.rfc7285 import AbstractNetworkMapBackend
from palto import palto_config

import logging
import json

class StaticFileNetworkMapBackend(AbstractNetworkMapBackend, BasicIRDResource):
    """
    """

    def __init__(self, config, global_config, rid, **args):
        meta, data = args.pop('meta'), args.pop('data')
        AbstractNetworkMapBackend.__init__(self, config)
        BasicIRDResource.__init__(self, rid, **meta)
        self._data = data

    def get(self, request, response, actual_get = None):
        actual_get = lambda req, rep: self._data
        return AbstractNetworkMapBackend.get(self, request, response, actual_get)

creators = {
    'networkmap' : StaticFileNetworkMapBackend,
}

def create_instance(rid, config, global_config):
    if palto_config.has_missing_options(config, 'static_file', ['path']):
        logging.warning('Resource %s has no path option in *static_file* section', rid)
        return None

    with open(config['static_file']['path']) as data:
        content = json.load(data)

    meta, data = content.get('meta'), content.get('data')
    if (meta is None) or (data is None):
        logging.warning('Static file must have fields *meta* and *data*')
        return None
    service = meta.get('service', '')
    creator = creators.get(service)
    if creator is None:
        logging.warning('Resource type %s is not supported yet', service)
        return None

    return creator(config, global_config, rid, meta = meta, data = data)

class TestObject():
    def __init__(self):
        pass

if __name__ == '__main__':
    global_file = 'examples/palto.conf'
    config_file = 'examples/resources/test_staticfile.conf'
    global_config = palto_config.parse(global_file)
    config = palto_config.parse(config_file)

    instance = create_instance('test_sf', config, global_config)
    request = TestObject()
    request.get_header = lambda x: 'application/alto-networkmap+json'

    response = TestObject()
    response.content_type = ""
    response.status = 0
    response.set_header = lambda x, y: print('set {} = {}'.format(x, y))

    print(instance)
    print(json.dumps(instance.get_meta()))
    print(json.dumps(instance.get(request, response)))
