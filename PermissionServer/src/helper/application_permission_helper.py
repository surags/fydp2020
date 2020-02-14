import subprocess
import threading
import uwsgi
import uuid

from threading import Lock
from peewee import JOIN
from src.model.application import Application
from src.model.application_permissions import ApplicationPermission
from src.model.base_model import db
from src.manager import os_container_info_manager
from src.manager import user_info_manager
from src.helper import thread_helper

container_info_manager = os_container_info_manager.factory.get_os_container_info_manager()
user_info_manager = user_info_manager.factory.get_user_info_manager()
thread_helper = thread_helper.factory.get_thread_helper()


class ApplicationPermissionHelper:
    def __init__(self):
        pass

    @db.connection_context()
    def remove_permissions(self):
        join_condition = Application.application_id == ApplicationPermission.application_id and ApplicationPermission.user_id == user_info_manager.user_id
        application_permissions_info = Application.select(Application, ApplicationPermission)\
            .join(ApplicationPermission, JOIN.LEFT_OUTER, on=join_condition).objects()

        for permissions_info in application_permissions_info:
            print(permissions_info)
            if permissions_info.user_id:
                self.add_permission(permissions_info.application_id)
            else:
                self.remove_permission(permissions_info.application_id)

    def setup_user(self, user_id):
        user_info_manager.user_id = user_id
        self.remove_permissions()
        print("Permissions removed")
        container_info_manager.is_free = False
        snapshot_thread = threading.Thread(name='os_container_health_check', target=thread_helper.snapshot_with_repeating_interval)
        vnc_check_thread = threading.Thread(name='os_container_health_check', target=thread_helper.check_vnc_connection_with_repeating_interval)
        thread_helper.enabled = True
        snapshot_thread.start()
        vnc_check_thread.start()
        print("Setup user")

    def health_check(self, enable=True)
        global health_check
        health_check = enable

    @db.connection_context()
    def add_permission(self, application_id):
        application_info = Application.get(Application.application_id == application_id)
        if uwsgi.opt["is_ubuntu"].decode("utf-8") == "True":
            subprocess.Popen("chmod -R +x /usr/lib/{0}".format(application_info.application_name), stdout=subprocess.PIPE,
                            shell=True)
        else:
            file_name = self.generate_windows_regedit_file(application_info.application_name, True)
            subprocess.Popen("cd /mnt/c && cmd.exe /c REGEDIT /s {0} && rm {1}".format(file_name, file_name), stdout=subprocess.PIPE,
                            shell=True)

    @db.connection_context()
    def remove_permission(self, application_id):
        application_info = Application.get(Application.application_id == application_id)
        if uwsgi.opt["is_ubuntu"].decode("utf-8") == "True":
            subprocess.Popen("chmod -R -x /usr/lib/{0}".format(application_info.application_name), stdout=subprocess.PIPE,
                            shell=True)
        else:
            file_name = self.generate_windows_regedit_file(application_info.application_name, False)
            subprocess.Popen("cd /mnt/c && cmd.exe /c REGEDIT /s {0} && rm {1}".format(file_name, file_name), stdout=subprocess.PIPE,
                            shell=True)

    def generate_windows_regedit_file(self, application_name, should_add_permission):
        file_name = "{0}-permissions-{1}.reg".format(uuid.uuid4(), application_name)
        with open("/mnt/c/{0}".format(file_name), "w") as file:
            file.write("Windows Registry Editor Version 5.00\n")
            file.write("[HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\DisallowRun]\n")
            if should_add_permission:
                file.write("\"{0}\"=-".format(application_name))
            else:
                file.write("\"{0}\"=\"{1}\"".format(application_name, application_name))
        return file_name


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
