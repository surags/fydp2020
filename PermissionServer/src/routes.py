import bottle

from src.wsgi import app
from bottle import response
from bottle import post, get, put


@get('/')
def listing_handler():
    return [b"Hello"]


@get('/application/add/permission/<application_id>')
def listing_handler(application_id):
    return [b"Hello"]


@get('/')
@app.auth.verify_request(scopes=['streamingOS'])
def listing_handler():
    return [b"Hello"]


@get('/mail')
@app.auth.verify_request(scopes=['streamingOS'])
def access_streamingOS():
    response.status = 200
    response.body = bottle.request.oauth
    return "Welcome {}, you have permissioned {} to use streamingOS".format(
        bottle.request.oauth["user"],
        bottle.request.oauth["client"].client_id
    )


@post('/token')
@app.auth.create_token_response()
def generate_token():
    pass
