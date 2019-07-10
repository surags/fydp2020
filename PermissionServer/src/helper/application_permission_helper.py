import subprocess
from threading import Lock

from peewee import JOIN

from src.model.application import Application
from src.model.application_permissions import ApplicationPermission

from src.model.os_container import OSContainer


class ApplicationPermissionHelper:
    def __init__(self):
        process = subprocess.Popen("grep \"$HOSTNAME\" /etc/hosts|awk '{print $1}'", stdout=subprocess.PIPE, shell=True)
        self.os_container_ip = process.communicate()[0].strip().decode('utf-8')
        self.setup_os_container_info(self.os_container_ip)
        self.user_id = ""

    def remove_permissions(self):
        join_condition = Application.application_id == ApplicationPermission.application_id and ApplicationPermission.user_id == self.user_id
        application_permissions_info = Application.select(Application, ApplicationPermission)\
            .join(ApplicationPermission, JOIN.LEFT_OUTER, on=join_condition).objects()

        for permissions_info in application_permissions_info:
            if permissions_info.user_id:
                self.add_permission(permissions_info.application_id)
            else:
                self.remove_permission(permissions_info.application_id)

    def setup_user(self, user_id):
        self.user_id = user_id
        self.remove_permissions()

    def add_permission(self, application_id):
        application_info = Application.get(Application.application_id == application_id)
        subprocess.Popen("chmod -R +x /usr/lib/{0}".format(application_info.application_name), stdout=subprocess.PIPE,
                         shell=True)

    def remove_permission(self, application_id):
        application_info = Application.get(Application.application_id == application_id)
        subprocess.Popen("chmod -R -x /usr/lib/{0}".format(application_info.application_name), stdout=subprocess.PIPE,
                         shell=True)

    def setup_os_container_info(self, os_container_ip):
        try:
            container = OSContainer()
            container.is_free = True
            container.is_running = True
            container.ip_address = os_container_ip
            container.docker_container_id = "FAKEID-123"
            container.save()
        except:
            pass


class Factory:
    application_permission_helper = None
    lock = Lock()

    def get_application_permissions_helper(self):
        with self.lock:
            if self.application_permission_helper is not None:
                return self.application_permission_helper
            else:
                self.application_permission_helper = ApplicationPermissionHelper()
                return self.application_permission_helper

    def reset_router(self):
        with self.lock:
            self.application_permission_helper = ApplicationPermissionHelper()
