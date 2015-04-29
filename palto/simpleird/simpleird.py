#!/usr/bin/env python3

from ..basic import AbstractIRDBackend

class SimpleIRD():
    """
    """

    def __init__(self, config, args = {}):
        self.config = config
        self.resources = args['resources'] if 'resources' in args else {}
        self.meta = args['meta'] if 'meta' in args else {}

    def set_resource(self, rid, resource):
        self.resources[rid] = resource

    def set_meta(self, field, value):
        self.meta[field] = value

    def get_meta(self, field):
        return self.meta[field] if field in self.meta else None

    def get_resource(self, rid):
        return self.resources[rid] if rid in self.resources else None

class SimpleIRDBackend(AbstractIRDBackend):
    """
    """

    def __init__(self, ird):
        AbstractIRDBackend.__init__(self, ird.config)
        self.ird = ird

    def _get(self, request, response):
        data = { 'meta' : self.ird.meta, 'resources' : self.ird.resources }
        return json.dumps(data)

    def get(self, request, response):
        actual_get = lambda req, rep: self._get(req, rep)
        return AbstractIRDBackend.get(self, request, response, actual_get)
