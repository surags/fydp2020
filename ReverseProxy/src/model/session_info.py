class SessionInfo:

    def __init__(self, client_ip, source_port, destination_ip, destination_port, guacamole_stream_id, guacamole_view_only_id, os_type, first_name, last_name):
        self.client_ip = client_ip
        self.source_port = source_port
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.guacamole_stream_id = guacamole_stream_id
        self.guacamole_view_only_id = guacamole_view_only_id
        self.os_type = os_type
        self.first_name = first_name
        self.last_name = last_name
