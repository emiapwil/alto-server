#!/usr/bin/env python3

def get_alto_mimetype(name):
    return 'application/alto-{}+json'.format(name)

IRD                     = get_alto_mimetype('directory')

NETWORK_MAP             = get_alto_mimetype('networkmap')
NETWORK_MAP_FILTER      = get_alto_mimetype('networkmapfilter')

COST_MAP                = get_alto_mimetype('costmap')
COST_MAP_FILTER         = get_alto_mimetype('costmapfilter')

ENDPOINT_PROP_MAP       = get_alto_mimetype('endpointprop')
ENDPOINT_PROP_PARAMS    = get_alto_mimetype('endpointpropparams')

ENDPOINT_COST           = get_alto_mimetype('endpointcost')
ENDPOINT_COST_PARAMS    = get_alto_mimetype('endpointcostparams')

ERROR                   = get_alto_mimetype('error')

