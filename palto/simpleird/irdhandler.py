#!/usr/bin/env python3

from .. import frontend
from ..ird import BasicIRDHandler
from ..rfc7285.mimetypes import get_alto_mimetype
import logging

class ResourceID2URIHandler(BasicIRDHandler):
    """
    """

    def __init__(self, environ):
        self.base_uri = frontend.get_base_url(environ)

    def on_generate(self, rid, resource, out, meta):
        if (out is None) or ('uri' in out) or ('resource-id' not in out):
            return

        out['uri'] = self.base_uri() + out['resource-id']
        del out['resource-id']

class Type2MediaTypeHandler(BasicIRDHandler):
    """
    """

    def on_generate(self, rid, resource, out, meta):
        if (out is None):
            return
        self.convert_mediatype(out)
        self.convert_accepts(out)

    def convert_mediatype(self, out):
        if ('media-type' in out) or ('output' not in out):
            return

        out['media-type'] = get_alto_mimetype(out['output'])
        del out['output']

    def convert_accepts(self, out):
        if ('accepts' in out) or ('input' not in out):
            return

        out['accepts'] = get_alto_mimetype(out['input'])
        del out['input']

class CostType2CostTypeNameHandler(BasicIRDHandler):
    """
    """

    def __init__(self):
        self.count = {}

    def generate_costtype_name(mode, metric):
        if (mode is None) or (metric is None):
            return None
        return '{}-{}'.format(mode, metric)

    def matches(rid, resource):
        if 'costmap' != resource.get_service():
            return False
        if not 'cost-types' in resource.get_capabilities():
            logging.warning('Resource %s declares costmap but supports no cost-types', rid)
            return False
        return True

    def get_name_from_dict(rid, cost_type):
        if ('cost-mode' not in cost_type) or ('cost-metric' not in cost_type):
            logging.warning('Resource %s has invalid cost_type %s', rid, cost_type)
            return None
        mode, metric = cost_type['cost-mode'], cost_type['cost-metric']
        name = CostType2CostTypeNameHandler.generate_costtype_name(mode, metric)
        if name is None:
            logging.error('Invalid cost_type: <mode: %s, metric: %s>', mode, metric)
        return name

    def on_register(self, rid, resource, meta):
        if not CostType2CostTypeNameHandler.matches(rid, resource):
            return

        capabilities = resource.get_capabilities()
        for cost_type in capabilities['cost-types']:
            name = CostType2CostTypeNameHandler.get_name_from_dict(rid, cost_type)
            if name is None:
                continue

            if not 'cost-types' in meta:
                meta['cost-types'] = {}

            if not name in meta['cost-types']:
                meta['cost-types'][name] = {}
                self.count[name] = 0

            meta['cost-types'][name].update(cost_type)
            self.count[name] = self.count[name] + 1

    def on_unregister(self, rid, resource, meta):
        if not CostType2CostTypeNameHandler.matches(rid, resource):
            return

        capabilities = resource.get_capabilities()
        for cost_type in capabilities['cost-types']:
            if not 'cost-types' in meta:
                break

            name = CostType2CostTypeNameHandler.get_name_from_dict(rid, cost_type)
            if name is None:
                continue
            if not name in meta['cost-types']:
                continue
            if not name in self.count:
                continue
            self.count[name] = self.count[name] - 1
            if self.count[name] == 0:
                del self.count[name]
                del meta['cost-types'][name]

    def on_generate(self, rid, resource, output, meta):
        if not CostType2CostTypeNameHandler.matches(rid, resource):
            return

        if not 'capabilities' in output:
            return
        if not 'cost-types' in output['capabilities']:
            return
        if 'cost-type-names' in output['capabilities']:
            return
        cost_type_names = {}
        for cost_type in output['capabilities']['cost-types']:
            name = CostType2CostTypeNameHandler.get_name_from_dict(rid, cost_type)
            if name is None:
                continue
            cost_type_names.update({name : cost_type})
        output['capabilities']['cost-type-names'] = [x for x in cost_type_names]
        del output['capabilities']['cost-types']

if __name__ == '__main__':
    test_meta = {}
    cost_types = [
        { 'cost-mode' : 'numerical', 'cost-metric' : 'hopcount' },
        { 'cost-mode' : 'ordinal', 'cost-metric' : 'routingcost' },
        { 'cost-mode' : 'numerical', 'cost-metric' : 'hopcroft' }
    ]
    test_output = {
        'resource-id' : 'test',
        'input' : 'costmapfilter',
        'output' : 'costmap',
        'capabilities' : {
            'cost-types' : cost_types
        },
        'uses' : [ 'default_network_map' ]
    }

    from ..ird import BasicIRDResource, BasicIRD
    import json

    ird = BasicIRD()
    test_resource = BasicIRDResource('test', 'costmap', capabilities = { 'cost-types' : cost_types }, default = True, input = 'costmapfilter')

    print(json.dumps(test_resource.get_meta()))

    rid2uri = ResourceID2URIHandler('http://localhost:8080/')
    t2m = Type2MediaTypeHandler()
    t2n = CostType2CostTypeNameHandler()
    handlers = {
        'rid2uri' : rid2uri,
        't2m' : t2m,
        't2n': t2n
    }
    events = {
        'rid2uri' : ['on_generate'],
        't2m' : ['on_generate'],
        't2n' : ['on_register', 'on_unregister', 'on_generate']
    }

    for name, handler in handlers.items():
        ird.enable_handler(name, events[name], handler)

    ird.register('test', test_resource)

    output = ird.generate('test')

    print(json.dumps(ird.meta))
    print(json.dumps(output))
