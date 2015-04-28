class AbstractODLMap:
    def load_from_odl(self, odl_map):
        raise NotImplementedError( "Should have implemented this" )

    def load_from_rfc(self, rfc_map):
        raise NotImplementedError( "Should have implemented this" )

    def resource_id(self):
        raise NotImplementedError( "Should have implemented this" )

    def odl_map(self):
        raise NotImplementedError( "Should have implemented this" )

    def rfc_map(self):
        raise NotImplementedError( "Should have implemented this" )
