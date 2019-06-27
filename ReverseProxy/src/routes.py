from bottle import request, response
from bottle import post, get, put, delete
from src.helper import router

router = router.Factory().get_router()

@get('/')
def listing_handler():
    return [b"Hello World"]

@get('/setup/routes/<user_id>')
def setup_routes(user_id):
    destination_ip = ""
    router.setup_routes(user_id, destination_ip)
    response.status = 200
    return

@get('/delete/routes/<user_id>')
def setup_routes(user_id):
    router.delete_iptable_rules(user_id)
    response.status = 200
    return