#!/usr/bin/env python3

from palto.rfc7285 import AbstractEndpointCostMapBackend
import logging
import json
from SubnetTree import SubnetTree
import palto.frontend
import palto.utils
from palto.utils import correct_inet_format, cost_type_match

def encode_addr(family, addr):
    return '{}:{}'.format(family, addr)

def decode_addr(addr):
    return addr.split(':')

class ECSLite(AbstractEndpointCostMapBackend):
    """
    """

    def __init__(self, config, networkmaps = set(), costmap = None):
        if (networkmaps is None) or (len(networkmaps) == 0):
            raise Exception("Missing dependency: ECSLite requires network maps")
        if costmap is None:
            raise Exception("Missing dependency: ECSLite requires cost maps")

        AbstractEndpointCostMapBackend.__init__(self, config)
        self.networkmaps = networkmaps
        self.costmap = costmap

    def setup_pid_mapping(networkmaps):
        mapping = { 'ipv4' : SubnetTree(), 'ipv6' : SubnetTree() }
        for url in networkmaps:
            networkmap = palto.utils.get_json_map(url, ['network-map'])['network-map']
            for pid, groups in networkmap.items():
                for family, prefixes in groups.items():
                    prefixes = [ p for p in prefixes if correct_inet_format(family, p) ]
                    for p in prefixes:
                        mapping[family][p] = pid
        return mapping

    def parse_input(data):
        data = json.loads(data)
        _cost_type = data['cost-type']
        cost_type = { k: _cost_type[k] for k in ['cost-mode', 'cost-metric'] }
        srcs = data['endpoints']['srcs']
        dsts = data['endpoints']['dsts']
        return cost_type, srcs, dsts

    def find_pid(mapping, addresses):
        pids = {}
        for _addr in addresses:
            family, addr = decode_addr(_addr)
            if not family in mapping:
                logging.warning('Family %s not supported', family)
                continue
            if not correct_inet_format(family, addr):
                logging.warning('Bad %s address format %s', family, addr)
                continue
            if not family in pids:
                pids[family] = {}
            pids[family][addr] = mapping[family][addr]
        return pids

    def get_costs(costmap, cost_type, srcs, dsts):
        """ TODO
        use filtered cost map instead of cost map
        """
        costs = {}
        data = palto.utils.get_json_map(costmap, ['meta', 'cost-map'])
        _cost_type = data['meta']['cost-type']
        if not cost_type_match(_cost_type, cost_type):
            logging.warning('Cost type %s not supported by %s', cost_type, costmap)
            return None
        _costs = data['cost-map']

        for family in srcs:
            if not family in dsts:
                continue
            if not family in costs:
                costs[family]= {}
            src_pids, dst_pids = srcs[family], dsts[family]
            for saddr, spid in src_pids.items():
                costs[family][saddr] = { daddr: _costs[spid][dpid] for (daddr, dpid) in dst_pids.items() }
        return costs

    def compose_output(cost_type, costs):
        output = {}
        output['meta'] = { 'cost-type' : cost_type }
        output['endpoint-cost-map'] = {}
        for family in costs:
            for src in costs[family]:
                _costs = costs[family][src]
                cost = { encode_addr(family, dst): _costs[dst] for dst in _costs }
            output['endpoint-cost-map'].update({ encode_addr(family, src): cost })

        return output

    def _post(self, request, response):
        try:
            data = request.body.getvalue().decode()
            cost_type, srcs, dsts = ECSLite.parse_input(data)
        except Exception as e:
            logging.error('Failed to parse input for ECSLite: %s', request.body)
            raise e

        try:
            mapping = ECSLite.setup_pid_mapping(self.networkmaps)
            src_pids = ECSLite.find_pid(mapping, srcs)
            dst_pids = ECSLite.find_pid(mapping, dsts)
        except Exception as e:
            logging.error('Failed to setup the mapping: %s', e)
            raise e

        try:
            costs = ECSLite.get_costs(self.costmap, cost_type, src_pids, dst_pids)
        except Exception as e:
            logging.error('Failed to get costs: %s', e)
            raise e

        return ECSLite.compose_output(cost_type, costs)

    def post(self, request, response):
        actual_post = lambda req, rep: self._post(req, rep)
        return AbstractEndpointCostMapBackend.post(self, request, response, actual_post)

def create_instance(resource_id, config, global_config):
    networkmaps = config.get('ecslite', 'networkmaps').split(',')
    networkmaps = { nm for nm in [x.strip() for x in networkmaps] }
    costmap = config.get('ecslite', 'costmap')

    if len(networkmaps) == 0 or costmap is None:
        logging.error('ECSLite requires networkmaps and costmap')
        return None

    nm_urls = { palto.frontend.get_url(global_config, nm) for nm in networkmaps }
    cm_url = palto.frontend.get_url(global_config, costmap)

    return ECSLite(config, nm_urls, cm_url)
