import ast
import socket
import threading
import json

ip_input = input('Met welk IPv4 address wil je verbinden?\n')
HOST_IPV4 = ip_input
port_input = input('En op welke port?\n')
PORT = int(port_input)
ADDR = (HOST_IPV4, PORT)
FORMAT = 'utf-8'
HEADER = 64

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def send_own():
    while True:
        inp = input()
        send(inp)


def receiver():
    while True:
        msg = client.recv(2048).decode(FORMAT)
        try:
            msg = ast.literal_eval(msg)
            print(msg.get('text').replace("_[", "").replace("]_", "").replace("*[", "").replace("]*", ""))
            if msg.get('Answer possibilities'):
                for idx, i in enumerate(msg.get('Answer possibilities').keys()):
                    print(f' >\t{idx+1}. ', i, flush=True, sep='')
                # print(f' >\tb{i.decode(FORMAT)}')
        except:
            print(msg, flush=True)
            pass


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


def startup():
    client.connect(ADDR)

    # start a threading for all the actions that need to take place simultaneously
    rec_thread = threading.Thread(target=receiver)
    send_own_thread = threading.Thread(target=send_own)

    # start all the threads
    rec_thread.start()
    send_own_thread.start()


if __name__ == '__main__':
    startup()
