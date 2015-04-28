#!/usr/bin/env python3

import logging

class BasicIRD():

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

    def register(self, rid, resource):
        if rid in self.resources:
            return False

        self.resources[rid] = resource
        for name in self.handle[BasicIRD.ON_REGISTER]:
            handle = self.handlers[name]['instance']
            handle.on_register(rid, resource, self.meta)
        return True

    def unregister(self, rid):
        if not rid in self.resources:
            return True

        for name in self.handle[BasicIRD.ON_UNREGISTER]:
            handle = self.handlers[name]['instance']
            handle.on_unregister(rid, self.resources[rid], self.meta)
        del self.resources[rid]

    def generate(self, rid):
        if not rid in self.resources:
            return []

        output = self.resources[rid].get_meta()
        for name in self.handle[BasicIRD.ON_GENERATE]:
            handle = self.handlers[name]['instance']
            handle.on_generate(rid, self.resources[rid], output, self.meta)
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

    def __init__(self, resource_id, service, **args):
        self.rid = resource_id
        self.service = service
        self.capabilities = args['capabilities'] if 'capabilities' in args else {}
        self.uses = args['uses'] if 'uses' in args else set()

    def get_meta(self):
        output = {}
        output['resource-id'] = self.rid
        output['output'] = self.service
        output['capabilities'] = self.capabilities
        output['uses'] = [ x for x in self.uses ]

    def add_capabilities(self, capabilities = {}):
        self.capabilities.update(capabilities)

    def uses(self, new_uses):
        self.uses.update(new_uses)
        
class BasicIRDHandler():

    def on_register(self, rid, resource, meta):
        pass

    def on_unregister(self, rid, resource, meta):
        pass

    def on_generate(self, rid, resource, output, meta):
        pass

    def on_update(self, rid, resource, meta):
        self.on_unregister(rid, resource, meta)
        self.on_register(rid, resource, meta)
