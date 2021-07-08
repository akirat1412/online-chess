import socket
import threading

MSG_LEN = 4
FORMAT = 'utf-8'
PORT = 5050

SEND_CHALLENGE = '8000'
RECEIVE_CHALLENGE = '8001'
ACCEPT_CHALLENGE = '8002'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class Client:
    def __init__(self):
        # will be value of text input
        self.server_ip = socket.gethostbyname(socket.gethostname())
        self.addr = (self.server_ip, PORT)

    def connect_to_server(self):
        client.connect(self.addr)
        self.send(SEND_CHALLENGE)

    def send(self, msg):
        self.client.send(msg.encode(FORMAT))
