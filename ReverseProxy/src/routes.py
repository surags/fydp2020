from functools import singledispatch
from datetime import datetime

import bottle
import json

from peewee import JOIN

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
        join_condition = Users.school_id == School.school_id
        query = Users.select(Users, School.school_name).join(School, JOIN.LEFT_OUTER, on=join_condition).where(Users.user_name == username).dicts()
        response.body = json.dumps({'student': list(query)}, default=to_serializable)
        response.status = 200
    except Exception as e:
        print(e)
        response.body = "Error: User does not exist"
        response.status = 400
    return response


# Get a list of all the students
@get('/user/studentlist')
def student_list():
    query = Users.select(Users.user_id, Users.first_name, Users.last_name).where(Users.user_type == "Student").dicts()
    response.body = json.dumps({'students': list(query)})
    response.status = 200
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
