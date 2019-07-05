import subprocess
from queue import Queue
from threading import Lock
from src.model import session_info
from src.model import os_container

class Router:

    def __init__(self):
        process = subprocess.Popen("ip route show default | awk '/default/ {print $3}'", stdout=subprocess.PIPE,
                                   shell=True)
        self.client_ip = process.communicate()[0].strip().decode('utf-8')
        process = subprocess.Popen("grep \"$HOSTNAME\" /etc/hosts|awk '{print $1}'", stdout=subprocess.PIPE, shell=True)
        self.reverse_proxy_ip = process.communicate()[0].strip().decode('utf-8')
        self.session_info_map = {}
        self.port_queue = Queue()
        self.setup_ports()

    def setup_ports(self):
        for i in range(0, 5):
            self.port_queue.put(8080+i)

    def add_to_port_queue(self, port):
        self.port_queue.put(port)

    def get_free_port(self):
        #TODO: Change this function to return a port from a pool of available ports
        return self.port_queue.get()

    def set_container_busy(self, container):
        (os_container.OSContainer
            .set_by_id(container.container_id, {'is_free': False}))


    def set_container_free(self, container_id):
        (os_container.OSContainer
            .set_by_id(container_id, {'is_free': True}))


    def get_free_container(self):
        #TODO: Change this function to read from the database, and get a free ip/port
        container_info = (os_container.OSContainer
                .select()
                .where(
                    (os_container.OSContainer.is_free == True) &
                    (os_container.OSContainer.is_running == True)
                )
        )

        self.set_container_busy(container_info[0])

        return container_info[0]

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

    def setup_routes(self, user_id):
        if user_id not in self.session_info_map:
            source_port = self.get_free_port()
            destination_port = "5901"
            container = self.get_free_container()
            iptables_rules = self.build_iptable_rules_setup(container.ip_address, source_port, destination_port)
            self.session_info_map[user_id] = session_info.SessionInfo(container.container_id, self.client_ip, source_port, container.ip_address, destination_port)
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
            self.set_container_free(self.session_info_map[user_id].container_id)
            print(iptables_rules)
            process = subprocess.Popen(iptables_rules, stdout=subprocess.PIPE, shell=True)
            proc_stdout = process.communicate()[0].strip()
            print(proc_stdout)
            self.add_to_port_queue(self.session_info_map[user_id].source_port)
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
