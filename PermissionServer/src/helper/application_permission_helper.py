import subprocess

from src.model.application import Application
from src.model.os_container import OSContainer


class ApplicationPermissionHelper:
    def __init__(self):
        process = subprocess.Popen("grep \"$HOSTNAME\" /etc/hosts|awk '{print $1}'", stdout=subprocess.PIPE, shell=True)
        self.os_container_ip = process.communicate()[0].strip().decode('utf-8')
        self.setup_os_container_info(self.os_container_ip)

    def add_permission(self, application_id):
        application_info = Application.get(Application.application_id == application_id)
        print(application_info[0].application_name)


    def remove_permission(self, application_id):
        application_info = Application.get(Application.application_id == application_id)
        print(application_info[0].application_name)


    def setup_os_container_info(self, os_container_ip):
        container = OSContainer()
        container.is_free = True
        container.is_running = True
        container.ip_address = os_container_ip
        container.docker_container_id = "FAKEID-123"
        container.save()
