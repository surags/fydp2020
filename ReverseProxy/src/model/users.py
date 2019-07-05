from src.model.user_type import UserType
from .base_model import BaseModel
import datetime
import peewee

class Users(BaseModel):
    user_id = peewee.AutoField(primary_key=True)
    school_id = peewee.CharField(unique=True)
    user_name = peewee.CharField(unique=True)
    user_type = peewee.ForeignKeyField(UserType, field='user_type')
    hashed_password = peewee.CharField()
    registration_date = peewee.DateTimeField(default=datetime.datetime.now())
    first_name = peewee.CharField()
    last_name = peewee.CharField()
    email = peewee.CharField(unique=True)
