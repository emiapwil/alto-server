#!/usr/bin/env python3
from .odl_abstract_map import AbstractODLMap
import time

class ODLEndpointPropertyMap( AbstractODLMap ):
    def load_odl_map(self, odl_end_prop_map):
        self.content = odl_end_prop_map
        return self

    def load_rfc_map(self, rfc_endp_prop_map):
        self.content = {
            'meta': self.to_odl_meta(rfc_endp_prop_map['meta']),
            'endpoint-properties': self.to_odl_endp_props(rfc_endp_prop_map['endpoint-properties'])
        }
        return self

    def odl_map(self):
        return self.content

    def rfc_map(self):
        return {
            'meta': self.to_rfc_meta(self.content['meta']),
            'endpoint-properties': self.to_rfc_endp_props(self.content['endpoint-properties'])
        }

    def to_rfc_meta(self, odl_meta):
        meta = {}
        meta['dependent-vtags'] = []
        for d_vtag in odl_meta['dependent-vtags']:
            meta['dependent-vtags'].append({
                'resource-id': d_vtag['resource-id'],
                'tag': d_vtag['tag']
            })
        return meta

    def to_rfc_endp_props(self, odl_endp_props):
        endp_props = {}
        for endp_prop in odl_endp_props:
            endpoint = endp_prop['endpoint']
            properties = endp_prop['properties']
            endp_props[endpoint] = {}
            for prop in properties:
                prop_name = prop['property-type']
                prop_value = prop['property']
                endp_props[endpoint][prop_name] = prop_value
        return endp_props

    def to_odl_meta(self, rfc_meta):
        meta = {}
        odl_meta['dependent-vtags'] = []
        for d_vtag in rfc_meta['dependent-vtags']:
            odl_meta['dependent-vtags'].append({
                'resource-id': d_vtag['resource-id'],
                'tag': d_vtag['tag']
            })
        return meta

    def to_odl_endp_props(self, rfc_endp_props):
        endp_props = []
        for endpoint in rfc_endp_props:
            endp_prop = {}
            endp_prop[endpoint] = []
            for prop in rfc_endp_props['properties']:
                endp_prop[endpoint].append({
                    prop['property-type']: prop['property']
                })
        return endp_props
