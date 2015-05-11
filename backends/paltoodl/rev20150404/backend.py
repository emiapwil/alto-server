#!/usr/bin/env python3

from .odl_adapter import ODLAdapter
from palto.rfc7285 import AbstractNetworkMapBackend
from palto.ird import BasicIRDResource
from palto import palto_config
from palto import errors

import logging

ODL_INFO = ['revision', 'type', 'host', 'user', 'password', 'resource-id']
REVISION = '2015-04-04'

class OpenDaylightNetworkMapBackend(AbstractNetworkMapBackend, BasicIRDResource):
    """
    """

    def __init__(self, config, rid, **args):
        AbstractNetworkMapBackend.__init__(self, config)
        self.odl_args = { info : args.pop(info) for info in ODL_INFO }
        BasicIRDResource.__init__(self, rid, 'networkmap', **args)
        self.connector = ODLAdapter(self.odl_args)

    def _get(self):
        result = self.connector.get_network_map(self.odl_args['resource-id'])
        if result is None:
            raise RuntimeError('Error while reading from ODL')
        return result

    def get(self, request, response):
        actual_get = lambda req, rep: self._get()
        return AbstractNetworkMapBackend.get(self, request, response, actual_get)

    def post(self, request, response):
        return errors.not_implemented(response)

creators = {
    'networkmap' : OpenDaylightNetworkMapBackend,
}

def create_instance(resource_id, config, environ):
    if palto_config.has_missing_options(config, 'odl', ODL_INFO):
        logging.warning('Need %s to create odl backend', ODL_INFO)
        return None
    args = { info: config.get('odl', info) for info in ODL_INFO }
    args['resource-id'] = config.get('odl', 'resource-id', fallback=resource_id)

    if REVISION != args['revision']:
        logging.error('This backend only support revision %s', REVISION)
        return None

    if args['type'] not in creators:
        logging.error('Map type %s not supported yet', args['type'])

    return creators[args['type']](config, resource_id, **args)
