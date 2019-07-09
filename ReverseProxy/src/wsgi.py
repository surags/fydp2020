import bottle
from bottle_oauthlib.oauth2 import BottleOAuth2
from oauthlib import oauth2

from src.helper import database_intializer_helper, database_data_initializer
from src.authentication.oauth2_password_validator import OAuth2_PasswordValidator

app = application = bottle.default_app()
db_init = database_intializer_helper.DatabaseInitializer()
db_data_init = database_data_initializer.DatabaseDataInitializer()

validator = OAuth2_PasswordValidator()
app.auth = BottleOAuth2(app)
app.auth.initialize(oauth2.LegacyApplicationServer(OAuth2_PasswordValidator()))

if __name__ == '__main__':
    bottle.run(host='127.0.0.1', port=8000)
