from enum import Enum

class BroadcastStates(Enum):
    IDLE = None
    START = {"eventType": "start_broadcast", "broadcast_id": None}
    STOP = {"eventType": "stop_broadcast", "broadcast_id": None}
