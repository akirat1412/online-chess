import socket
import threading

MSG_LEN = 4
FORMAT = 'utf-8'
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

SEND_CHALLENGE = '8000'
RECEIVE_CHALLENGE = '8001'
ACCEPT_CHALLENGE = '8002'

class Connector:
    def __init__(self):
        self.server = None
        self.client = None
        self.searching = False



