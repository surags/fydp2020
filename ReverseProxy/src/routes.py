from functools import singledispatch
from datetime import datetime

import bottle
import json

from src.helper import authentication_helper
from src.model.school import School
from src.model.users import Users
from src.wsgi import app
from bottle import response, request
from bottle import post, get, put, delete

from src.helper import router

router = router.Factory().get_router()
authentication_helper = authentication_helper.Factory().get_authentication_helper()


@get('/test')
def test_call():
    return [b"This is a test call"]


@get('/')
def listing_handler():
    return [b"Hello"]


@get('/setup/routes/<user_id>')
def setup_routes(user_id):
    try:
        source_port, container_ip = router.setup_routes(user_id)
        data = {}
        data['source_port'] = source_port
        data['container_ip'] = container_ip
        response.body = json.dumps(data)
        response.status = 200
    except Exception as e:
        print(e)
        response.status = 500
    return


@get('/delete/routes/<user_id>')
def delete_routes(user_id):
    router.delete_iptable_rules(user_id)
    response.status = 200
    return


# Create user, returns user_id
@put('/user/<username>/create/<password>')
def create_user(username, password):
    try:
        response.body, response.status = authentication_helper.create_new_user(username, password, request.params)
    except Exception as e:
        response.body = str(e)
        response.status = 500
    return response


# Delete user
@delete('/user/<username>/delete')
def delete_user(username):
    try:
        response.body, response.status = authentication_helper.delete_user(username)
    except Exception as e:
        response.body = str(e)
        response.status = 500
    return response


# Get info about a user
@get('/user/<username>/info')
def user_info(username):
    try:
        user = Users.get(Users.user_name == username)
        school = School.get(School.school_id == user.school_id)
        data = {}
        data['username'] = user.user_name
        data['user_id'] = user.user_id
        data['first_name'] = user.first_name
        data['last_name'] = user.last_name
        data['school_id'] = user.school_id
        data['email'] = user.email
        data['user_type'] = user.school_id  # TODO: Fix this
        data['school_name'] = school.school_name
        data['date_created'] = user.registration_date
        response.body = json.dumps(data, default=to_serializable)
        response.status = 200
    except Exception as e:
        print(e)
        response.body = "Error: User does not exist"
        response.status = 400
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


@singledispatch
def to_serializable(val):
    """Used by default."""
    return str(val)


@to_serializable.register(datetime)
def ts_datetime(val):
    """Used if *val* is an instance of datetime."""
    return val.isoformat() + "Z"
