#!/usr/bin/env python3
import json
import time

class ODLCostMap:
    def load_from_str(self, json_str):
        self.content = json.load(json_str)
        return self

    def load_from_rfc(self, rfc_cost_map):
        self.content = {
            'alto:resource-id': self.resource_id(rfc_cost_map['meta']),
            'alto:tag': self.tag(),
            'alto:meta': self.to_odl_meta(rfc_cost_map['meta']),
            'alto:map': self.to_odl_maps(rfc_cost_map['cost-map'])
        }
        return self

    def resource_id(self, rfc_meta):
        resource_id = rfc_meta['dependent-vtags'][0]['resource-id']
        cost_mode = rfc_meta['cost-type']['cost-mode']
        cost_metric = rfc_meta['cost-type']['cost-metric']
        return resource_id + '-' + cost_mode + '-' + cost_metric

    #TODO
    def tag(self):
        return int(time.time())

    def to_odl_meta(self, rfc_meta):
        d_vtags = rfc_meta['dependent-vtags']
        cost_type = rfc_meta['cost-type']
        return {
            'alto:dependent-vtags': self.to_odl_dependent_vtags(d_vtags),
            'alto:cost-type': self.to_odl_cost_type(cost_type)
        }

    def odl_cost_map(self):
        return self.content

    def odl_cost_map_json(self):
        return json.dumps(self.odl_cost_map())

    def rfc_cost_map(self):
        return {
            'meta': self.to_rfc_meta(self.content['alto:meta']),
            'cost-map': self.to_rfc_maps(self.content['alto:map'])
        }

    def rfc_cost_map_json(self):
        return json.dumps(self.rfc_cost_map())

    def to_odl_dependent_vtags(self, rfc_d_vtags):
        odl_d_vtags = []
        for d_vtags in rfc_d_vtags:
            odl_d_vtags.append({
                'alto:resource-id': d_vtags['resource-id'],
                'alto:vtag': d_vtags['tag']
            })
        return odl_d_vtags

    def to_odl_cost_type(self, rfc_cost_type):
        cost_type =  {
            'alto:cost-mode': rfc_cost_type['cost-mode'],
            'alto:cost-metric': rfc_cost_type['cost-metric'],
        }
        if 'description' in rfc_cost_type:
            cost_type['alto:description'] = rfc_cost_type['description']
        return cost_type

    def to_odl_maps(self, rfc_maps):
        maps = []
        for src in rfc_maps:
            odl_map = {}
            odl_map['alto:src'] = src
            dst_costs = []
            for dst in rfc_maps[src]:
                dst_costs.append({
                    "alto:dst" : dst,
                    "alto:cost" : rfc_maps[src][dst]
                })
            odl_map['alto:dst-costs'] = dst_costs
            maps.append(odl_map)
        return maps

    def to_rfc_meta(self, odl_meta):
        return {
            'dependent-vtags': self.to_rfc_dependent_vtags(odl_meta['alto:dependent-vtags']),
            'cost-type': self.to_rfc_cost_type(odl_meta['alto:cost-type']),
        }

    def to_rfc_dependent_vtags(self, odl_d_vtags):
        rfc_d_vtags = []
        for d_vtags in odl_d_vtags:
            rfc_d_vtags.append({
                'resource-id': d_vtags['alto:resource-id'],
                'tag': d_vtags['alto:vtag']
            })
        return rfc_d_vtags

    def to_rfc_cost_type(self, odl_cost_type):
        cost_type = {
            'cost-mode': odl_cost_type['alto:cost-mode'],
            'cost-metric': odl_cost_type['alto:cost-metric'],
        }
        if 'alto:description' in odl_cost_type:
            cost_type['description'] = odl_cost_type['alto:description']
        return cost_type

    def to_rfc_maps(self, odl_maps):
        rfc_maps = {}
        for odl_map in odl_maps:
            src = odl_map['alto:src']
            dst_costs = odl_map['alto:dst-costs']
            rfc_map = {}
            for dst_cost in dst_costs:
                rfc_map[dst_cost['alto:dst']] = dst_cost['alto:cost']
            rfc_maps[src] = rfc_map
        return rfc_maps
