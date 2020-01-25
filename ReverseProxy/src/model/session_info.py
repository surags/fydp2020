class SessionInfo:

    def __init__(self, client_ip, source_port, destination_ip, destination_port, os_type):
        self.client_ip = client_ip
        self.source_port = source_port
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.os_type = os_type
