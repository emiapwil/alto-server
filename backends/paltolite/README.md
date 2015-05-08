# About ECSLite

`ECSLite` is a simple implementation for *endpoint cost service* defined in
section 11.5.1 of RFC 7285. It finds the PIDs of the input endpoints from a list
of network maps and returns the corresponding cost in the cost map.

See [example config](../../examples/resources/test_ecslite.conf) for how to configure
it.

There is also an [example input](../../examples/input/ecs.json) that can be used to
test the service by executing

~~~bash
curl -D - -H 'content-type: application/alto-endpointcostparams+json' \
      -d @examples/input/ecs.json -X POST http://localhost:3400/ecslite
~~~

## TODO

- use filtered cost map instead of cost map
- check dependencies for the cost map

# About FilteredNetworkMapLite

The mechanism is simple: retrieve data from the network map and pick the
required data.

Use the following command to test it out:

~~~bash
curl -D - -H "content-type: application/alto-networkmapfilter+json" \
      -X POST -d @examples/input/test_fnm.json http://localhost:3400/fnmlite
~~~

# About FilteredCostMapLite

The mechanism is simple: retrieve data from the cost map and pick the required
data.

Use the following command to test it out:

~~~bash
curl -D - -H "content-type: application/alto-costmapfilter+json" \
      -X POST -d @examples/input/test_fcm.json http://localhost:3400/fcmlite
