from .base_model import BaseModel
import peewee

class OSContainer(BaseModel):
    container_id = peewee.AutoField(primary_key=True)
    docker_container_id = peewee.CharField()
    ip_address = peewee.CharField(unique=True)
    is_free = peewee.BooleanField()
    is_running = peewee.BooleanField()
