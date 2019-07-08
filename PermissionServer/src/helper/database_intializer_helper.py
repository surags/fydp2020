from src.model.base_model import BaseModel
from src.model.application import Application
from src.model.application_permissions import ApplicationPermission
from src.model.os_container import OSContainer
import peewee

db = peewee.MySQLDatabase(
    "streamingOS",
    host="db",
    port=3306,
    user="root",
    passwd="supersecret"
)


class DatabaseInitializer:
    def __init__(self):
        try:
            Application.create_table()
            ApplicationPermission.create_table()
            OSContainer.create_table()
        except peewee.InternalError as e:
            print(str(e))
