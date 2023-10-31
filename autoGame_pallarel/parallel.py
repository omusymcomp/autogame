from subprocess import run as runShell
import threading
import time
import os

GAME = 100
parallel = 10

rel_pos = "$HOME/rcss/ham/omuHam/src/rel_pos/"

def autoGame(port):
    runShell([f"./autogame.sh {port} {rel_pos}"],shell=True)

start = time.time()

log_path = "./log/"
if not os.path.exists(log_path):
    os.makedirs(log_path)

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

end = time.time()
print("Time", (end-start))
