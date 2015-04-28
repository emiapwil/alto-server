#!/usr/bin/env python3

from .odl_types.odl_network_map import ODLNetworkMap
from .odl_types.odl_cost_map import ODLCostMap
from requests.auth import HTTPBasicAuth
import requests
import logging
import json

class ODLAdapter:
    HEADERS = {'Content-Type': 'application/yang.data+json'}

    def __init__(self, args):
        self.host = args['host']
        self.resource_url = self.host + '/restconf/config/alto-service:resources/'
        self.auth = HTTPBasicAuth(args['user'], args['password'])

    def get_network_map(self, resource_id):
        url = self.network_map_url(resource_id)
        r = requests.get(url, auth=self.auth, headers=self.HEADERS)
        if self.check_response(r, 'HttpGet'):
            odl_network_map = self.unwrap_network_map(r.text)
            network_map = ODLNetworkMap().load_from_odl(odl_network_map)
            return self.to_json(network_map.rfc_network_map())

    def put_network_map(self, rfc_network_map):
        network_map = ODLNetworkMap().load_from_rfc(rfc_network_map)
        map_data = self.wrap_network_map(network_map.odl_network_map())
        url = self.network_map_url(network_map.resource_id())
        r = requests.put(url, auth=self.auth, data=map_data, headers=self.HEADERS)
        self.check_response(r, 'HttpPut')

    def wrap_network_map(self, network_map):
        wrap_data = {'network-map': [network_map]}
        return self.to_json(wrap_data)

    def unwrap_network_map(self, wrapped_network_map):
        network_maps = json.loads(wrapped_network_map)
        return network_maps['network-map'][0]

    def get_cost_map(self, resource_id):
        url = self.cost_map_url(resource_id)
        r = requests.get(url, auth=self.auth, headers=self.HEADERS)
        if self.check_response(r, 'HttpGet'):
<<<<<<< HEAD:odl_adapter/odl_adapter.py
            odl_cost_map = self.unwrap_cost_map(r.text)
            cost_map = ODLCostMap().load_from_odl(odl_cost_map)
            return self.to_json(cost_map.rfc_cost_map())
=======
            cost_map = ODLCostMap().load_from_str(r.text)
            return cost_map.rfc_cost_map_json()
>>>>>>> 4cec48fd0700d78014f16660c9713a8a4d8ea301:backends/paltoodl/rev20150404/odl_adapter.py

    def put_cost_map(self, rfc_cost_map):
        cost_map = ODLCostMap().load_from_rfc(rfc_cost_map)
        map_data = self.wrap_cost_map(cost_map.odl_cost_map())
        url = self.cost_map_url(cost_map.resource_id())
        r = requests.put(url, auth=self.auth, data=map_data, headers=self.HEADERS)
        self.check_response(r, 'HttpPut')

    def wrap_cost_map(self, cost_map):
        wrap_data = {'cost-map': [cost_map]}
        return self.to_json(wrap_data)

    def unwrap_cost_map(self, wrapped_cost_map):
        cost_maps = json.loads(wrapped_cost_map)
        return cost_maps['cost-map'][0]

    def network_map_url(self, resource_id):
        return self.resource_url + 'alto-service:network-maps/alto-service:network-map/' + resource_id

    def cost_map_url(self, resource_id):
        return self.resource_url + 'alto-service:cost-maps/alto-service:cost-map/' + resource_id

    def check_response(self, resp, operation):
        if resp.status_code == requests.codes.ok:
            logging.info('ODLAdapter: %s succeed', operation)
            return True
        logging.error('ODLAdapter: %s failed', operation)
        logging.error('ODLAdapter: Status: %s', resp.status_code)
        logging.error('ODLAdapter: Response body: %s', resp.text)
        return False

    def to_json(self, dict_data):
        return json.dumps(dict_data, separators=(',', ':'))
