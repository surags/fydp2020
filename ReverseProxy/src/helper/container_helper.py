import json
from io import BytesIO

import peewee
import requests

from bottle import response
from src.helper import session_helper
from src.model.os_container import OSContainer
from src.model.base_model import db
session_helper = session_helper.factory.get_session_helper()


class ContainerHelper:
    def __init__(self):
        pass

    def get_screenshot(self, user_id):
        user_session = session_helper.get_session_for_user(user_id)
        screenshot_response = requests.get("http://{0}:9090/screen/snapshot".format(user_session.destination_ip))
        return BytesIO(screenshot_response.content)

    def cleanup_user_session(self, user_id):
        user_session = session_helper.get_session_for_user(user_id)
        url = 'http://{0}:9090/user/remove'.format(user_session.destination_ip)
        requests.post(url)

    @db.connection_context()
    def available_vm_list(self):
        availablevm = (OSContainer.select(OSContainer.os_type.alias('os_type'), peewee.fn.COUNT('*').alias('count')).where(
            (OSContainer.is_free == True) & (OSContainer.is_running == True)).group_by(OSContainer.os_type).dicts())

        # for row in result_count:
        #     availablevm[row['os_type']] = row['count']

        response.body = json.dumps(list(availablevm))
        response.status = 200
        return response