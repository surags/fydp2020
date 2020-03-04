from time import sleep
from queue import Queue

from src.helper import router
from src.helper import container_helper
from src.helper import authentication_helper
from src.helper import user_helper
from src.helper import broadcast_helper
from src.helper import session_helper

from src.wsgi import app
from bottle import response, request
from bottle import post, get, put, delete
from src.model import base_model
from src.model.broadcast_states import BroadcastStates

import json

router = router.factory.get_router()
authentication_helper = authentication_helper.factory.get_authentication_helper()
user_helper = user_helper.Factory().get_user_helper()
container_helper = container_helper.ContainerHelper()
broadcast_helper = broadcast_helper.factory.get_broadcast_helper()
session_helper = session_helper.factory.get_session_helper()
db = base_model.db

# A test call to determine if the API is working
@get('/test')
def test_call():
    return [b"This is a test call"]


# A test call to determine if the API is working
@get('/')
def listing_handler():
    return [b"Hello"]


# Setup routes for the user.
# client_ip: Should be the public ipv4 of the client
# os_type: Should be either 'Windows' or 'Linux'
# user_id: The unique identifier for the user
# width: Screen width
# height: Screen height
@get('/routes/setup/<user_id>/<client_ip>/<os_type>/<width>/<height>')
@app.auth.verify_request(scopes=['studentTeacherStreamingOS'])
def setup_routes(user_id, client_ip, os_type, width, height):
    return router.setup_routes(user_id, client_ip, os_type, width, height)


# Deletes routes for user
# user_id: The unique identifier for the user
@get('/routes/delete/<user_id>')
@app.auth.verify_request(scopes=['studentTeacherStreamingOS'])
def delete_routes(user_id):
    router.delete_routes(user_id)
    response.status = 200
    return response


# Create user, returns user_id
# username: The unique username for the user
# password: The unique password for the user
@put('/user/<username>/create/<password>')
def create_user(username, password):
    return authentication_helper.create_new_user(username, password, request.params)


# Delete user
# user_id: The unique identifier for the user
@delete('/user/<user_id>/delete')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def delete_user(user_id):
    return authentication_helper.delete_user(user_id)


# Get info about a user
# user_id: The unique identifier for the user
@get('/user/<user_id>/screen/snapshot')
#@app.auth.verify_request(scopes=['teacherStreamingOS'])
def get_screen_snapshot(user_id):
    buffer_image = container_helper.get_screenshot(user_id)
    response.set_header('Content-type', 'image/jpeg')
    return buffer_image.read()


# Broadcast teacher session
# user_id: User ID of the teacher broadcasting
@put('/broadcast/<user_id>')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def broadcast_session(user_id):
    # Disable health checks
    session_helper.update_all_health_checks(False)
    #Keep user health check going
    session_helper.update_health_check(user_id, True)
    start_broadcast_event = BroadcastStates.START
    start_broadcast_event.value["broadcast_id"] = user_id
    broadcast_helper.broadcast_session_state = start_broadcast_event
    broadcast_helper.add_message_for_all(start_broadcast_event.value)
    response.status = 200


# Stop broadcast of the teacher session
@put('/broadcast/stop')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def stop_broadcast_session():
    message = BroadcastStates.STOP.value
    message["broadcast_id"] = broadcast_helper.broadcast_session_state.value["broadcast_id"]
    broadcast_helper.broadcast_session_state = BroadcastStates.STOP
    broadcast_helper.add_message_for_all(message)
    response.status = 200


# Notify students with a message
@put('/broadcast/message/<username>/<data>')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def message_clients(username, data):
    user_id = user_helper.get_userid_for_username(username)
    if user_id is None:
        return
    print(user_id)
    message = {"eventType": "notification_message", "message_data": data}
    broadcast_helper.add_message_for_user(user_id, message)
    # TODO Add code to verify send to all connected clients
    response.status = 200


# Subscribe to Broadcast Event Stream
@get('/subscribe/<user_id>')
@app.auth.verify_request(scopes=['studentTeacherStreamingOS'])
def subscribe(user_id):
    response.content_type  = 'text/event-stream'
    response.cache_control = 'no-cache'

    broadcast_helper.broadcast_message_queues[user_id] = Queue()

    # Set client-side auto-reconnect timeout, ms.
    yield 'retry: 100\n\n'

    # Keep client subscribed indefinitely
    while True:
        events_values = list()
        events_json = dict()


        # Add broadcast information
        if broadcast_helper.broadcast_session_state is BroadcastStates.START:
            events_values.append(broadcast_helper.broadcast_session_state.value)
            if not broadcast_helper.broadcast_message_queues[user_id].empty():
                message = broadcast_helper.broadcast_message_queues[user_id].get(block=False)
                events_values.append(message)
            events_json["events"] = events_values
            yield "data: {}\n\n".format(json.dumps(events_json))
            sleep(10)
            continue
        else:
            message = broadcast_helper.broadcast_message_queues[user_id].get(block=True)
            events_values.append(message)

        # if broadcast_helper.broadcast is BroadcastStates.STOP_BROADCAST:
        #     stop_broadcast_event = BroadcastStates.STOP_BROADCAST.value
        #     stop_broadcast_event["broadcast_id"] = broadcast_helper.broadcast["broadcast_id"]
        #     events_values.append(stop_broadcast_event)
        #
        # # Add messages
        # if broadcast_helper.message is not None:
        #     event_message["data"] = broadcast_helper.message
        #     events_values.append(event_message)

        # Send events to subscribed clients
        events_json["events"] = events_values
        yield "data: {}\n\n".format(json.dumps(events_json))



# Setup routes for the user.
# client_ip: Should be the public ipv4 of the client
# os_type: Should be either 'Windows' or 'Linux'
# user_id: The unique identifier for the user
@get('/setup/stream/<user_id>/<client_ip>/<broadcast_id>')
@app.auth.verify_request(scopes=['studentTeacherStreamingOS'])
def setup_stream(user_id, client_ip, broadcast_id):
    return router.setup_stream_routes(user_id, client_ip, str(broadcast_id))


# Stop broadcast streaming and restore user session stream (if it exists)
@get('/restore/stream/<user_id>')
@app.auth.verify_request(scopes=['studentTeacherStreamingOS'])
def restore_stream(user_id):
    # cleanup broadcast routes
    router.delete_stream_routes(user_id)
    current_session = router.get_session(user_id)
    # Check if a current session exists
    if current_session is not None:
        # All user data should exist in session helper
        response.body = json.dumps({'routes': current_session})
        response.status = 200
    else:
        response.status = 204
    return response

@get('/restore/stream/healthcheck/<user_id>')
def restore_stream_health_check(user_id):
    session_helper.update_health_check(user_id, True)

# Get info about a user
# username: The unique username for the user
@get('/user/<username>/info')
@app.auth.verify_request(scopes=['studentTeacherStreamingOS'])
def user_info(username):
    return user_helper.user_info(username)


# Get info about a user
# username: The unique username for the user
@get('/user/<username>/scope')
def user_scope(username):
    return user_helper.user_scope(username)


# Get a list of all the students in the school specified
# school_id: The unique identifier for the school
@get('/school/<school_id>/studentlist')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def student_list(school_id):
    return user_helper.student_list(school_id)


# Get a list of all applications supported
@get('/applications')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def application_list():
    return user_helper.application_list()

# Get a list of all users that have an active session
# Note that every time the ReverseProxy container is built,
# the sessions must be recreated/freed in the DB and then the
# setup_routes endpoint must be called to add the user to the
# session. Then the call will work :)
@get('/sessions')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def session_list():
    response.body = user_helper.session_list()
    response.status = 200
    return response


# Get the list of permitted applications for a student
# user_id: The unique identifier for the user
@get('/user/<user_id>/applications')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def permitted_apps(user_id):
    return user_helper.permitted_apps(user_id)


# Give access to a user for an application
# user_id: The unique identifier for the user
# application_id: The unique identifier for the application
@put('/user/<user_id>/grant/<application_id>')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def give_access(user_id, application_id):
    return user_helper.give_access(user_id, application_id)


# Revoke access to a user for an application
# user_id: The unique identifier for the user
# application_id: The unique identifier for the application
@delete('/user/<user_id>/revoke/<application_id>')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def revoke_access(user_id, application_id):
    return user_helper.revoke_access(user_id, application_id)


# Generates an OAuth2.0 token for the user
# This requires a few fields in the body set as x-www-form-urlencoded. Also requires the following Content-Type header: application/x-www-form-urlencoded
# client_id: The client type (i.e. teacher or student)
# grant_type: The grant type. Only one supported right now which is 'password'
# username: The unique username for the user
# password: The password for the user
# scope: Scopes define what you are requesting access to with the token (i.e. teacherStreamingOS, studentStreamingOS, studentAndTeacherStreamingOS)
@post('/token')
@app.auth.create_token_response()
def generate_token():
    pass


# Test call for authenticating
# username: The unique username for the user
# password: The password for the user
@get('/user/<username>/auth/<password>')
def auth_user(username, password):
    if authentication_helper.validate_user(username, password):
        response.body = "Yay we're authenticated"
        response.status = 200
    else:
        response.body = "OoPs SoMeThInG wEnT wRoNg"
        response.status = 418
    return response

# Get a list of all the students in the school specified
# school_id: The unique identifier for the school
@get('/availableVM')
@app.auth.verify_request(scopes=['studentTeacherStreamingOS'])
def available_vm_list():
    return container_helper.available_vm_list()
