import socket
import threading
import time
import yaml
from types import NoneType
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
        connected = True
        # conn.send(f'Je bent verbonden met: [{self.ADDR[0]}:{self.ADDR[1]}]'.encode(self.FORMAT))

        request = conn.recv(1024).decode(self.FORMAT)
        string_list = request.split(' ')
        request_data = string_list[1]

        # game components
        def scenario_setup(conn, addr, msg=''):
            # conn.send(str(self.scenarios[self.voortgang.get(addr[0])[0]]).encode(self.FORMAT))
            self.send(conn, addr, cus=msg)

        def scenario_progression(conn, addr, answer, toSend):
            allowed = True
            # see if answer is a number
            answer = answer
            if 'reset' in answer.lower():
                self.voortgang[addr[0]] = ['scenario_1', []]
                scenario_setup(conn, addr)
                return
            try:
                try:
                    answer = int(answer)
                    answer = list(self.scenarios[self.voortgang[addr[0]][0]].get('Answer possibilities').keys())[answer - 1]
                except:
                    # means that the answer is not a number
                    pass
                answer = list(i for i in self.scenarios[self.voortgang[addr[0]][0]].get('Answer possibilities'))[list(i.lower() for i in self.scenarios[self.voortgang[addr[0]][0]].get('Answer possibilities')).index(answer.lower())]
                if 'needed' in self.scenarios[self.voortgang[addr[0]][0]].keys():
                    if type(self.scenarios[self.voortgang[addr[0]][0]]['needed']) != NoneType and answer in self.scenarios[self.voortgang[addr[0]][0]]['needed']:
                        if self.scenarios[self.voortgang[addr[0]][0]]['needed'][answer][0] not in self.voortgang[addr[0]][1]:
                            allowed = False
                            self.send(conn, addr, cus=f'{self.scenarios[self.voortgang[addr[0]][0]].get("needed").get(answer)[1]}')
                            return

                        if allowed:
                            # item_index = self.voortgang[addr[0]][1].index(self.scenarios[self.voortgang[addr[0]][0]]['needed'][answer][0])
                            # del self.voortgang[addr][1][item_index]
                            pass

                if 'get' in self.scenarios[self.voortgang[addr[0]][0]].keys() and type(self.scenarios[self.voortgang[addr[0]][0]]['get']) != NoneType and answer in \
                        self.scenarios[self.voortgang[addr[0]][0]]['get']:
                    # since it can't be deleted (if I do, it wil be deleted for everyone playing the game), I have to check for duplicates
                    if self.scenarios[self.voortgang[addr[0]][0]]['get'] not in self.voortgang[addr[0]][1]:
                        self.voortgang[addr[0]][1].append(self.scenarios[self.voortgang[addr[0]][0]]['get'][answer])
                if allowed:
                    self.voortgang[addr[0]][0] = self.scenarios[self.voortgang[addr[0]][0]].get('Answer possibilities')[answer]

                time.sleep(0.4)
                if toSend:
                    scenario_setup(conn, addr)
            except:
                print('er gaat iets fout')
                self.send(conn, addr, cus='Oeps, er ging iets mis!')

        # scenario_setup(conn, addr)
        global request_option
        request_option = None
        if request_data[0:2] == '/?':
            request_option = request_data[2:].split('=')[1]
            scenario_progression(conn, addr, request_option, True)
        else:
            scenario_setup(conn, addr)

    def send(self, conn, addr, cus=''):
        read_html = open('index.html', 'r')
        response = read_html.read()
        read_html.close()

        # replacing the content
        response = response.replace('{Stuk_Title}', self.voortgang[addr[0]][0])
        response = response.replace('{Stuk_Text}', self.scenarios[self.voortgang[addr[0]][0]]['text'].replace("_[", "`<i>").replace("]_", "</i>").replace("*[", "<b>").replace("]*", "</b>"))
        option_txt = ''
        option_amount = 0
        if self.scenarios[self.voortgang[addr[0]][0]].get('Answer possibilities'):
            for i in self.scenarios[self.voortgang[addr[0]][0]].get('Answer possibilities').keys():
                option_amount = option_amount + 1
                option_txt += f'<li>{i}</li>'
        response = response.replace('{Stuk_Options}', option_txt)
        response = response.replace('{Custom_Message}', cus)
        option_list = ''
        for i in range(option_amount):
            option_list += f"<option value='{i+1}' />"
        option_list += "<option value='reset' />"
        response = response.replace('{List_Items}', option_list)

        response = response.encode(self.FORMAT)
        header = 'HTTP/1.1 200 OK\n'
        mimetype = 'text/html'

        header += 'Content-Type: ' + str(mimetype) + '\n\n'

        final_response = header.encode(self.FORMAT)
        final_response += response
        conn.send(final_response)
        print(self.voortgang[addr[0]])
        conn.close()

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
            if addr[0] not in self.voortgang.keys():
                self.voortgang[addr[0]] = ['scenario_1', []]

            # create a new thread for the accepted user
            thread = threading.Thread(target=self.Game, args=(conn, addr))

            # start the new thread
            thread.start()


if __name__ == '__main__':
    IPV4 = socket.gethostbyname(socket.gethostname())
    PORT = 5500
    s = Server(IPv4=IPV4, port=PORT)
    print(s)
    s.start()
