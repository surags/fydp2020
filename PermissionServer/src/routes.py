import bottle

from src.wsgi import app
from bottle import response
from bottle import post, get, put
from src.helper import application_permission_helper

permission_helper = application_permission_helper.Factory().get_application_permissions_helper()


@get('/')
def listing_handler():
    return [b"Hello"]


@post('/application/permission/add/<application_id>')
def add_application_permission(application_id):
    permission_helper.add_permission(application_id)
    response.body = "Success"
    response.status = 200
    return response


@post('/user/setup/<user_id>')
def setup_user(user_id):
    permission_helper.setup_user(user_id)
    response.body = "Success"
    response.status = 200
    return response


@post('/application/permission/remove/<application_id>')
def remove_application_permission(application_id):
    permission_helper.remove_permission(application_id)
    response.body = "Success"
    response.status = 200
    return response

@get('/health/check')
def health_check():
    response.body = "OK"
    response.status = 200
    return response
