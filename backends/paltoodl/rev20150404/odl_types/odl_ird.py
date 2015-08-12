class ODLIRD():
    def load_odl_ird(self, odl_ird):
        self.content = odl_ird
        return self

    def rfc_ird(self):
        return {
            'meta': self.to_rfc_meta(self.content['meta']),
            'resources': self.to_rfc_resources(self.content['resources'])
        }

    def to_rfc_meta(self, odl_meta):
        return {
            'cost-types': self.to_rfc_cost_type(odl_meta['cost-types']),
            'default-alto-network-map': odl_meta['default-alto-network-map']['resource-id']
        }

    def to_rfc_cost_type(self, odl_cost_types):
        cost_types = {}
        for cost_type in odl_cost_types:
            cost_type_name = cost_type['cost-type-name']
            cost_types[cost_type_name] = {
                'cost-mode': cost_type['cost-mode'],
                'cost-metric': cost_type['cost-metric'],
                'description': cost_type['description']
            }
        return cost_types

    def to_rfc_resources(self, odl_resources):
        resources = {}
        for resource in odl_resources:
            resource_id = resource['resource-id']
            resources[resource_id] = self.to_rfc_resource(resource)
        return resources

    def to_rfc_resource(self, odl_resource):
        rfc_resource = {
            'uri': odl_resource['uri'],
            'media-type': odl_resource['media-type']
        }
        if 'accepts' in odl_resource:
            rfc_resource['accepts'] = ','.join(odl_resource['accepts'])
        if 'capabilities' in odl_resource:
            rfc_resource['capabilities'] = odl_resource['capabilities']
        if 'uses' in odl_resource:
            rfc_resource['uses'] = odl_resource['uses']
        return rfc_resource
