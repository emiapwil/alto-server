#!/usr/bin/env python3

from palto.rfc7285 import AbstractNetworkMapBackend
from palto import errors
import palto.frontend
import logging
import json

class FilteredNetworkMapLite(AbstractNetworkMapBackend):
    """
    """

    def __init__(self, config, networkmap):
        AbstractNetworkMapBackend.__init__(self, config, True)
        self.networkmap = networkmap

    def parse_input(raw_data):
        data = json.loads(raw_data)
        if not 'pids' in data:
            raise Exception('Must specify pids in filtered network map')
        return data['pids'], data.get('address-types', None)

    def _post(self, request, response):
        try:
            data = request.body.getvalue().decode()
            pids, addrtypes = FilteredNetworkMapLite.parse_input(data)
        except Exception as e:
            logging.warning('Failed to parse input: %s:%s', data, e)
            return errors.bad_request(response, message=e, exception=e)

        try:
            nm = palto.utils.get_json_map(self.networkmap, ['meta', 'network-map'])
            nm_data = nm['network-map']
        except Exception as e:
            logging.error('Failed to get network map: %s', self.networkmap)
            return errors.server_error(response, e)

        fnm_data = {}
        for pid in pids:
            if not pid in nm_data:
                logging.warning('Pid %s is not in %s', pid, self.networkmap)
                continue
            types = addrtypes if addrtypes is not None else nm_data[pid].keys()
            types = types & nm_data[pid].keys()
            fnm_data[pid] = { t: nm_data[pid][t] for t in types }

        output = { 'meta': nm['meta'], 'network-map': fnm_data }
        return output

    def post(self, request, response):
        actual_post = lambda req, rep: self._post(req, rep)
        return AbstractNetworkMapBackend.post(self, request, response, actual_post)

def create_instance(name, config, environ):
    networkmap = config.get('fnmlite', 'networkmap')
    if networkmap is None:
        logging.error('FilteredNetworkMapLite requires networkmap option')
        return None

    nm_url = palto.frontend.get_url(environ, networkmap)
    return FilteredNetworkMapLite(config, nm_url)

