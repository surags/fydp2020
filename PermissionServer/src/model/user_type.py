from .base_model import BaseModel
import peewee


class UserType(BaseModel):
    user_type = peewee.CharField(unique=True)
