import bottle
from src import routes
from src.helper import database_intializer_helper

app = application = bottle.default_app()
db_init = database_intializer_helper.DatabaseInitializer()

if __name__ == '__main__':
    bottle.run(host = '127.0.0.1', port = 8000)
