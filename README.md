# About ALTO-server project

## Prerequisites

In current approach we require the following python libraries:

- [`bottle.py`][bottle.py],
- [`mimeparse`][mimeparse]

## Architecture

See [architecture](docs/architecture.png).

Each instance **MAY** have multiple roles. The only one required is the *HTTP
service provider* which is named `palto.Backend` currently.

Only if the backend instance wants to be included in the IRD provided by palto
server, the `ird` section in the corresponding configuration file **CAN** and
**MUST** be provided. In that circumstance, the instance has to implement the
`BasicIRDResource` interface. The *mountpoint* option in *ird* section specifies
where the resource wants to register itself.

### Front-end

We will be using [bottle][bottle.py] to provide RESTful service.

### Back-end

There are currently two back-end types to be supported:

- Static file back-end: reading data from a static file
- Open Daylight back-end: reading data from an ODL controller

#### Implementing a customized back-end

To write a customized back-end, the module should contain the following method:

~~~
create_instance(resource-id, backend-config, global-config)
~~~

## Usage

~~~
python -m palto.server -c examples/palto.conf
~~~

## Debugging

BasicIRD and some standard handlers are tested by:

~~~
python -m palto.rfc7285.irdhandler
~~~

[bottle.py]: http://bottlepy.org/
[mimeparse]: https://github.com/dbtsai/python-mimeparse

# About Static File Back-end

The support for network map is implemented. The example data file can be found
in `examples/static_file/networkmap.json`.

## Testing static file back-end

Run the following command in one terminal to start the server:

~~~
python -m palto.server -c examples/palto.conf
~~~

Then run the following command in another terminal to see the result:

~~~
curl -D - -X GET http://localhost:3400/test_sf
~~~

You can also run the following command to see the generated ird:

~~~
curl -D - -X GET http://localhost:3400/
~~~
