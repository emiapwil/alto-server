#!/usr/bin/env python3

from ..rfc7285.basic import AbstractIRDBackend
from ..rfc7285.irdhandler import ResourceID2URIHandler
from ..rfc7285.irdhandler import Type2MediaTypeHandler
from ..rfc7285.irdhandler import CostType2CostTypeNameHandler
from ..ird import BasicIRD, BasicIRDResource
from .. import frontend
import json

class SimpleIRDBackend(AbstractIRDBackend, BasicIRD, BasicIRDResource):
    """
    """

    def __init__(self, config, rid):
        AbstractIRDBackend.__init__(self, config)
        BasicIRD.__init__(self)
        BasicIRDResource.__init__(self, rid, 'directory')

    def _get(self, request, response):
        data = self.generate_dir()
        return json.dumps(data)

    def get(self, request, response):
        actual_get = lambda req, rep: self._get(req, rep)
        return AbstractIRDBackend.get(self, request, response, actual_get)

def create_instance(rid, config, global_config):
    instance = SimpleIRDBackend(config, rid)

    rid2uri = ResourceID2URIHandler(frontend.get_base_url(global_config))
    type2media = Type2MediaTypeHandler()
    cost2name = CostType2CostTypeNameHandler()
    names = ['resource-id-to-uri', 'type-to-media-type', 'cost-type-to-name']
    events = [
        [BasicIRD.ON_GENERATE],
        [BasicIRD.ON_GENERATE],
        [BasicIRD.ON_REGISTER, BasicIRD.ON_UNREGISTER, BasicIRD.ON_GENERATE],
    ]
    handlers = [rid2uri, type2media, cost2name]
    for i in range(len(names)):
        instance.enable_handler(names[i], events[i], handlers[i])

    return instance

if __name__ == '__main__':
    try:
        create_instance(1, 2, 3)
    except Exception as e:
        print(e)

    try:
        m = __import__('palto.simpleird.simpleird')
        print(m.__dict__)
        m.create_instance(1,2,3)
    except Exception as e:
        print(e)
