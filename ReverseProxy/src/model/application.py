from .base_model import BaseModel
import peewee

class Application(BaseModel):
    application_id = peewee.AutoField(primary_key=True)
    application_name = peewee.CharField()
