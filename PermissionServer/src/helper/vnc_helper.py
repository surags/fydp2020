import os
import subprocess
from time import sleep

import uwsgi


class VNCHelper:

    def __init__(self):
        pass

    def cleanup_vnc_server(self):
        if uwsgi.opt["is_ubuntu"].decode("utf-8") == "True":
            subprocess.Popen("vncserver -kill :1", stdout=subprocess.PIPE, shell=True)
        else:
            subprocess.Popen("winvnc.exe -stopservice", stdout=subprocess.PIPE, shell=True)

    def start_vnc_server(self, width, height):
        if uwsgi.opt["is_ubuntu"].decode("utf-8") == "True":
            subprocess.Popen("sudo -u fydp-root vncserver -geometry {0}x{1}".format(width, height),
                             stdout=subprocess.PIPE, shell=True)
        else:
            subprocess.Popen("winvnc.exe -startservice", stdout=subprocess.PIPE, shell=True)
