import subprocess
import requests
import uwsgi
from threading import Lock

from peewee import JOIN

from src.model.application import Application
from src.model.application_permissions import ApplicationPermission

from src.model.os_container import OSContainer
from src.manager import os_container_info_manager
from src.manager import user_info_manager

container_info_manager = os_container_info_manager.factory.get_os_container_info_manager()
user_info_manager = user_info_manager.factory.get_user_info_manager()


class ApplicationPermissionHelper:
    def __init__(self):
        pass

    def remove_permissions(self):
        join_condition = Application.application_id == ApplicationPermission.application_id and ApplicationPermission.user_id == user_info_manager.user_id
        application_permissions_info = Application.select(Application, ApplicationPermission)\
            .join(ApplicationPermission, JOIN.LEFT_OUTER, on=join_condition).objects()

        for permissions_info in application_permissions_info:
            if permissions_info.user_id:
                self.add_permission(permissions_info.application_id)
            else:
                self.remove_permission(permissions_info.application_id)

    def setup_user(self, user_id):
        user_info_manager.user_id = user_id
        self.remove_permissions()
        container_info_manager.is_free = False

    def add_permission(self, application_id):
        application_info = Application.get(Application.application_id == application_id)
        subprocess.Popen("chmod -R +x /usr/lib/{0}".format(application_info.application_name), stdout=subprocess.PIPE,
                         shell=True)

    def remove_permission(self, application_id):
        application_info = Application.get(Application.application_id == application_id)
        subprocess.Popen("chmod -R -x /usr/lib/{0}".format(application_info.application_name), stdout=subprocess.PIPE,
                         shell=True)


class Factory:
    def __init__(self):
        self.application_permission_helper = None
        self.lock = Lock()

    def get_application_permissions_helper(self):
        with self.lock:
            if self.application_permission_helper is not None:
                return self.application_permission_helper
            else:
                self.application_permission_helper = ApplicationPermissionHelper()
                return self.application_permission_helper

    def reset_application_permissions_helper(self):
        with self.lock:
            self.application_permission_helper = ApplicationPermissionHelper()

factory = Factory()