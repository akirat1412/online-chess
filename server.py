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

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class Server:
    def __init__(self):
        # will be public ip address
        self.server_ip = socket.gethostbyname(socket.gethostname())
        self.addr = (self.server_ip, PORT)
        server.bind(self.addr)
        self.searching = False
        self.open_connection()

    def open_connection(self):
        self.searching = True
        server.listen()
        thread = threading.Thread(target=self.open_connection_thread)
        thread.start()

    def open_connection_thread(self):
        print('thread started')
        while self.searching:
            conn, addr = server.accept()
            self.accept_connection(conn, addr)

    def accept_connection(self, conn, addr):
        print(f'{addr} connected')
        connected = True
        while connected:
            message = conn.recv(MSG_LEN).decode(FORMAT)
            if message == SEND_CHALLENGE:
                conn.send(RECEIVE_CHALLENGE.encode(FORMAT))
            print(message)