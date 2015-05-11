#!/usr/bin/env python3


class SimpleIRD():
    """
    """

    def __init__(self, get_meta = None, **kargs):
        self.get_meta = get_meta
        for name, method in kargs.items():
            setattr(self, name, method)

    def get_capabilities(self):
        return self.get_meta().get('capabilities', {})

    def get_uses(self):
        return self.get_meta().get('uses', [])

    def get_resource_id(self):
        return self.get_meta().get('resource-id')

    def get_service(self):
        return self.get_meta().get('output')
