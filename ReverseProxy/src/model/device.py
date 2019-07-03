from .base_model import BaseModel
import peewee

class Device(BaseModel):
    device_id = peewee.AutoField(primary_key=True)
    ip_address = peewee.CharField()
    mac_address = peewee.CharField()
