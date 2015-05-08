#!/usr/bin/env python3

from palto.rfc7285 import AbstractEndpointPropMapBackend
import json
import logging
from palto import errors
import palto.frontend
from .utils import reverse_networkmap, encode_addr, decode_addr
from palto.utils import correct_inet_format

class EPSLite(AbstractEndpointPropMapBackend):
    """
    """

    def __init__(self, config, networkmaps = set(), urls = {}):
        AbstractEndpointPropMapBackend.__init__(self, config)
        self.prop_urls = { '.'.join([nm, 'pid']): urls[nm] for nm in networkmaps }
        self.networkmaps = networkmaps
        self.urls = urls

    def parse_input(data):
        data = json.loads(data)
        return data['properties'], data['endpoints']

    def setup_pid_mapping(networkmaps, vtags = []):
        mapping = {}
        for prop, url in networkmaps.items():
            try:
                networkmap = palto.utils.get_json_map(url, ['meta', 'network-map'])
                vtag, data = networkmap['meta']['vtag'], networkmap['network-map']
                mapping[prop] = reverse_networkmap(data)
                vtags.append(vtag)
            except Exception as e:
                logging.warning('Failed to fetch map data from %s', url)
                continue

        return mapping, vtags

    def _post(self, request, response):
        try:
            data = request.body.getvalue().decode()
            properties, endpoints = EPSLite.parse_input(data)
        except Exception as e:
            logging.warning('Failed to parse input %s', str(request.body))
            return errors.bad_request(response, exception=e)

        try:
            properties = properties & self.prop_urls.keys()
            prop_urls = { prop: self.prop_urls[prop] for prop in properties }
            mapping, vtags = EPSLite.setup_pid_mapping(prop_urls)
        except Exception as e:
            logging.error('Failed to setup mapping')
            return errors.server_error(response, exception=e)

        meta_out = { 'dependent-vtags' : vtags }
        data_out = {}
        for ep in endpoints:
            family, address = decode_addr(ep)
            if not correct_inet_format(family, address):
                logging.warning('Bad format %s: %s', family, address)
                continue
            props = {}
            for prop in properties:
                prop_map = mapping[prop][family]
                if not address in prop_map:
                    continue
                props.update({ prop: prop_map[address]})
            if len(props) > 0:
                data_out[ep] = props

        return { 'meta': meta_out, 'endpoint-properties': data_out }

    def post(self, request, response):
        actual_post = lambda req, rep: self._post(req, rep)
        return AbstractEndpointPropMapBackend.post(self, request, response, actual_post)

def create_instance(name, config, global_config):
    networkmaps = config.get('epslite', 'networkmaps').split(',')
    networkmaps = { x.strip() for x in networkmaps }

    if len(networkmaps) == 0:
        logging.error('EPSLite requires networkmaps')

    urls = { nm: palto.frontend.get_url(global_config, nm) for nm in networkmaps }
    return EPSLite(config, networkmaps, urls)
