import subprocess

from timeloop import Timeloop
from datetime import timedelta
from threading import Lock

from src.manager import os_container_info_manager
from src.manager import user_info_manager
from src.model.os_container import OSContainer

tl = Timeloop()
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600
SNAPSHOT_FILE_NAME = "snapshot.jpeg"
container_info_manager = os_container_info_manager.factory.get_os_container_info_manager()
user_info_manager = user_info_manager.factory.get_user_info_manager()


class SnapshotHelper:
    def __init__(self):
        pass

    def initialize_timeloop(self):
        tl.start(block=True)

    def get_latest_snapshot(self):
        return SNAPSHOT_FILE_NAME


@tl.job(interval=timedelta(seconds=5))
def snapshot_with_repeating_interval():
    subprocess.Popen("vncsnapshot -passwd ~/.vnc/passwd -rect 0x0-{0}-{1} :1 ~/PermissionServer/src/snapshots/snapshot.jpeg".format(IMAGE_WIDTH, IMAGE_HEIGHT),
                     stdout=subprocess.PIPE, shell=True)


@tl.job(interval=timedelta(seconds=10))
def check_vnc_connection_with_repeating_interval():
    process = subprocess.Popen("netstat -an | grep \"ESTABLISHED\" | grep \":5901\"",
                               stdout=subprocess.PIPE, shell=True)
    if not process.communicate()[0].strip():
        if not container_info_manager.is_free:
            container = OSContainer()
            container.ip_address = container_info_manager.ip_address
            container.is_free = True
            container.save()
            container_info_manager.is_free = True
    else:
        if container_info_manager.is_free:
            container_info_manager.is_free = False


class Factory:
    snapshot_helper = None
    lock = Lock()

    def get_snapshot_helper(self):
        with self.lock:
            if self.snapshot_helper is not None:
                return self.snapshot_helper
            else:
                self.snapshot_helper = SnapshotHelper()
                return self.snapshot_helper

    def reset_snapshot_helper(self):
        with self.lock:
            self.snapshot_helper = SnapshotHelper()


factory = Factory()
