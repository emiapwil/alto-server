# About ALTO-server project

## Architecture

### Front-end

We will be using [bottle](http://bottlepy.org/) to provide RESTful service.

### Back-end

There are currently two back-end types to be supported:

- Static file back-end: reading data from a static file
- Open Daylight back-end: reading data from an ODL controller

## Usage

~~~
python -m palto.server -c examples/palto.conf
~~~
