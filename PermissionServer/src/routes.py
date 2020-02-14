import json
import os

from bottle import response
from bottle import post, get, put
from bottle import static_file
from src.helper import application_permission_helper
from src.helper import thread_helper
from src.helper import vnc_helper
from src.manager import os_container_info_manager
from src.manager import user_info_manager
from src.model import base_model

permission_helper = application_permission_helper.factory.get_application_permissions_helper()
thread_helper = thread_helper.factory.get_thread_helper()
container_info_manager = os_container_info_manager.factory.get_os_container_info_manager()
user_info_manager = user_info_manager.factory.get_user_info_manager()
vnc_helper = vnc_helper.VNCHelper()
db = base_model.db

@get('/')
def listing_handler():
    return [b"Hello"]


@post('/application/permission/add/<application_id>')
def add_application_permission(application_id):
    permission_helper.add_permission(application_id)
    response.body = "Success"
    response.status = 200
    return response


@post('/user/setup/<user_id>/<width>/<height>')
def setup_user(user_id, width, height):
    vnc_helper.start_vnc_server(width, height)
    permission_helper.setup_user(user_id)
    response.body = "Success"
    response.status = 200
    return response


@post('/user/remove')
def remove_user():
    vnc_helper.cleanup_vnc_server()
    user_info_manager.user_id = ""
    container_info_manager.is_free = True
    thread_helper.enabled = False
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
    project_root = os.path.dirname(os.path.dirname(__file__))
    print(project_root)
    return static_file(thread_helper.get_latest_snapshot(), root=os.path.join(os.path.dirname(__file__), 'snapshots'),
                       mimetype='image/jpg')


@get('/health/check')
def health_check():
    response_body = {
        'user_id' : user_info_manager.user_id,
        'is_free' : container_info_manager.is_free
    }
    response.status = 200
    response.content_type = 'application/json'
    return json.dumps(response_body)


@post('/health/disable')
def health_disable():
    permission_helper.health_check(enable=False)
    response.body = "Success"
    response.status = 200
    return response


@post('/health/enable')
def health_enable():
    permission_helper.health_check(enable=True)
    response.body = "Success"
    response.status = 200
    return response
