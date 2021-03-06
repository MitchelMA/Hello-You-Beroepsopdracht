import ctypes
import os
import time
import yaml
from types import NoneType
from yaml.loader import FullLoader


class Game:
    def __init__(self, dev=False, direct=True, clear_screen=False):
        """Initialiseert de Class en zoekt ook naar een save file"""
        # houd bij in welke scenario de game zit
        self.current_scenario = 'scenario_1'
        # kijk of developer mode aan staat
        self.developer = dev
        self.directType = direct
        self.clear_screen = clear_screen
        # probeer de save file te openen als die er is
        try:
            save_file = open('saveFile.txt', 'r')
            self.current_scenario = save_file.read()
            save_file.close()

            scenarios.get(self.current_scenario).get('text')
        except:
            self.current_scenario = 'scenario_1'

        if '__setup_scenario__':
            self.setup_scenario()

    # * setup scenario function
    def setup_scenario(self):
        """Set de tekst up en kijkt vervolgens naar de input van de speler.\n
        Wanneer er een input is gegeven, wordt de definition scenario_progression gecalld"""
        if self.clear_screen:
            os.system('cls')
        if self.directType:
            print(scenarios[self.current_scenario]['text'].replace("_[", "\033[3m").replace("]_", "\033[0m").replace("*[", "\033[1m").replace("]*", "\033[0m"))
        else:
            for i in scenarios[self.current_scenario]['text'].replace("_[", "\033[3m").replace("]_", "\033[0m").replace("*[", "\033[1m").replace("]*", "\033[0m"):
                print(i, end='', flush=True)
                time.sleep(0.015)
            time.sleep(0.1)
            print('')

        if 'Answer possibilities' in scenarios[self.current_scenario]:
            cur_ans_numb = 1
            for i in scenarios[self.current_scenario]['Answer possibilities']:
                print(">", end='\t')
                if i != '':
                    print(f'{cur_ans_numb}. {i}', flush=True)
                else:
                    print(f'{cur_ans_numb}. Enter om verder te gaan', flush=True)
                cur_ans_numb = cur_ans_numb + 1
            else:
                pass

        # check de waarde van de input
        player_answer = input('> ')
        # save wanneer waarde gelijk is aan 'save()'
        # ! temporarily removed save feature
        if player_answer.lower() == 'save()':
            # self.save()
            pass

        # start opnieuw op wanneer waarde gelijk is aan 'restart()'
        elif player_answer.lower() == 'restart()' and self.developer is True:
            self.current_scenario = 'scenario_1'
            self.setup_scenario()

        # zorg dat je van scenario kan wisselen als developer mode aans staat en de input waarde gelijk is aan '--load'
        elif player_answer.lower() == '--load' and self.developer is True:
            loader = input('welke scenario wil je laden?\n')
            self.current_scenario = loader
            self.setup_scenario()

        # print de inhoud van de pockets wanneer waarde gelijk is aan 'pockets()'
        elif player_answer.lower() == 'pockets()':
            print(pockets)
            time.sleep(1)
            self.setup_scenario()

        # laat het spel stoppen wanneer waarde gelijk is aan 'end()'
        elif player_answer.lower() == 'end()':
            pass
        # als de waarde gelijk is aan geen van de vorige voorwaarden, pakt het spel het op als een antwoord op een input-vraag
        else:
            self.scenario_progression(player_answer)

    # * scenario progression function
    def scenario_progression(self, answer: str):
        """Waarde handeling definition.\n
        Checkt of de waarde overeenkomt met ????n van de gegeven antwoorden.\n
        Wanneer dit het geval is, wordt self.current_scenario ge??pdate naar de waarde van het gegeven antwoord in de scenarios.yaml file"""
        # check of waarde een nummer kan zijn
        global ans
        answer_when_num = None
        try:
            answer_num = int(answer)
            answer_when_num = list(scenarios[self.current_scenario]['Answer possibilities'].keys())[answer_num - 1]
            answer = answer_when_num
        except:
            pass
        # kijk of het gegeven antwoord een mogelijkheid is, gebruik comprehension om lowercase te kunnen gebruiken
        try:
            ans = list(i for i in scenarios[self.current_scenario]['Answer possibilities'])[list(i.lower() for i in scenarios[self.current_scenario]['Answer possibilities']).index(answer.lower())]
        except:
            print('dit is geen optie')
            time.sleep(1)
            self.setup_scenario()

        if ans in scenarios[self.current_scenario]['Answer possibilities']:
            allowed = True
            # kijk of er een specifiek item in je pockets moet zitten om verder te kunnen
            if 'needed' in scenarios[self.current_scenario].keys():
                if type(scenarios[self.current_scenario]['needed']) != NoneType and ans in \
                        scenarios[self.current_scenario]['needed']:
                    # als je dit item niet in je pockets hebt, kan je niet verder
                    if scenarios[self.current_scenario]['needed'][ans][0] not in pockets:
                        allowed = False

                    # als je dit item wel hebt
                    if allowed:
                        # als je dit item hebt, haal het dan uit je pockets
                        item_index = pockets.index(scenarios[self.current_scenario]['needed'][ans][0])
                        # del pockets[item_index]

                    # in het geval je niet door mag, print uit waarom
                    else:
                        print(scenarios[self.current_scenario]['needed'][ans][1])

            # kijk of er een specifiek item is dat je krijgt als je deze optie kiest
            if 'get' in scenarios[self.current_scenario].keys() and type(scenarios[self.current_scenario]['get']) != NoneType and ans in scenarios[self.current_scenario]['get']:
                # voeg het item dat je hoort te krijgen toe aan je pockets en verwijder de de 'get' content van het gegeven antwoord, zorg voor geen dubbele
                if scenarios[self.current_scenario]['get'][ans] not in pockets:
                    pockets.append(scenarios[self.current_scenario]['get'][ans])
                    del scenarios[self.current_scenario]['get'][ans]

            # wanneer je door mag gaan, zet de 'self.current_scenario' naar de volgende scenario
            if allowed:
                # get lowercase index so uppercase can be used
                self.current_scenario = scenarios[self.current_scenario]['Answer possibilities'][ans]

        # wanneer het gegeven antwoord geen mogelijkheid is, geef dit dan aan
        else:
            print('Dit is geen optie!')

        time.sleep(0.8)
        self.setup_scenario()

    # * save function
    # ! NEEDS UPDATING
    def save(self):
        """Functie voor opslaan.\n
        WORDT MOMENTEEL NIET GEBRUIKT!!"""
        save_file = open('saveFile.txt', 'w')
        save_file.write(self.current_scenario)
        save_file.close()
        cont = input('Wil je stoppen? Y/N\n')
        if cont.lower() == 'n':
            self.setup_scenario()
        else:
            pass


# toepassing die deze opdracht eigen is:

if __name__ == '__main__':
    # load file with scenarios
    loadYaml = open('./scenarios.yaml', 'r', encoding='utf-8')
    loadYaml = yaml.load(loadYaml, Loader=FullLoader)
    scenarios = loadYaml['scenarios']
    pockets = loadYaml['pockets']
    ctypes.windll.kernel32.SetConsoleTitleW("Vluchteling")

    thegame = Game(direct=False, clear_screen=True)
