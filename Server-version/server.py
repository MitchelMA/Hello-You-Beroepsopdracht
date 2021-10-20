import threading
import socket
import time
from types import NoneType
import yaml
from yaml.loader import FullLoader


class Server:
    def __init__(self, IPv4: str = '192.168.1.42', port: int = 5500, FORMAT: str = 'utf-8', loadFile: str = '../scenarios.yaml'):
        self.__IPv4 = IPv4
        self.__port = port
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__ADDR = (self.ipv4, self.port)
        self.__load_file = loadFile
        self.__opened = None
        self.__scenarios = None
        self.__FORMAT = FORMAT
        self.__HEADER = 64
        self.voortgang = {}

    def __repr__(self):
        return f"{self.__class__.__name__} (address={self.ipv4}, port={self.port}, server={self.server})"

    @property
    def ipv4(self):
        return self.__IPv4

    @property
    def port(self):
        return self.__port

    @property
    def server(self):
        return self.__server

    @property
    def ADDR(self):
        return self.__ADDR

    @property
    def load_file(self):
        return self.__load_file

    @property
    def FORMAT(self):
        return self.__FORMAT

    @property
    def HEADER(self):
        return self.__HEADER

    @property
    def opened_yaml(self):
        return self.__opened

    @property
    def scenarios(self):
        return self.__scenarios

    def Game(self, conn, addr):
        print(f'[NEW CONNECTION] {addr} connected.')
        print(f'[ACTIVE] {threading.active_count() - 1}')
        # print(self.voortgang)
        connected = True
        conn.send(f'Je bent verbonden met: [{self.ADDR[0]}:{self.ADDR[1]}]'.encode(self.FORMAT))

        # game components
        def scenario_setup(conn, addr):
            conn.send(str(self.scenarios[self.voortgang.get(addr)[0]]).encode(self.FORMAT))

        def scenario_progression(conn, addr, answer):
            allowed = True
            # see if answer is a number
            answer = answer
            try:
                try:
                    answer = int(answer)
                    answer = list(self.scenarios[self.voortgang[addr][0]].get('Answer possibilities').keys())[answer - 1]
                except:
                    # means that the answer is not a number
                    pass
                answer = list(i for i in self.scenarios[self.voortgang[addr][0]].get('Answer possibilities'))[list(i.lower() for i in self.scenarios[self.voortgang[addr][0]].get('Answer possibilities')).index(answer.lower())]
                if 'needed' in self.scenarios[self.voortgang[addr][0]].keys():
                    if type(self.scenarios[self.voortgang[addr][0]]['needed']) != NoneType and answer in self.scenarios[self.voortgang[addr][0]]['needed']:
                        if self.scenarios[self.voortgang[addr][0]]['needed'][answer][0] not in self.voortgang[addr][1]:
                            allowed = False
                            conn.send(f'{self.scenarios[self.voortgang[addr][0]].get("needed").get(answer)[1]}\n'.encode(self.FORMAT))

                        if allowed:
                            item_index = self.voortgang[addr][1].index(self.scenarios[self.voortgang[addr][0]]['needed'][answer][0])
                            # del self.voortgang[addr][1][item_index]

                if 'get' in self.scenarios[self.voortgang[addr][0]].keys() and type(self.scenarios[self.voortgang[addr][0]]['get']) != NoneType and answer in self.scenarios[self.voortgang[addr][0]]['get']:
                    # since it can't be deleted (if I do, it wil be deleted for everyone playing the game), I have to check for duplicates
                    if self.scenarios[self.voortgang[addr][0]]['get'] not in self.voortgang[addr][1]:
                        self.voortgang[addr][1].append(self.scenarios[self.voortgang[addr][0]]['get'][answer])

                if allowed:
                    self.voortgang[addr][0] = self.scenarios[self.voortgang[addr][0]].get('Answer possibilities')[answer]

                time.sleep(0.4)
                scenario_setup(conn, addr)
            except:
                conn.send('oeps, er ging iets fout!\n'.encode(self.FORMAT))
                time.sleep(0.4)
                scenario_setup(conn, addr)

        time.sleep(1)
        scenario_setup(conn, addr)

        # message receiving with protocol (first get length, when there is a length; read the message)
        while connected:
            try:
                msg_length = conn.recv(self.HEADER).decode(self.FORMAT)
            except:
                conn.close()
                break

            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.FORMAT)
                scenario_progression(conn, addr, msg)
                # print(f'[PROGRESSION] {self.voortgang}')

        del self.voortgang[addr]
        print(f'[DISCONNECTION] {addr} disconnected')
        conn.close()
        print(f'[ACTIVE] {threading.active_count()-2}')

    def start(self):
        """function to start the server on the specified address and port"""

        # open the yaml file
        opened = open(self.load_file, 'r', encoding=self.FORMAT)
        opened = yaml.load(opened, Loader=FullLoader)
        self.__opened = opened
        self.__scenarios = self.opened_yaml['scenarios']

        self.server.bind(self.ADDR)
        self.server.listen()
        print(f"[LISTENING] server is listening on {self.ipv4}:{self.port}")
        while True:
            # accept the new user
            conn, addr = self.server.accept()

            # create a new list_entry for every joined user
            self.voortgang[addr] = ['scenario_1', []]

            # create a new thread for the accepted user
            thread = threading.Thread(target=self.Game, args=(conn, addr))

            # start the new thread
            thread.start()


if __name__ == '__main__':
    port_input = input('Op welke port wil je je server starten?\n')
    IPV4 = socket.gethostbyname(socket.gethostname())
    PORT = port_input
    s = Server(IPV4, int(port_input))
    s.start()
