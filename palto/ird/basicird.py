#!/usr/bin/env python3

import logging
import copy

class BasicIRD():
    """
    """
    BASIC_ATTR = ['register', 'unregister', 'generate_dir', 'generate', 'update']
    ON_REGISTER = 'on_register'
    ON_UNREGISTER = 'on_unregister'
    ON_UPDATE = 'on_update'
    ON_GENERATE = 'on_generate'

    def __init__(self):
        self.meta = {}
        self.resources = {}
        self.handle = {}
        self.handle[BasicIRD.ON_REGISTER] = set()
        self.handle[BasicIRD.ON_UNREGISTER] = set()
        self.handle[BasicIRD.ON_GENERATE] = set()
        self.handlers = {}

    def execute_handler(self, name, handler_task):
        try:
            handle = self.handlers[name]['instance']
            handler_task(handle)
        except Exception as e:
            logging.error('Error while executing handler %s: %s', name, e)

    def register(self, rid, resource):
        if rid in self.resources:
            return False

        if not BasicIRDResource.is_ird_resource(resource):
            return False

        self.resources[rid] = resource
        for name in self.handle[BasicIRD.ON_REGISTER]:
            task = lambda h: h.on_register(rid, resource, self.meta)
            self.execute_handler(name, task)
        return True

    def unregister(self, rid):
        resource = self.resources.get(rid, None)
        if resource is None:
            return

        del self.resources[rid]
        for name in self.handle[BasicIRD.ON_UNREGISTER]:
            task = lambda h: h.on_unregister(rid, resource, self.meta)
            self.execute_handler(name, task)

    def update(self, rid, new_resource):
        self.unregister(rid)
        self.register(rid, new_resource)

    def generate_dir(self):
        ird = {}
        ird['meta'] = self.meta
        ird['resources'] = {}
        for rid, resource in self.resources.items():
            output = self.generate(rid, resource, ird['meta'])
            if output is not None:
                ird['resources'][rid] = output

        return ird

    def generate(self, rid, resource = None, meta = {}):
        if resource is None:
            resource = self.resources.get(rid, None)
        if resource is None:
            return None

        output = resource.get_meta()
        for name in self.handle[BasicIRD.ON_GENERATE]:
            task = lambda h: h.on_generate(rid, resource, output, meta)
            self.execute_handler(name, task)
        return output

    def enable_handler(self, name, events, instance):
        if (name is None) or (events is None) or (instance is None):
            return False
        if name in self.handlers:
            return False

        for event in events:
            if not hasattr(instance, event):
                logging.warn('Handler %s doesn\' support %s', name, event)
                continue
            self.handle[event] |= { name }

        self.handlers[name] = { 'events' : events, 'instance' : instance }

    def disable_handler(self, name):
        if name is None or name not in self.handlers:
            return

        handler = self.handlers[name]
        for event in handler['events']:
            self.handle[event] -= { name }

        del self.handlers[name]

class BasicIRDResource():
    """
    """

    BASIC_ATTR = ['get_meta']

    def is_ird_resource(instance):
        for attr in BasicIRDResource.BASIC_ATTR:
            if not hasattr(instance, attr):
                return False
        return True

    def __init__(self, resource_id, service, **args):
        self.rid = resource_id
        self.service = service
        self.accept = args.pop('accepts', None)

        self.capabilities = args.pop('capabilities', {})
        self.uses = args.pop('uses', set())
        self.args = args

    def get_meta(self):
        output = copy.deepcopy(self.args)
        output['resource-id'] = self.rid
        output['output'] = self.service
        if self.accept is not None:
            output['input'] = self.accept
        if len(self.capabilities) > 0:
            output['capabilities'] = self.get_capabilities()
        if len(self.uses) > 0:
            output['uses'] = list(self.uses)
        return output

    def get_capabilities(self):
        return copy.deepcopy(self.capabilities)

    def add_capabilities(self, capabilities = {}):
        self.capabilities.update(capabilities)

    def uses(self, new_uses):
        self.uses.update(new_uses)

    def get_uses(self):
        return copy.deepcopy(self.uses)

    def get_resource_id(self):
        return self.rid

    def get_service(self):
        return self.service

class BasicIRDHandler():
    """
    """

    def on_register(self, rid, resource, meta):
        pass

    def on_unregister(self, rid, resource, meta):
        pass

    def on_generate(self, rid, resource, output, meta):
        pass

    def on_update(self, rid, resource, meta):
        self.on_unregister(rid, resource, meta)
        self.on_register(rid, resource, meta)
