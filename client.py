import socket
import threading

MSG_LEN = 4
FORMAT = 'utf-8'
PORT = 5050
SERVER_IP = socket.gethostbyname(socket.gethostname())

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.connect(SERVER_IP, PORT)

clients = []


def match_clients():
    pass


while True:
    message, addr = server.recvfrom()
    clients.append(addr)
    print(f'{addr} started connection')
    if len(clients) >= 2:
        break
