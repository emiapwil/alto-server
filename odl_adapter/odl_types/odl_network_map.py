#!/usr/bin/env python3
import json
import time

class ODLNetworkMap:
    def load_from_str(self, json_str):
        self.content = json.load(json_str)
        return self

    def load_from_rfc(self, rfc_network_map):
        self.content = {
            'alto-service:resource-id': rfc_network_map['meta']['vtag']['resource-id'],
            'alto-service:tag': rfc_network_map['meta']['vtag']['tag'],
            'alto-service:map': self.to_odl_maps(rfc_network_map['network-map'])
        }
        return self

    def odl_network_map(self):
        return self.content

    def odl_network_map_json(self):
        return json.dumps(self.odl_network_map())

    def rfc_network_map(self):
        return {
            'meta': {
                'vtag': {
                    'resource-id': self.content['alto-service:resource-id'],
                    'tag': self.content['alto-service:tag']
                }
            },
            'network-map': self.to_rfc_maps(self.content['alto-service:map'])
        }

    def rfc_network_map_json(self):
        return json.dumps(self.rfc_network_map())

    def to_odl_maps(self, rfc_maps):
        odl_maps = []
        for pid in rfc_maps:
            odl_map = {
                'alto-service:pid': pid,
                'alto-service:endpoint-address-group': []
            }
            for addr_type in rfc_maps[pid]:
                odl_map['alto-service:endpoint-address-group'].append({
                    'alto-service:address-type': addr_type,
                    'alto-service:endpoint-prefix': rfc_maps[pid][addr_type]
                })
            odl_maps.append(odl_map)
        return odl_maps

    def to_rfc_maps(self, odl_maps):
        rfc_maps = {}
        for odl_map in odl_maps:
            pid = odl_map['alto-service:pid']
            rfc_maps[pid] = {}
            for group in odl_map['alto-service:endpoint-address-group']:
                add_type = group['alto-service:address-type']
                prefixes = group['alto-service:endpoint-prefix']
                rfc_maps[pid][add_type] = prefixes
        return rfc_maps
