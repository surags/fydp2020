import bottle
from bottle_oauthlib.oauth2 import BottleOAuth2
from oauthlib import oauth2
# Do not remove this important statement! Otherwise routes cannot be found
from src import routes

from src.helper import database_intializer_helper
from src.authentication.oauth2_password_validator import OAuth2_PasswordValidator
from src.helper.database_data_initializer import DatabaseDataInitializer

app = application = bottle.default_app()
db_init = database_intializer_helper.DatabaseInitializer()
db_data_init = DatabaseDataInitializer()

validator = OAuth2_PasswordValidator()
app.auth = BottleOAuth2(app)
app.auth.initialize(oauth2.LegacyApplicationServer(OAuth2_PasswordValidator()))

if __name__ == '__main__':
    bottle.run(host='127.0.0.1', port=8000, server=bottle.GeventServer)
