from subprocess import run as runShell
import threading
import time

GAME = 2
parallel = 2

rel_pos = "$HOME/rcss/ham/omuHam/src/rel_pos/"

def autoGame(port):
    runShell([f"./autogame.sh {port} {rel_pos}"],shell=True)

for num in range(GAME):
    port = 6000
    para = []
    for n in range(parallel):
        t = threading.Thread(target=autoGame, args=(port,))
        t.start()
        port += 100
        para.append(t)
        time.sleep(3)
    
    for n in range(parallel):
        tmp = para[n]
        tmp.join()