import json

from peewee import JOIN

from src.helper import authentication_helper
from src.helper import response_format_helper
from src.model.application import Application
from src.model.application_permissions import ApplicationPermission
from src.model.school import School
from src.model.users import Users
from src.wsgi import app
from bottle import response, request
from bottle import post, get, put, delete

from src.helper import router

router = router.Factory().get_router()
authentication_helper = authentication_helper.Factory().get_authentication_helper()
response_format_helper = response_format_helper.Factory().get_response_format_helper()


@get('/test')
def test_call():
    return [b"This is a test call"]


@get('/')
def listing_handler():
    return [b"Hello"]


@get('/routes/start/<user_id>')
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


@get('/routes/delete/<user_id>')
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
@delete('/user/<user_id>/delete')
def delete_user(user_id):
    try:
        response.body, response.status = authentication_helper.delete_user(user_id)
    except Exception as e:
        response.body = str(e)
        response.status = 500
    return response


# Get info about a user
@get('/user/<user_id>/info')
def user_info(user_id):
    try:
        join_condition = Users.school_id == School.school_id
        query = Users.select(Users, School.school_name).join(School, JOIN.LEFT_OUTER, on=join_condition).where(Users.user_id == user_id).dicts()
        response.body = json.dumps({'student': list(query)}, default=response_format_helper.to_serializable)
        response.status = 200
    except Exception as e:
        print(e)
        response.body = "Error: User does not exist"
        response.status = 400
    return response


# Get a list of all the students in the school specified
@get('/school/<school_id>/studentlist')
def student_list(school_id):
    query = Users.select(Users.user_id, Users.first_name, Users.last_name).where(Users.user_type == "Student" and Users.school_id == school_id).dicts()
    response.body = json.dumps({'students': list(query)})
    response.status = 200
    return response

# Get the list of permitted applications for a student
@get('/user/<user_id>/applications')
def student_list(user_id):
    join_condition = ApplicationPermission.application_id == Application.application_id
    query = ApplicationPermission.select(Application.application_name).join(Application, JOIN.INNER, on=join_condition).where(ApplicationPermission.user_id == user_id).dicts()
    response.body = json.dumps({'applications': list(query)})
    response.status = 200
    return response


@post('/token')
@app.auth.create_token_response()
def generate_token():
    pass

