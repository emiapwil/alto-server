
def get_alto_type(name):
    return 'application/alto-{}+json'.format(name)

IRD                     = get_alto_type('directory')

NETWORK_MAP             = get_alto_type('networkmap')
NETWORK_MAP_FILTER      = get_alto_type('networkmapfilter')

COST_MAP                = get_alto_type('costmap')
COST_MAP_FILTER         = get_alto_type('costmapfilter')

ENDPOINT_PROP_MAP       = get_alto_type('endpointprop')
ENDPOINT_PROP_PARAMS    = get_alto_type('endpointpropparams')

ENDPOINT_COST           = get_alto_type('endpointcost')
ENDPOINT_COST_PARAMS    = get_alto_type('endpointcostparams')

ERROR                   = get_alto_type('error')

