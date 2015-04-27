from bottle import request, response, run, route
import json

tested = []

@route('/test')
def test():
    response.set_header('Content-Type', 'application/test+json')
    return json.dumps({ 'a' : 1, 'b' : 2})

@route('/test/<name:re:.+>')
def test_name_with_slash(name):
    response.set_header('Content-Type', 'application/echo+json')
    tested.append(name)
    return json.dumps(tested)

@route('/test_request', method='POST')
def test_request():
    response.set_header('Content-Type', 'application/echo+json')
    return request.body

run(host='localhost', port=3200, debug=True)
