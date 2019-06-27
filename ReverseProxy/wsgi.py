import bottle
from bottle import request, response
from bottle import post, get, put, delete

app = application = bottle.default_app()

@get('/')
def listing_handler():
    return [b"Hello World"]

if __name__ == '__main__':
    bottle.run(host = '127.0.0.1', port = 8000)