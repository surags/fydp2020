import bottle
import uwsgi

from src.helper import database_intializer_helper
from src.helper import application_permission_helper
from src.helper import thread_helper
#DONT DELETE THE ROUTES IMPORT. WITHOUT IT OUR ROUTING WONT WORK
from src import routes

app = application = bottle.default_app()
db_init = database_intializer_helper.DatabaseInitializer()
app_permission_helper = application_permission_helper.factory.get_application_permissions_helper()


if __name__ == '__main__':
    bottle.run(host='127.0.0.1', port=8000)
