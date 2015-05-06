# About ALTO-server project

## Prerequisites

In current approach we require the following extra python libraries (some other
packages such as `configparser` often comes with a python distribution)

- [`bottle.py`][bottle.py],
- [`mimeparse`][mimeparse],
- [`SubnetTree`][subnettree]

Also since the packages in [backends](backends) are required using the example
configuration file, the path must be added to the python path before running the
server. It can be done by putting the following line in files such as `.bashrc`:

~~~bash
export PYTHONPATH=$PATH_TO_ALTO_SERVER:$PATH_TO_ALTO_SERVER_BACKENDS:$PYTHONPATH
~~~

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
[subnettree]: https://github.com/bro/pysubnettree

# About Advanced `PaltoServer` and `PaltoManager`

A progress to enhance the management ability of `palto` is on-going. A new
`PaltoServer` and `PaltoManager` are implemented. Trying them out with:

~~~bash
python -m palto.paltoserver

python -m palto.paltomanager
~~~

And you can use the following commands to test them out:

~~~bash
# for paltoserver

## should get 501
curl -D - -X GET http://localhost:3400/test

## should get 200
curl -D - -X GET http://localhost:3400/get_baseurl

# for paltomanager

## should get 404
curl -D -X GET http://localhost:3400/alto/test_sf_networkmap

## should get 200
curl -D - -X POST --data-binary @examples/input/test_staticfile.conf \
      http://localhost:3400/add-backend/test_sf_networkmap

## should get 200
curl -D -X GET http://localhost:3400/alto/test_sf_networkmap

## should get 200
curl -D - -X POST http://localhost:3400/remove-backend/test_sf_networkmap

## should get 404 again
curl -D -X GET http://localhost:3400/alto/test_sf_networkmap
~~~

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
curl -D - -X GET http://localhost:3400/test_sf_networkmap
curl -D - -X GET http://localhost:3400/test_sf_costmap
~~~

You can also run the following command to see the generated ird:

~~~
curl -D - -X GET http://localhost:3400/
~~~

# About the ECSLite

See [ECSLite](backends/paltoecslite/README.md)

# Features in the Future

- Improve the code structure for server/backend/frontend
- Management interface for palto
- Dependency management and tracing (especially for ODL-backend)
- Tag support
