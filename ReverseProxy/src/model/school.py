from .base_model import BaseModel
import peewee

class School(BaseModel):
    school_id = peewee.AutoField(unique=True)
    school_name = peewee.CharField()
    primary_key = peewee.CompositeKey('school_id', 'school_name')
