from .base_model import BaseModel
import peewee


class OSContainer(BaseModel):
    ip_address = peewee.CharField(primary_key=True)
    is_free = peewee.BooleanField()
    is_running = peewee.BooleanField()
