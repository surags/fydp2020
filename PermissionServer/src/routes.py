import bottle

from src.helper import authentication_helper
from src.wsgi import app
from bottle import response
from bottle import post, get, put

from src.helper import router

router = router.Factory().get_router()
authentication_helper = authentication_helper.Factory().get_authentication_helper()


@get('/')
@app.auth.verify_request(scopes=['streamingOS'])
def listing_handler():
    return [b"Hello"]


@get('/setup/routes/<user_id>')
def setup_routes(user_id):
    router.setup_routes(user_id)
    response.status = 200
    return


@get('/delete/routes/<user_id>')
def delete_routes(user_id):
    router.delete_iptable_rules(user_id)
    response.status = 200
    return


# Authenticate user
@get('/student/<username>/auth/<password>')
def authenticate_user(username, password):
    try:
        response.body, response.status = authentication_helper.validate_user(username, password)
    except Exception as e:
        print(e)
        response.body = str(e)
        response.status = 500
    return response


# Create user, returns user_id
@put('/student/<username>/create/<password>')
def create_user(username, password):
    try:
        response.body, response.status = authentication_helper.create_new_user(username, password)
    except Exception as e:
        response.body = str(e)
        response.status = 500
    return response


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
