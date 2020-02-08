import subprocess
import psutil as psutil
import uwsgi




class VNCHelper:

    def __init__(self):
        pass

    def cleanup_vnc_server(self):
        if uwsgi.opt["is_ubuntu"].decode("utf-8") == "True":
            subprocess.Popen("vncserver -kill :1", stdout=subprocess.PIPE, shell=True)
        else:
            subprocess.Popen("echo yes | cmd.exe /c rwinsta rdp-tcp", stdout=subprocess.PIPE, shell=True)

    def start_vnc_server(self, width, height):
        if uwsgi.opt["is_ubuntu"].decode("utf-8") == "True":
            subprocess.Popen("sudo -u fydp-root vncserver -geometry {0}x{1}".format(width, height),
                             stdout=subprocess.PIPE, shell=True)
        # else:
        #     subprocess.Popen("/mnt/c/'Program Files'/RealVNC/'VNC Server'/vncserver.exe -service -start", stdout=subprocess.PIPE, shell=True)


    def getProcessPIDs(self, process_name):
        '''
        Check if there is any running process(es) that contains the given name processName and returns its PID(s),
        '''
        pids = []
        #Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if process_name.lower() in ''.join(proc.cmdline()).lower():
                    print("Exists: {0}".format(proc.pid))
                    pids.append(proc.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                print("ERROR")
                pass
        return pids