#!/usr/bin/env python3

def create_instance(name, config, environ):

    def test_plugin(callback):

        def wrapper(*args, **kargs):
            reply = callback(*args, **kargs)
            print(reply)

            return reply

        return wrapper

    return test_plugin
