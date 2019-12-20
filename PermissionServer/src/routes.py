import json

import bottle

from src.wsgi import app
from bottle import response
from bottle import post, get, put
from bottle import static_file
from src.helper import application_permission_helper
from src.helper import snapshot_helper
from src.manager import os_container_info_manager
from src.manager import user_info_manager

permission_helper = application_permission_helper.factory.get_application_permissions_helper()
snapshot_helper = snapshot_helper.factory.get_snapshot_helper()
container_info_manager = os_container_info_manager.factory.get_os_container_info_manager()
user_info_manager = user_info_manager.factory.get_user_info_manager()

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

@post('/user/remove')
def remove_user():
    user_info_manager.user_id = ""
    response.body = "Success"
    response.status = 200
    return response

@post('/application/permission/remove/<application_id>')
def remove_application_permission(application_id):
    permission_helper.remove_permission(application_id)
    response.body = "Success"
    response.status = 200
    return response


@get('/screen/snapshot')
def get_latest_snapshot():
    return static_file(snapshot_helper.get_latest_snapshot(), root='snapshots')


@get('/health/check')
def health_check():
    response_body = {
        'user_id' : user_info_manager.user_id,
        'is_free' : container_info_manager.is_free
    }
    response.status = 200
    response.content_type = 'application/json'
    return json.dumps(response_body)
