import json

from src.helper import authentication_helper
from src.helper import user_helper
from src.wsgi import app
from bottle import response, request
from bottle import post, get, put, delete

from src.helper import router

router = router.Factory().get_router()
authentication_helper = authentication_helper.Factory().get_authentication_helper()
user_helper = user_helper.Factory().get_user_helper()


@get('/test')
def test_call():
    return [b"This is a test call"]


@get('/')
def listing_handler():
    return [b"Hello"]


@get('/routes/start/<user_id>')
def setup_routes(user_id):
    return router.setup_routes(user_id)


# Deletes routes for user
@get('/routes/delete/<user_id>')
def delete_routes(user_id):
    return router.delete_iptable_rules(user_id)


# Create user, returns user_id
@put('/user/<username>/create/<password>')
def create_user(username, password):
    return authentication_helper.create_new_user(username, password, request.params)


# Delete user
@delete('/user/<user_id>/delete')
def delete_user(user_id):
    return authentication_helper.delete_user(user_id)


# Get info about a user
@get('/user/<user_id>/info')
def user_info(user_id):
    return user_helper.user_info(user_id)


# Get a list of all the students in the school specified
@get('/school/<school_id>/studentlist')
def student_list(school_id):
    return user_helper.student_list(school_id)


# Get a list of all applications supported
@get('/applications')
def application_list():
    return user_helper.application_list()


# Get the list of permitted applications for a student
@get('/user/<user_id>/applications')
def permitted_apps(user_id):
    return user_helper.permitted_apps(user_id)


# Give access to a user for an application
@put('/user/<user_id>/grant/<application_id>')
def give_access(user_id, application_id):
    return user_helper.give_access(user_id, application_id)


# Revoke access to a user for an application
@delete('/user/<user_id>/revoke/<application_id>')
def revoke_access(user_id, application_id):
    return user_helper.revoke_access(user_id, application_id)


@post('/token')
@app.auth.create_token_response()
def generate_token():
    pass

