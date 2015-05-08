#!/usr/bin/env python3

from palto.rfc7285 import AbstractCostMapBackend
from palto import errors
import palto.frontend
import logging
import json
import palto.utils

class FilteredCostMapLite(AbstractCostMapBackend):
    """
    """

    def __init__(self, config, costmap):
        AbstractCostMapBackend.__init__(self, config, True)
        self.costmap = costmap

    def parse_input(data):
        data = json.loads(data)
        if not 'cost-type' in data:
            raise Exception('Must specify cost-type in filtered cost map')
        cost_type = data['cost-type']
        for field in ['cost-mode', 'cost-metric']:
            if not field in cost_type:
                raise Exception('Invalid cost-type: {}'.format(cost_type))
        constraints = data.get('constraints')
        srcs = data.get('pids', {}).get('srcs')
        dsts = data.get('pids', {}).get('dsts')
        return cost_type, constraints, srcs, dsts

    def _post(self, request, response):
        try:
            data = request.body.getvalue().decode()
            # constaints are not supported now
            cost_type, _, srcs, dsts = FilteredCostMapLite.parse_input(data)
        except Exception as e:
            logging.warning('Failed to parse input: %s:%s', data, e)
            return errors.bad_request(response, message=e, exception=e)

        try:
            cm = palto.utils.get_json_map(self.costmap, ['meta', 'cost-map'])
            cm_meta = cm['meta']
            cm_data = cm['cost-map']
        except Exception as e:
            logging.error('Failed to get cost map: %s', self.costmap)
            return errors.server_error(response, exception = e)

        if not 'cost-type' in cm_meta:
            TEMPLATE = 'cost map {} returns no \'cost-type\' in meta'
            return errors.server_error(response, TEMPLATE.format(self.costmap))

        if not palto.utils.cost_type_match(cost_type, cm_meta['cost-type']):
            TEMPLATE = 'Cost type {} is not supported by {}'
            return errors.bad_request(TEMPLATE.format(cost_type, self.costmap))

        fcm_data = {}
        srcs = srcs if srcs is not None else cm_data.keys()
        dsts = dsts if dsts is not None else cm_data.keys()
        srcs = srcs & cm_data.keys()
        for src in srcs:
            _dsts = dsts & cm_data[src].keys()
            fcm_data[src] = { dst: cm_data[src][dst] for dst in _dsts }

        output = { 'meta': cm['meta'], 'cost-map': fcm_data }
        return output

    def post(self, request, response):
        actual_post = lambda req, rep: self._post(req, rep)
        return AbstractCostMapBackend.post(self, request, response, actual_post)

def create_instance(name, config, global_config):
    costmap = config.get('fcmlite', 'costmap')
    if costmap is None:
        logging.error('FilteredCostMapLite requires costmap option')
        return None

    cm_url = palto.frontend.get_url(global_config, costmap)
    return FilteredCostMapLite(config, cm_url)

