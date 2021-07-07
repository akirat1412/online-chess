import socket

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (PORT, SERVER)

class Connector:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)

    def open_connection(self):
        self.server.listen()
        while True:
            conn, addr = self.server.accept()