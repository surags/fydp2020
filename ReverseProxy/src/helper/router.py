import json
import threading
from time import sleep

import requests
import uwsgi
from bottle import response
import subprocess
from threading import Lock

from src.helper import container_helper
from src.helper import session_helper
from src.helper import broadcast_helper

from src.model import os_container
from src.model import session_info
from src.model import broadcast_session_info
from src.model.broadcast_states import BroadcastStates

from src.model.users import Users
from src.model.base_model import db

session_helper = session_helper.factory.get_session_helper()
broadcast_helper = broadcast_helper.factory.get_broadcast_helper()
container_helper = container_helper.ContainerHelper()


class Router:

    def __init__(self):
        self.reverse_proxy_ip = ""
        if uwsgi.opt["is_azure"].decode("utf-8") == "False":
            process = subprocess.Popen("grep \"$HOSTNAME\" /etc/hosts|awk '{print $1}'", stdout=subprocess.PIPE,
                                       shell=True)
            self.reverse_proxy_ip = process.communicate()[0].strip().decode('utf-8')
        else:
            self.reverse_proxy_ip = requests.get(
                "http://169.254.169.254/metadata/instance/network/interface/0/ipv4/ipAddress/0/privateIpAddress?api-version=2017-04-02&format=text",
                headers={"Metadata": "true"}).content.decode('utf-8')

    @db.connection_context()
    def set_container_busy(self, container):
        (os_container.OSContainer
         .set_by_id(container.ip_address, {'is_free': False}))

    @db.connection_context()
    def set_container_free(self, ip_address):
        (os_container.OSContainer
         .set_by_id(ip_address, {'is_free': True}))

    # This is done to set the container as unavailable. Mainly when the container is not running
    @db.connection_context()
    def set_container_unavailable(self, ip_address):
        (os_container.OSContainer
         .set_by_id(ip_address, {'is_running': False}))

    @db.connection_context()
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

    def delete_routes(self, user_id):
        container_helper.cleanup_user_session(user_id)
        response.body = self.delete_iptable_rules(user_id)
        if broadcast_helper.broadcast_session_state is BroadcastStates.START and user_id is \
                broadcast_helper.broadcast_session_state.value["broadcast_id"]:
            broadcast_helper.cleanup_broadcast_session()

    def setup_routes(self, user_id, client_ip, os_type, width, height):
        try:
            data = {}
            if user_id not in session_helper.session_info_map:
                source_port = session_helper.get_free_port()
                destination_port = "8080"
                container = self.get_free_container(os_type)
                if (container is None):
                    response.body = json.dumps({'error': 'No free containers'})
                    response.status = 400
                    return response

                iptables_rules = self.build_iptable_rules_setup(client_ip, container.ip_address, source_port,
                                                                destination_port)
                query = Users.select(Users.first_name, Users.last_name).where(Users.user_id == user_id)
                result = query[0]
                print("Name: " + result.first_name + result.last_name)
                session_helper.session_info_map[user_id] = session_info.SessionInfo(client_ip,
                                                                                    source_port, container.ip_address,
                                                                                    destination_port,
                                                                                    container.guacamole_stream_id,
                                                                                    container.guacamole_view_only_id,
                                                                                    os_type, result.first_name,
                                                                                    result.last_name)
                process = subprocess.Popen(iptables_rules, stdout=subprocess.PIPE, shell=True)
                process.communicate()[0].strip()
                data['source_port'] = source_port
                data['guacamole_id'] = container.guacamole_stream_id
                data['os_type'] = os_type
                self.setup_user_in_container(user_id, container.ip_address, width, height)
                health_check_thread = threading.Thread(name='os_container_health_check',
                                                       target=self.os_container_health_check,
                                                       args=(container.ip_address, user_id,))
                health_check_thread.start()
            else:
                if session_helper.session_info_map[user_id].os_type != os_type:
                    container_helper.cleanup_user_session(user_id)
                    self.delete_iptable_rules(user_id)
                    return self.setup_routes(user_id, client_ip, os_type, width, height)
                else:
                    data['source_port'] = session_helper.session_info_map[user_id].source_port
                    data['guacamole_id'] = session_helper.session_info_map[user_id].guacamole_stream_id
                    data['os_type'] = session_helper.session_info_map[user_id].os_type
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

    # Get the existing user session if one exists
    def get_session(self, user_id):
        if user_id in session_helper.session_info_map:
            current_session = {'guacamole_id': session_helper.session_info_map[user_id].guacamole_stream_id,
                               'source_port': session_helper.session_info_map[user_id].source_port,
                               'os_type': session_helper.session_info_map[user_id].os_type}
            return current_session
        else:
            return None

    # Setup routes to allow clients to stream broadcast content
    def setup_stream_routes(self, user_id, client_ip, broadcast_id):
        try:
            # Do not update the session info map to retain the previous connection
            print("Setup stream routes")
            data = {}
            if user_id in broadcast_helper.broadcast_session_info_map:
                data['source_port'] = str(broadcast_helper.broadcast_session_info_map[user_id].source_port)
                data['guacamole_id'] = broadcast_helper.broadcast_session_info_map[user_id].guacamole_view_only_id
                data['os_type'] = broadcast_helper.broadcast_session_info_map[user_id].os_type

                response.body = json.dumps({'routes': data})
                response.status = 200
            # Query session info map for broadcast session
            elif broadcast_id in session_helper.session_info_map:
                print("Found session")
                # Get broadcast container IP
                container_ip = session_helper.session_info_map[broadcast_id].destination_ip

                # Get new source_port
                source_port = session_helper.get_free_port()
                destination_port = "8080"

                iptables_rules = self.build_iptable_rules_setup(client_ip, container_ip, source_port, destination_port)
                process = subprocess.Popen(iptables_rules, stdout=subprocess.PIPE, shell=True)
                process.communicate()[0].strip()
                print("Built IP tables done")

                data['source_port'] = str(source_port)
                data['guacamole_id'] = str(session_helper.session_info_map[broadcast_id].guacamole_view_only_id)
                data['os_type'] = session_helper.session_info_map[broadcast_id].os_type

                broadcast_helper.broadcast_session_info_map[user_id] = broadcast_session_info.BroadcastSessionInfo(
                    client_ip,
                    source_port,
                    container_ip,
                    destination_port,
                    session_helper.session_info_map[
                        broadcast_id].guacamole_view_only_id,
                    session_helper.session_info_map[
                        broadcast_id].os_type
                )
                print("Broadcasting " + str(container_ip) + ":8080 to " + str(client_ip) + " at :" + str(source_port))
                response.body = json.dumps({'routes': data})
                response.status = 200

            else:
                response.body = json.dumps({'error': "The broadcast session does not exist"})
                response.status = 500

        except Exception as e:
            response.body = json.dumps({'error': str(e)})
            response.status = 500

        finally:
            return response

    # Delete the temporarily created stream routes
    def delete_stream_routes(self, user_id):
        json_resp = dict()
        try:
            # Get broadcast IP from session_info_map
            broadcast_ip = broadcast_helper.broadcast_session_info_map[user_id].destination_ip
            client_ip = broadcast_helper.broadcast_session_info_map[user_id].client_ip
            source_port = broadcast_helper.broadcast_session_info_map[user_id].source_port
            destination_port = broadcast_helper.broadcast_session_info_map[user_id].destination_port
            iptables_rules = self.build_iptable_rules_setup_delete(client_ip, broadcast_ip, source_port,
                                                                   destination_port)
            process = subprocess.Popen(iptables_rules, stdout=subprocess.PIPE, shell=True)
            process.communicate()[0].strip()
            session_helper.add_to_port_queue(source_port)
            broadcast_helper.remove_user_from_session_info(user_id)
            json_resp["success"] = 'Deleted temp routes for user_id ' + str(user_id)
        except Exception as e:
            json_resp["error"] = "An unexpected error occured: " + str(e)
        finally:
            return json.dumps(json_resp)

    def setup_user_in_container(self, user_id, os_container_ip, width, height):
        url = 'http://{0}:9090/user/setup/{1}/{2}/{3}'.format(os_container_ip, user_id, width, height)
        requests.post(url)

    def os_container_health_check(self, os_container_ip, user_id):
        while True:
            sleep(30)
            if session_helper.session_info_map[user_id].is_health_check_enabled is True:
                url = "http://{0}:9090/health/check".format(os_container_ip)
                health_response = requests.get(url)
                if health_response.status_code != 200:
                    self.set_container_unavailable(os_container_ip)
                    # TODO: Delete routes for user connected to that failed container
                    break
                else:
                    health_response_json = health_response.json()
                    print(health_response_json)
                    if health_response_json['is_free'] and health_response_json['user_id'] and \
                            session_helper.session_info_map[health_response_json['user_id']]:
                        if session_helper.session_info_map[
                            health_response_json['user_id']].destination_ip == os_container_ip:
                            container_helper.cleanup_user_session(health_response_json['user_id'])
                            self.delete_iptable_rules(health_response_json['user_id'])
                            if broadcast_helper.broadcast_session_state is BroadcastStates.START and user_id is \
                                    broadcast_helper.broadcast_session_state.value["broadcast_id"]:
                                broadcast_helper.cleanup_broadcast_session()

                        break
                    elif health_response_json['is_free'] and not health_response_json['user_id']:
                        break
            # Make thread sleep for 30 seconds


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
