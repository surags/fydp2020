class BroadcastSessionInfo:

    def __init__(self, client_ip, source_port, destination_ip, destination_port, guacamole_view_only_id, os_type):
        self.client_ip = client_ip
        self.source_port = source_port
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.guacamole_view_only_id = guacamole_view_only_id
        self.os_type = os_type
