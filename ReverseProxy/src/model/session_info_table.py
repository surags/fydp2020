from .base_model import BaseModel
from .users import Users
from .os_container import OSContainer
from .device import Device
import peewee

class SessionInfo(BaseModel):
    session_id = peewee.AutoField(primary_key=True)
    user_id = peewee.ForeignKeyField(Users, field='user_id')
    ip_address = peewee.ForeignKeyField(OSContainer, field='ip_address')
    device_id = peewee.ForeignKeyField(Device, field='device_id')
    has_system_access = peewee.BooleanField()
