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

## Usage

~~~
python -m palto.server -c examples/palto.conf
~~~

[bottle.py]: http://bottlepy.org/
[mimeparse]: https://github.com/dbtsai/python-mimeparse
