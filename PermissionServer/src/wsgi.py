import bottle

from src.helper import database_intializer_helper
from src.helper.application_permission_helper import ApplicationPermissionHelper
from src import routes

app = application = bottle.default_app()
db_init = database_intializer_helper.DatabaseInitializer()
app_permission_helper = ApplicationPermissionHelper()

if __name__ == '__main__':
    bottle.run(host='127.0.0.1', port=8000)
