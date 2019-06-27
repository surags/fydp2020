import subprocess
from threading import Lock
from src.model import session_info


class Router:

    def __init__(self):
        process = subprocess.Popen("ip route show default | awk '/default/ {print $3}'", stdout=subprocess.PIPE,
                                   shell=True)
        self.client_ip = process.communicate()[0].strip().decode('utf-8')
        process = subprocess.Popen("grep \"$HOSTNAME\" /etc/hosts|awk '{print $1}'", stdout=subprocess.PIPE, shell=True)
        self.reverse_proxy_ip = process.communicate()[0].strip().decode('utf-8')
        self.session_info_map = {}

    def get_free_port(self):
        #TODO: Change this function to return a port from a pool of available ports
        return 8080

    def get_destination_ip_port(self):
        #TODO: Change this function to read from the database, and get a free ip/port
        return "172.18.0.2", "5901"

    def build_iptable_rules_setup(self, destination_ip, source_port, destination_port):
        route1 = "iptables -t nat -A PREROUTING -p tcp --dport %s -j DNAT --to-destination %s:%s;" % (source_port, destination_ip, destination_port)
        route2 = "iptables -t nat -A POSTROUTING -p tcp -s %s --dport %s -j SNAT --to-source %s;" % (destination_ip, destination_port, self.client_ip)
        route3 = "iptables -t nat -A POSTROUTING -p tcp -d %s --dport %s -j SNAT --to-source %s;" % (destination_ip, destination_port, self.reverse_proxy_ip)

        return route1 + route2 + route3

    def build_iptable_rules_setup_delete(self, client_ip, destination_ip, source_port, destination_port):
        route1 = "iptables -t nat -D PREROUTING -p tcp --dport %s -j DNAT --to-destination %s:%s;" % (source_port, destination_ip, destination_port)
        route2 = "iptables -t nat -D POSTROUTING -p tcp -s %s --dport %s -j SNAT --to-source %s;" % (destination_ip, destination_port, client_ip)
        route3 = "iptables -t nat -D POSTROUTING -p tcp -d %s --dport %s -j SNAT --to-source %s;" % (destination_ip, destination_port, self.reverse_proxy_ip)

        return route1 + route2 + route3

    def setup_routes(self, user_id, destination_ip):
        source_port = self.get_free_port()
        destination_ip, destination_port = self.get_destination_ip_port()
        iptables_rules = self.build_iptable_rules_setup(destination_ip, source_port, destination_port)
        self.session_info_map[user_id] = session_info.SessionInfo(self.client_ip, source_port, destination_ip, destination_port)
        process = subprocess.Popen(iptables_rules, stdout=subprocess.PIPE, shell=True)
        proc_stdout = process.communicate()[0].strip()
        print(iptables_rules)
        print(proc_stdout)

    def delete_iptable_rules(self, user_id):
        if user_id in self.session_info_map:
            iptables_rules = self.build_iptable_rules_setup_delete(
                self.session_info_map[user_id].client_ip,
                self.session_info_map[user_id].destination_ip,
                self.session_info_map[user_id].source_port,
                self.session_info_map[user_id].destination_port,
            )
            print(iptables_rules)
            process = subprocess.Popen(iptables_rules, stdout=subprocess.PIPE, shell=True)
            proc_stdout = process.communicate()[0].strip()
            print(proc_stdout)
            del self.session_info_map[user_id]


class Factory:
    router = None
    lock = Lock()

    def get_router(self):
        with self.lock:
            if self.router is not None:
                return self.router
            else:
                self.router = Router()
                return self.router

    def reset_router(self):
        with self.lock:
            self.router = Router()
