#!/usr/bin/env python3

from .odl_types.odl_network_map import ODLNetworkMap
from .odl_types.odl_cost_map import ODLCostMap
from .odl_types.odl_endpoint_property_map import ODLEndpointPropertyMap
from .odl_types.odl_ird import ODLIRD
from requests.auth import HTTPBasicAuth
import requests
import logging
import json

class ODLAdapter:
    HEADERS = {'Content-Type': 'application/yang.data+json'}
    NETWORK_MAP = 'network-map'
    COST_MAP = 'cost-map'
    ENDPOINT_PROPERTY_MAP = 'endpoint-property-map'

    def __init__(self, args):
        self.host = args['host']
        self.resource_url = self.host + '/restconf/config/alto-service:resources/'
        self.auth = HTTPBasicAuth(args['user'], args['password'])

    def get_ird(self):
        text = self.http_get(self.ird_url())
        if text is not None:
            odl_ird = ODLIRD().load_odl_ird(self.unwrap_ird(text))
            return self.to_json(odl_ird.rfc_ird())

    def unwrap_ird(self, text):
        return json.loads(text)['IRD']

    def get_endpoint_property_map(self):
        return self.get_map(self.ENDPOINT_PROPERTY_MAP, None)

    def get_network_map(self, resource_id):
        return self.get_map(self.NETWORK_MAP, resource_id)

    def get_cost_map(self, resource_id):
        return self.get_map(self.COST_MAP, resource_id)

    def get_map(self, map_type, resource_id):
        text = self.http_get(self.map_url(map_type, resource_id))
        if text is not None:
            return self.extract_rfc_map(map_type, text)

    def extract_rfc_map(self, map_type, text):
        map_data = self.unwrap_map(map_type, text)
        odl_map = self.get_map_instance(map_type).load_odl_map(map_data)
        return self.to_json(odl_map.rfc_map())

    def put_network_map(self, rfc_network_map):
        self.put_map(self.NETWORK_MAP, rfc_network_map)

    def put_cost_map(self, rfc_cost_map):
        self.put_map(self.COST_MAP, rfc_cost_map)

    def put_endpoint_property_map(self, rfc_endpoint_prop_map):
        self.put_map(self.ENDPOINT_PROPERTY_MAP, rfc_endpoint_prop_map)

    def put_map(self, map_type, rfc_map):
        odl_map = self.get_map_instance(map_type).load_rfc_map(rfc_map)
        map_data = self.wrap_map(map_type, odl_map.odl_map())
        url = self.map_url(map_type, odl_map.resource_id())
        self.http_put(url, map_data)

    def get_map_instance(self, map_type):
        if map_type == self.NETWORK_MAP:
            return ODLNetworkMap()
        if map_type == self.COST_MAP:
            return ODLCostMap()
        if map_type == self.ENDPOINT_PROPERTY_MAP:
            return ODLEndpointPropertyMap()

    def wrap_map(self, map_type, map_data):
        if map_type == self.ENDPOINT_PROPERTY_MAP:
            wrapped_map = {map_type: map_data}
        else:
            wrapped_map = {map_type: [map_data]}
        return self.to_json(wrapped_map)

    def unwrap_map(self, map_type, text):
        if map_type == self.ENDPOINT_PROPERTY_MAP:
            return json.loads(text)[map_type]
        else:
            return json.loads(text)[map_type][0]

    def map_url(self, map_type, resource_id):
        if map_type == self.ENDPOINT_PROPERTY_MAP:
            return self.resource_url + 'alto-service:' + self.ENDPOINT_PROPERTY_MAP
        else:
            return self.resource_url + 'alto-service:' + map_type + 's/alto-service:' + map_type + '/' + resource_id

    def ird_url(self):
        return self.resource_url + 'alto-service:IRD'

    def http_get(self, url):
        r = requests.get(url, auth=self.auth, headers=self.HEADERS)
        if self.check_response(r, 'HttpGet'):
            return r.text

    def http_put(self, url, data):
        r = requests.put(url, auth=self.auth, data=data, headers=self.HEADERS)
        self.check_response(r, 'HttpPut')

    def check_response(self, resp, operation):
        if resp.status_code == requests.codes.ok:
            logging.info('ODLAdapter: %s succeed', operation)
            return True
        logging.error('ODLAdapter: %s failed', operation)
        logging.error('ODLAdapter: Status: %s', resp.status_code)
        logging.error('ODLAdapter: Response body: %s', resp.text)
        raise RuntimeError(resp.text)

    def to_json(self, dict_data):
        return json.dumps(dict_data, separators=(',', ':'))
