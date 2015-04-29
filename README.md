# About ALTO-server project

## Prerequisites

In current approach we require the following python libraries:

- [`bottle.py`][bottle.py],
- [`mimeparse`][mimeparse]

## Architecture

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
