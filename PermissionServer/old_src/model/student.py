from .base_model import BaseModel
from .users import Users
import peewee


class Student(BaseModel):
    student_id = peewee.AutoField(primary_key=True)
    user_id = peewee.ForeignKeyField(Users, field='user_id')
    has_system_access = peewee.BooleanField()
