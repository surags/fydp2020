import subprocess
import requests
import uwsgi as uwsgi

from threading import Lock
from src.model.os_container import OSContainer


class OSContainerInfoManager:
    def __init__(self):
        self.os_type = ""
        if uwsgi.opt["is_ubuntu"].decode("utf-8") == "True":
            self.os_type = "Linux"
        else:
            self.os_type = "Windows"
        self.ip_address = self.initialize_container_ip_address()
        self.is_running = True
        self.is_free = True

    def initialize_container_ip_address(self):
        if not bool(uwsgi.opt["is_azure"].decode("utf-8")):
            process = subprocess.Popen("grep \"$HOSTNAME\" /etc/hosts|awk '{print $1}'", stdout=subprocess.PIPE, shell=True)
            ip_address = process.communicate()[0].strip().decode('utf-8')
        else:
            ip_address = requests.get(
                "http://169.254.169.254/metadata/instance/network/interface/0/ipv4/ipAddress/0/privateIpAddress?api-version=2017-04-02&format=text",
                headers={"Metadata": "true"}).content
        self.setup_os_container_info_in_db(ip_address)
        return ip_address

    def setup_os_container_info_in_db(self, os_container_ip):
        try:
            container = OSContainer()
            container.is_free = True
            container.is_running = True
            container.ip_address = os_container_ip
            container.os_type = self.os_type
            container.save(force_insert=True)
        except Exception as e:
            print("Failed to save container info on startup")
            print(e)
            pass


class Factory:
    def __init__(self):
        self.os_container_info_manager = None
        self.lock = Lock()

    def get_os_container_info_manager(self):
        with self.lock:
            if self.os_container_info_manager is not None:
                return self.os_container_info_manager
            else:
                self.os_container_info_manager = OSContainerInfoManager()
                return self.os_container_info_manager

    def reset_os_container_info_manager(self):
        with self.lock:
            self.os_container_info_manager = OSContainerInfoManager()

factory = Factory()