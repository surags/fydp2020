from .base_model import BaseModel
import peewee


class OSContainer(BaseModel):
    ip_address = peewee.CharField(primary_key=True)
    is_free = peewee.BooleanField()
    is_running = peewee.BooleanField()
    guacamole_stream_id = peewee.CharField()
    guacamole_view_only_id = peewee.CharField()
    os_type = peewee.CharField()
