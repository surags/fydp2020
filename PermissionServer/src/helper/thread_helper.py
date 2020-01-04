import os
import subprocess
import uwsgi

from time import sleep
from threading import Lock
from src.manager import os_container_info_manager
from src.manager import user_info_manager

SNAPSHOT_FILE_NAME = "snapshot.jpg"
container_info_manager = os_container_info_manager.factory.get_os_container_info_manager()
user_info_manager = user_info_manager.factory.get_user_info_manager()
project_root = os.path.dirname(os.path.dirname(__file__))


class ThreadHelper:
    def __init__(self):
        self.enabled = False
        pass

    def get_latest_snapshot(self):
        return SNAPSHOT_FILE_NAME

    def snapshot_with_repeating_interval(self):
        while self.enabled:
            subprocess.Popen(
                "vncsnapshot -passwd ~/.vnc/passwd -quality 50 :1 {0}/snapshots/snapshot.jpg".format(project_root),
                stdout=subprocess.PIPE, shell=True)
            sleep(5)

    def check_vnc_connection_with_repeating_interval(self):
        while self.enabled:
            if uwsgi.opt["is_ubuntu"].decode("utf-8") == "True":
                process = subprocess.Popen("netstat -an | grep \"ESTABLISHED\" | grep \":5901\"",
                                           stdout=subprocess.PIPE, shell=True)
            else:
                process = subprocess.Popen("cmd.exe /c netstat -an | grep \"ESTABLISHED\" | grep \":5901\"",
                                           stdout=subprocess.PIPE, shell=True)
            if not process.communicate()[0].strip():
                if not container_info_manager.is_free:
                    container_info_manager.is_free = True
                    print("True")
            else:
                if container_info_manager.is_free:
                    container_info_manager.is_free = False
                    print("False")
            sleep(10)


class Factory:
    thread_helper = None
    lock = Lock()

    def get_thread_helper(self):
        with self.lock:
            if self.thread_helper is not None:
                return self.thread_helper
            else:
                self.thread_helper = ThreadHelper()
                return self.thread_helper

    def reset_thread_helper(self):
        with self.lock:
            self.thread_helper = ThreadHelper()


factory = Factory()
