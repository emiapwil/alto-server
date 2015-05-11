# About AutoIRDPlugin

AutoIRDPlugin generates the IRD by reading meta information from the backends
using the `get_meta` method.

To register the backends with AutoIRDPlugin, there are two steps:

*Add an [ird] section in the configuration file*

~~~
[ird]
mountpoints=, secondary_ird
~~~

There is only one option `mountpoints` required by AutoIRDPlugin. It defines
a list of IRD services where IRD the resource wants to register itself. The
option contains the name of the services and separates them with a ','.

Like the name suggests, AutoIRDPlugin will generates the corresponding IRD
services if they doesn't exist.

*Define an `get_meta` function*

The `get_meta` function should be able to run with only a `self` parameter. It
returns a map with at least two items: *resource-id* and *output*.

The data will be converted to rfc 7285 automatically. The mapping between
AutoIRDPlugin-required and RFC-7285-formatted data is shown below:

~~~
AutoIRD -> RFC7285
resource-id -> uri
output -> media-type
input -> accepts
capabilities -> capabilities
uses -> uses
~~~

There is a handler that will manage the cost types and cost-type names. So the
`get_meta` function should have a `cost-types` in capabilities instead of
`cost-type-names`.
