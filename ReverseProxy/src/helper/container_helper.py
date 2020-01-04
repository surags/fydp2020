from io import BytesIO
from src.helper import session_helper
import requests


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