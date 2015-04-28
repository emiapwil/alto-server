#!/usr/bin/env python3
from .odl_abstract_map import AbstractODLMap
import time

class ODLCostMap( AbstractODLMap ):
    def load_odl_map(self, odl_cost_map):
        self.content = odl_cost_map
        return self

    def load_rfc_map(self, rfc_cost_map):
        self.content = {
            'resource-id': self.generate_resource_id(rfc_cost_map['meta']),
            'tag': self.tag(),
            'meta': self.to_odl_meta(rfc_cost_map['meta']),
            'map': self.to_odl_maps(rfc_cost_map['cost-map'])
        }
        return self

    def odl_map(self):
        return self.content

    def rfc_map(self):
        return {
            'meta': self.to_rfc_meta(self.content['meta']),
            'cost-map': self.to_rfc_maps(self.content['map'])
        }

    def generate_resource_id(self, rfc_meta):
        resource_id = rfc_meta['dependent-vtags'][0]['resource-id']
        cost_mode = rfc_meta['cost-type']['cost-mode']
        cost_metric = rfc_meta['cost-type']['cost-metric']
        return resource_id + '-' + cost_mode + '-' + cost_metric

    def resource_id(self):
        return self.content['resource-id']

    #TODO
    def tag(self):
        return time.time()

    def to_odl_meta(self, rfc_meta):
        d_vtags = rfc_meta['dependent-vtags']
        cost_type = rfc_meta['cost-type']
        return {
            'dependent-vtags': self.to_odl_dependent_vtags(d_vtags),
            'cost-type': self.to_odl_cost_type(cost_type)
        }

    def to_odl_dependent_vtags(self, rfc_d_vtags):
        odl_d_vtags = []
        for d_vtags in rfc_d_vtags:
            odl_d_vtags.append({
                'resource-id': d_vtags['resource-id'],
                'tag': d_vtags['tag']
            })
        return odl_d_vtags

    def to_odl_cost_type(self, rfc_cost_type):
        cost_type =  {
            'cost-mode': rfc_cost_type['cost-mode'],
            'cost-metric': rfc_cost_type['cost-metric'],
        }
        if 'description' in rfc_cost_type:
            cost_type['description'] = rfc_cost_type['description']
        return cost_type

    def to_odl_maps(self, rfc_maps):
        maps = []
        for src in rfc_maps:
            odl_map = {}
            odl_map['src'] = src
            dst_costs = []
            for dst in rfc_maps[src]:
                dst_costs.append({
                    "dst" : dst,
                    "cost" : rfc_maps[src][dst]
                })
            odl_map['dst-costs'] = dst_costs
            maps.append(odl_map)
        return maps

    def to_rfc_meta(self, odl_meta):
        odl_d_vtags = odl_meta['dependent-vtags']
        odl_cost_type = odl_meta['cost-type']
        return {
            'dependent-vtags': self.to_rfc_dependent_vtags(odl_d_vtags),
            'cost-type': self.to_rfc_cost_type(odl_cost_type)
        }

    def to_rfc_dependent_vtags(self, odl_d_vtags):
        rfc_d_vtags = []
        for d_vtags in odl_d_vtags:
            rfc_d_vtags.append({
                'resource-id': d_vtags['resource-id'],
                'tag': d_vtags['tag']
            })
        return rfc_d_vtags

    def to_rfc_cost_type(self, odl_cost_type):
        cost_type = {
            'cost-mode': odl_cost_type['cost-mode'],
            'cost-metric': odl_cost_type['cost-metric']
        }
        if 'description' in odl_cost_type:
            cost_type['description'] = odl_cost_type['description']
        return cost_type

    def to_rfc_maps(self, odl_maps):
        rfc_maps = {}
        for odl_map in odl_maps:
            src = odl_map['src']
            dst_costs = odl_map['dst-costs']
            rfc_map = {}
            for dst_cost in dst_costs:
                dst = dst_cost['dst']
                #TODO: replace it with dst_cost['cost']
                rfc_map[dst] = 'dummy'
            rfc_maps[src] = rfc_map
        return rfc_maps
