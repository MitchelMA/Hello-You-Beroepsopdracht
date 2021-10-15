import time, yaml, os, ctypes
from types import NoneType
from yaml.loader import FullLoader


class game():
    def __init__(self, dev=False, direct=True, clear_screen=False):
        # houd bij in welke scenario de game zit
        self.current_scenario = 'scenario_1'
        # kijk of developer mode aan staat
        self.developer = dev
        self.directType = direct
        self.clear_screen= clear_screen
        # probeer de save file te openen als die er is
        try:
            saveFile = open('saveFile.txt', 'r')
            self.current_scenario = saveFile.read()
            saveFile.close()

            scenarios.get(self.current_scenario).get('text')
        except:
            self.current_scenario = 'scenario_1'
            pass
        if '__setup_scenario__':
            self.setup_scenario()
            
    #* setup scenario function
    def setup_scenario(self):
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

        if 'Answer posibilities' in scenarios[self.current_scenario]:
            curAnsNumb = 1
            for i in scenarios[self.current_scenario]['Answer posibilities']:
                print(">", end='\t')
                if i != '':
                    print(f'{curAnsNumb}. {i}', flush=True)
                else:
                    print(f'{curAnsNumb}. Enter om verder te gaan', flush=True)
                curAnsNumb = curAnsNumb + 1
            else:
                pass

        # check de waarde van de input
        player_answer = input('> ')
        # save wanneer waarde gelijk is aan 'save()'
        #! temporarly removed save feature
        if player_answer.lower() == 'save()':
            # self.save()
            pass
        
        # start opnieuw op wanneer waarde gelijk is aan 'restart()'
        elif player_answer.lower() == 'restart()' and self.developer == True:
            self.current_scenario = 'scenario_1'
            self.setup_scenario()

        # zorg dat je van scenario kan wisselen als developer mode aans staat en de input waarde gelijk is aan '--load'
        elif player_answer.lower() == '--load' and self.developer == True:
            loader = input('welke scenario wil je laden?\n')
            self.current_scenario = loader
            self.setup_scenario()
        
        # print de inhoud van de pockets wanneer waarde gelijk is aan 'pockets()'
        elif player_answer.lower() == 'pockets()':
            print(pockets)
            time.sleep(1)
            self.setup_scenario()
        
        # laat het spel stoppen waneer waarde glijk is aan 'end()'
        elif player_answer.lower() == 'end()':
            pass
        # als de waarde gelijk is aan geen van de vorige voorwaarden, pakt het spel het op als een antwoord op een input-vraag
        else:
            self.scenario_progression(player_answer)

    #* scenario progression function
    def scenario_progression(self, answer):
        # check of waarde een nummer kan zijn
        answerWhenNum = None
        try:
            answer_num = int(answer)
            # print(answer, '\b:', list(scenarios[self.current_scenario]['Answer posibilities'].keys())[answer_num - 1])
            answerWhenNum = list(scenarios[self.current_scenario]['Answer posibilities'].keys())[answer_num - 1]
            answer = answerWhenNum
        except:
            pass
        # kijk of het gegeven antwoord een mogelijkheid is, gebruik comprehension to get lowercase
        try:
            ans = list(i for i in scenarios[self.current_scenario]['Answer posibilities'])[list(i.lower() for i in scenarios[self.current_scenario]['Answer posibilities']).index(answer.lower())]
        except:
            print('dit is geen optie')
            time.sleep(1)
            self.setup_scenario()

        if ans in scenarios[self.current_scenario]['Answer posibilities']:
            allowed = True
            # kijk of er een specifiek item in je pockets moet zitten om verder te kunnen
            # print(ans)
            if 'needed' in scenarios[self.current_scenario].keys(): 
                if type(scenarios[self.current_scenario]['needed']) != NoneType and ans in scenarios[self.current_scenario]['needed']:
                    # als je dit item niet in je pockets hebt, kan je niet verder
                    if scenarios[self.current_scenario]['needed'][ans][0] not in pockets:
                        allowed = False

                    # als je dit item wel hebt
                    if allowed:
                        # als je dit item hebt, haal het dan uit je pockets
                        item_index = pockets.index(scenarios[self.current_scenario]['needed'][ans][0])
                        del pockets[item_index]

                    # in het geval je niet door mag, print uit waarom
                    else:
                        print(scenarios[self.current_scenario]['needed'][ans][1])
            
            # kijk of er een specifiek item is dat je krijgt als je deze optie kiest
            if 'get' in scenarios[self.current_scenario].keys() and type(scenarios[self.current_scenario]['get']) != NoneType and ans in scenarios[self.current_scenario]['get']:
                    # voeg het item dat je hoort te krijgen toe aan je pockets en verwijder de de 'get' content van het gegeven antwoord
                    pockets.append(scenarios[self.current_scenario]['get'][ans])
                    del scenarios[self.current_scenario]['get'][ans]
            
            # waneer je door mag gaan, zet de 'self.current_scenario' naar de volgende scenario
            if allowed:
                # get lowercase index so uppercase can be used
                self.current_scenario = scenarios[self.current_scenario]['Answer posibilities'][ans]
        
        # wanneer het gegeven antwoord geen mogelijkheid is, geef dit dan aan
        else:
            print('Dit is geen optie!')

        time.sleep(0.8)
        self.setup_scenario()

    #* save function
    #! NEEDS UPDATING
    def save(self):
        saveFile = open('saveFile.txt', 'w')
        saveFile.write(self.current_scenario)
        saveFile.close()
        cont = input('Wil je stoppen? Y/N\n')
        if cont.lower() == 'n':
            self.setup_scenario()
        else:
            pass

# toepassing die deze opdracht eigen is:

if __name__ == '__main__':
    # load file with scenarios
    loadYaml = open('scenarios.yaml', 'r')
    loadYaml = yaml.load(loadYaml, Loader=FullLoader)
    scenarios = loadYaml['scenarios']
    pockets = loadYaml['pockets']
    ctypes.windll.kernel32.SetConsoleTitleW("Vluchteling")

    thegame = game(direct=False, clear_screen=True)