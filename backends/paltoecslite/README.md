# About ECSLite

`ECSLite` is a simple implementation for *endpoint cost service* defined in
section 11.5.1 of RFC 7285. It finds the PIDs of the input endpoints from a list
of network maps and returns the corresponding cost in the cost map.

See [example config](examples/resources/test_ecslite.conf) for how to configure
it.

There is also an [example input](examples/input/ecs.json) that can be used to
test the service by executing

~~~bash
curl -D - -H 'content-type: application/alto-endpointcostparams+json' \
      -d @examples/input/ecs.json -X POST http://localhost:3400/ecslite
~~~

## TODO

- use filtered cost map instead of cost map
- check dependencies for the cost map
