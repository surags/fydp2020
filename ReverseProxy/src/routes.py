import bcrypt
import bottle
from bottle import request, response
from bottle import post, get, put, delete
from oauthlib import oauth2
from bottle_oauthlib.oauth2 import BottleOAuth2

from src.helper import router
from src.helper import authentication_helper

router = router.Factory().get_router()
authentication_helper = authentication_helper.Factory().get_authentication_helper()

class OAuth2_PasswordValidator(oauth2.RequestValidator):
    """dict of clients containing list of valid scopes"""
    clients_scopes = {
        "clientA": ["streamingOS"]
    }
    """dict of username containing password"""
    users_password = {
        "john": "doe",
        "foo": "bar"
    }
    tokens_info = {
    }

    def client_authentication_required(self, request, *args, **kwargs):
        return False  # Allow public clients

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        if self.clients_scopes.get(client_id):
            request.client = Client()
            request.client.client_id = client_id
            return True
        return False

    def validate_user(self, username, password, client, request, *args, **kwargs):
        if self.users_password.get(username):
            request.user = username
            return password == self.users_password.get(username)
        return False

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        return grant_type in ["password"]

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        return all(scope in self.clients_scopes.get(client_id) for scope in scopes)

    def save_bearer_token(self, token_response, request, *args, **kwargs):
        self.tokens_info[token_response["access_token"]] = {
            "client": request.client,
            "user": request.user,
            "scopes": request.scopes
        }

    def validate_bearer_token(self, access_token, scopes_required, request):
        info = self.tokens_info.get(access_token, None)
        if info:
            request.client = info["client"]
            request.user = info["user"]
            request.scopes = info["scopes"]
            return all(scope in request.scopes for scope in scopes_required)
        return False


validator = OAuth2_PasswordValidator()
server = oauth2.Server(validator)
app = bottle.Bottle()
app.auth = BottleOAuth2(app)
app.auth.initialize(server)


@get('/')
def listing_handler():
    return [b"Hello"]


@get('/setup/routes/<user_id>')
def setup_routes(user_id):
    router.setup_routes(user_id)
    response.status = 200
    return


@get('/delete/routes/<user_id>')
def setup_routes(user_id):
    router.delete_iptable_rules(user_id)
    response.status = 200
    return


# Authenticate user
@get('/student/<user_id>/auth/<password>')
def authenticate_user(user_id, password):
    try:
        response.body, response.status = authentication_helper.validate_user(user_id, password)
    except Exception as e:
        print(e)
        response.body = str(e)
        response.status = 500
    return


# Create user, returns user_id
@put('/student/<username>/create/<password>')
def create_user(username, password):
    try:
        response.body, response.status = authentication_helper.create_new_user(username, password)
    except Exception as e:
        response.body = str(e)
        response.status = 500
    return


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
