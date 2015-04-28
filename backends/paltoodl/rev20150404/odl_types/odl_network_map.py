#!/usr/bin/env python3
from .odl_abstract_map import AbstractODLMap

class ODLNetworkMap( AbstractODLMap ):
    def load_odl_map(self, odl_network_map):
        self.content = odl_network_map
        return self

    def load_rfc_map(self, rfc_network_map):
        self.content = {
            'resource-id': rfc_network_map['meta']['vtag']['resource-id'],
            'tag': rfc_network_map['meta']['vtag']['tag'],
            'map': self.to_odl_maps(rfc_network_map['network-map'])
        }
        return self

    def odl_map(self):
        return self.content

    def resource_id(self):
        return self.content['resource-id']

    def rfc_map(self):
        return {
            'meta': {
                'vtag': {
                    'resource-id': self.content['resource-id'],
                    'tag': self.content['tag']
                }
            },
            'network-map': self.to_rfc_maps(self.content['map'])
        }

    def to_odl_maps(self, rfc_maps):
        odl_maps = []
        for pid in rfc_maps:
            odl_map = {
                'pid': pid,
                'endpoint-address-group': []
            }
            for addr_type in rfc_maps[pid]:
                odl_map['endpoint-address-group'].append({
                    'address-type': addr_type,
                    'endpoint-prefix': rfc_maps[pid][addr_type]
                })
            odl_maps.append(odl_map)
        return odl_maps

    def to_rfc_maps(self, odl_maps):
        rfc_maps = {}
        for odl_map in odl_maps:
            pid = odl_map['pid']
            rfc_maps[pid] = {}
            for group in odl_map['endpoint-address-group']:
                add_type = group['address-type']
                prefixes = group['endpoint-prefix']
                rfc_maps[pid][add_type] = prefixes
        return rfc_maps
