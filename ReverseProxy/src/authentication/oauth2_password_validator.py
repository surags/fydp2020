from oauthlib import oauth2

from src.helper import authentication_helper
from src.model.user_type import UserType

authentication_helper = authentication_helper.Factory().get_authentication_helper()


class Client():
    client_id = None


class OAuth2_PasswordValidator(oauth2.RequestValidator):
    """dict of clients containing list of valid scopes"""
    clients_scopes = {
        "student": ["studentStreamingOS", "studentTeacherStreamingOS"],
        "teacher": ["teacherStreamingOS", "studentTeacherStreamingOS"]
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
        try:
            user_types = UserType().select().where(UserType.user_type == client_id)
            if user_types:
                request.client = Client()
                request.client.client_id = client_id
                return True
            else:
                return False
        except Exception as e:
            print(e)

    def validate_user(self, username, password, client, request, *args, **kwargs):
        if authentication_helper.validate_user(username, password):
            request.user = username
            return True
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

            scopes = info['scopes']
            for scope in scopes_required:
                if scope not in scopes:
                    return False
            return True
        return False
