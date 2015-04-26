#!/usr/bin/env python3

from odl_types.odl_network_map import ODLNetworkMap
from odl_types.odl_cost_map import ODLCostMap
from requests.auth import HTTPBasicAuth
import requests
import logging

class ODLAdapter(Object):
    HEADERS = {'Content-Type': 'application/yang.data+json'}

    def __init__(self, args):
        self.host = args['host']
        self.resource_url = host + '/restconf/config/alto-service:resources/'
        self.auth = HTTPBasicAuth(args['user'], args['password'])

    def get_network_map(self, resource_id):
        url = self.network_map_url(self, resource_id)
        r = requests.get(url, auth=self.auth, headers=HEADERS)
        if self.check_response(r):
            network_map = ODLNetworkMap().load_from_str(r.text)
            return network_map.rfc_network_map_json()

    def put_network_map(self, rfc_network_map):
        network_map = ODLNetworkMap().load_from_rfc(rfc_network_map)
        map_data = network_map.odl_network_map_json()
        url = self.network_map_url(self, network_map.resource_id())
        r = requests.post(url, auth=self.auth, data=map_data, headers=self.HEADERS)
        self.check_response(r)

    def get_cost_map(self, resource_id):
        url = self.cost_map_url(self, resource_id)
        r = requests.get(url, auth=self.auth, headers=HEADERS)
        if self.check_response(r):
            cost_map = ODLCostMap().load_from_str(r.text)
            return network_map.rfc_network_map_json()

    def put_cost_map(self, rfc_cost_map):
        cost_map = ODLCostMap().load_from_rfc(rfc_cost_map)
        map_data = cost_map.odl_cost_map_json()
        url = self.cost_map_url(self, cost_map.resource_id())
        r = requests.post(url, auth=self.auth, data=map_data, headers=self.HEADERS)
        self.check_response(r)

    def network_map_url(self, resource_id):
        self.resource_url + 'alto-service:network-maps/alto-service:network-map/' + resource_id

    def cost_map_url(self, resource_id):
        self.resource_url + 'alto-service:cost-maps/alto-service:cost-map/' + resource_id

    def check_response(self, resp, operation):
        if resp.status_code == requests.codes.ok:
            logging.info('ODLAdapter: %s succeed', operation)
            return True
        logging.error('ODLAdapter: %s failed', operation)
        logging.error('ODLAdapter: Status: %s', resp.status_code)
        logging.error('ODLAdapter: Response body: %s', resp.text)
        return False

