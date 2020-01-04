import json
import threading
from time import sleep

import requests
import uwsgi
from bottle import response
import subprocess
from queue import Queue
from threading import Lock

from src.helper import container_helper
from src.helper import session_helper
from src.model import os_container
from src.model import session_info

session_helper = session_helper.factory.get_session_helper()
container_helper = container_helper.ContainerHelper()

class Router:

    def __init__(self):
        self.reverse_proxy_ip = ""
        if not bool(uwsgi.opt["is_azure"].decode("utf-8")):
            process = subprocess.Popen("grep \"$HOSTNAME\" /etc/hosts|awk '{print $1}'", stdout=subprocess.PIPE, shell=True)
            self.reverse_proxy_ip = process.communicate()[0].strip().decode('utf-8')
        else:
            self.reverse_proxy_ip = requests.get(
                "http://169.254.169.254/metadata/instance/network/interface/0/ipv4/ipAddress/0/privateIpAddress?api-version=2017-04-02&format=text",
                headers={"Metadata": "true"}).content.decode('utf-8')

    def set_container_busy(self, container):
        (os_container.OSContainer
         .set_by_id(container.ip_address, {'is_free': False}))

    def set_container_free(self, ip_address):
        (os_container.OSContainer
         .set_by_id(ip_address, {'is_free': True}))

    #This is done to set the container as unavailable. Mainly when the container is not running
    def set_container_unavailable(self, ip_address):
        (os_container.OSContainer
         .set_by_id(ip_address, {'is_running': False}))

    def get_free_container(self, os_type):
        try:
            print(os_type)
            container_info = (os_container.OSContainer.select().where(
                (os_container.OSContainer.is_free == True) & (os_container.OSContainer.is_running == True) & (
                            os_container.OSContainer.os_type == os_type)))
            print("Found results")
            print(container_info[0])
            self.set_container_busy(container_info[0])
            print("Updated results")
            return container_info[0]
        except Exception as e:
            print(e)
            return None

    def build_iptable_rules_setup(self, client_ip, destination_ip, source_port, destination_port):
        route1 = "iptables -t nat -A PREROUTING -p tcp --dport %s -j DNAT --to-destination %s:%s;" % (
            source_port, destination_ip, destination_port)
        route2 = "iptables -t nat -A POSTROUTING -p tcp -s %s --dport %s -j SNAT --to-source %s;" % (
            destination_ip, destination_port, client_ip)
        route3 = "iptables -t nat -A POSTROUTING -p tcp -d %s --dport %s -j SNAT --to-source %s;" % (
            destination_ip, destination_port, self.reverse_proxy_ip)

        return route1 + route2 + route3

    def build_iptable_rules_setup_delete(self, client_ip, destination_ip, source_port, destination_port):
        route1 = "iptables -t nat -D PREROUTING -p tcp --dport %s -j DNAT --to-destination %s:%s;" % (
            source_port, destination_ip, destination_port)
        route2 = "iptables -t nat -D POSTROUTING -p tcp -s %s --dport %s -j SNAT --to-source %s;" % (
            destination_ip, destination_port, client_ip)
        route3 = "iptables -t nat -D POSTROUTING -p tcp -d %s --dport %s -j SNAT --to-source %s;" % (
            destination_ip, destination_port, self.reverse_proxy_ip)

        return route1 + route2 + route3

    def setup_routes(self, user_id, client_ip, os_type, width, height):
        try:
            data = {}
            if user_id not in session_helper.session_info_map:
                source_port = session_helper.get_free_port()
                destination_port = "6080"
                container = self.get_free_container(os_type)
                if (container is None):
                    response.body = json.dumps({'error': 'No free containers'})
                    response.status = 400
                    return response
                iptables_rules = self.build_iptable_rules_setup(client_ip, container.ip_address, source_port, destination_port)
                session_helper.session_info_map[user_id] = session_info.SessionInfo(client_ip,
                                                                          source_port, container.ip_address,
                                                                          destination_port)
                process = subprocess.Popen(iptables_rules, stdout=subprocess.PIPE, shell=True)
                process.communicate()[0].strip()
                data['source_port'] = source_port
                self.setup_user_in_container(user_id, container.ip_address, width, height)
                health_check = threading.Thread(name='os_container_health_check', target=self.os_container_health_check,
                                                args=(container.ip_address,))
                health_check.start()
            else:
                data['source_port'] = session_helper.session_info_map[user_id].source_port
            response.body = json.dumps({'routes': data})
            response.status = 200
        except Exception as e:
            response.body = json.dumps({'error': str(e)})
            response.status = 500
        finally:
            return response

    def delete_iptable_rules(self, user_id):
        if user_id in session_helper.session_info_map:
            iptables_rules = self.build_iptable_rules_setup_delete(
                session_helper.session_info_map[user_id].client_ip,
                session_helper.session_info_map[user_id].destination_ip,
                session_helper.session_info_map[user_id].source_port,
                session_helper.session_info_map[user_id].destination_port,
            )
            self.set_container_free(session_helper.session_info_map[user_id].destination_ip)
            process = subprocess.Popen(iptables_rules, stdout=subprocess.PIPE, shell=True)
            process.communicate()[0].strip()
            session_helper.add_to_port_queue(session_helper.session_info_map[user_id].source_port)
            del session_helper.session_info_map[user_id]
        return json.dumps({'success': 'Deleted routes for user_id ' + str(user_id)})

    def setup_user_in_container(self, user_id, os_container_ip, width, height):
        url = 'http://{0}:9090/user/setup/{1}/{2}/{3}'.format(os_container_ip, user_id, width, height)
        requests.post(url)

    def os_container_health_check(self, os_container_ip):
        while True:
            url = "http://{0}:9090/health/check".format(os_container_ip)
            health_response = requests.get(url)
            if health_response.status_code != 200:
                self.set_container_unavailable(os_container_ip)
                #TODO: Delete routes for user connected to that failed container
                break
            else:
                health_response_json = health_response.json()
                print(health_response_json)
                if health_response_json['is_free'] and health_response_json['user_id'] and session_helper.session_info_map[health_response_json['user_id']]:
                    container_helper.cleanup_user_session(health_response_json['user_id'])
                    self.delete_iptable_rules(health_response_json['user_id'])
                    break
                elif health_response_json['is_free'] and not health_response_json['user_id']:
                    break
            #Make thread sleep for 30 seconds
            sleep(30)


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


factory = Factory()
