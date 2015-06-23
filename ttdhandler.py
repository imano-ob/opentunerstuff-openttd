
import subprocess
import threading
import sys
import time

class TTDHandler():
    def __init__(self,
                 #Maximo 15
                 max_ais = 8,
                 ais_per_round = 8):
        self.max_ais = max_ais
        #Not currently used
        self.ais_per_round = ais_per_round

        self.ai_sem = threading.Semaphore(self.max_ais)
        self.server_in_lock = threading.Lock()
        self.server_out_locks = {}
        self.server_in_locks = {}
        self.bufs = {}
        
    def start(self):
        self.server = subprocess.Popen(["openttd",
                                        "-D",
                                        "-d 6"],
                                       stdin  = subprocess.PIPE,
                                       stdout = subprocess.PIPE,
                                       stderr = subprocess.STDOUT)
        self.read_thread = threading.Thread(target = self.read_output)
                
    def add_ai(self, ai, ai_id):

        self.ai_sem.acquire()
        
        #management stuff
        self.server_out_locks[ai_id] = threading.Lock()
        self.server_in_locks[ai_id] = threading.Lock()

        #server communication
        self.server_in_lock.acquire()
        #Recarrega AIs para incluir a AI recem gerada
        self.server.stdin.write("reload_ai")
        self.server.stdin.write("start_ai {}\n".format(ai))
        #TODO: pegar id na ai no openttd?
        self.server_in_lock.release()

    def stop_ai(self, ai_id):
        self.server_in_lock.acquire()   
        #self.server.stdin.write("stop_ai {}\n".format(ai))
        #TODO: Stop AI
        self.server_in_lock.release()
        self.ai_sem.release()
        
    def read_output(self):
        while True:
            last_line = self.server.stdout.readline()
            ai_id, content = self.parse(last_line)
            #TODO: arranjar um jeito de lidar com o comando companies do Openttd
            if ai_id == None:
                continue
            self.server_out_locks[ai_id].acquire()
            #...huh. acho que isso pode nao fazer sentido
            #depende se a ai no final vai cuspir mais de uma mensagem?
            self.bufs[ai_id] = content
            self.server_out_locks[ai_id].release()
            self.server_in_locks[ai_id].release()

    def parse(self, line):
        #TODO: parsear
        #AIs: começam com [script]
        #...huh
        #São da forma [script][<ID>][<Error/Warning/Info>] <Texto>
        #Deve dar pra usar isso pra extrair o ID in TTD?
        pass
            
    def result(self, ai_id):
        #temp codez
        time.sleep(10)
        return 10
        #real codez
        #TODO: cleanup
        self.server_in_locks[ai_id].acquire()
        res = self.bufs[ai_id]
        self.server_in_locks[ai_id].release()

        self.stop_ai(ai_id)
        
        return res
        
    def shutdown(self):
        #TODO: cleanup
        self.server_in_lock.acquire()   
        self.server.stdin.write("quit\n")
        self.server_in_lock.release()

