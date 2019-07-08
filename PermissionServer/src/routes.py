import bottle

from src.wsgi import app
from bottle import response
from bottle import post, get, put
from src.helper import application_permission_helper

permission_helper = application_permission_helper.Factory().get_application_permissions_helper()

@get('/')
def listing_handler():
    return [b"Hello"]

@get('/application/permission/add/<application_id>')
def listing_handler(application_id):
    permission_helper.add_permission(application_id)
    return [b"Hello"]

@get('/setup/user/<user_id>')
def listing_handler(user_id):
    permission_helper.setup_user(user_id)
    return [b"Hello"]

@get('/application/permission/remove/<application_id>')
def listing_handler(application_id):
    permission_helper.remove_permission(application_id)
    return [b"Hello"]
