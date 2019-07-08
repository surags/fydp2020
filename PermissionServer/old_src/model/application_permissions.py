from .base_model import BaseModel
from .users import Users
from .application import Application

import peewee


class ApplicationPermission(BaseModel):
    user_id = peewee.ForeignKeyField(Users, field='user_id')
    application_id = peewee.ForeignKeyField(Application, field='application_id')
