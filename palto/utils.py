#!/usr/bin/env python3

import requests
from . import errors
import ipaddress

inet_network_types = {
    'ipv4' : ipaddress.IPv4Network,
    'ipv6' : ipaddress.IPv6Network
}

def correct_inet_format(family, prefix):
    if family not in inet_network_types:
        return False
    return type(ipaddress.ip_network(prefix)) is network_type[family]

def cost_type_match(x, y):
    mode_match = (x.get('cost-mode') == y.get('cost-mode'))
    metric_match = (x.get('cost-metric') == y.get('cost-metric'))
    return (mode_match and metric_match)

def get_json_map(url, required_sections = []):
    response = requests.get(url)
    if errors.is_error(response.status_code):
        raise Exception('Failed to fetch data from {}'.format(url))
    data = response.json()
    for section in required_sections:
        if not section in data:
            raise Exception('Failed to get map data from {}'.format(url))
    return data
