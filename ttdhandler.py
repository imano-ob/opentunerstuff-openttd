
# -*- coding: UTF-8 -*-

import subprocess
import threading
import sys
import time

class TTDHandler():
    def __init__(self,
                 #Maximo 15
                 ais_per_round = 8):

        self.ais_per_round = ais_per_round
        self.handler_lock = threading.Lock()
        self.started_ais = 0
        self.active_ais = 0
        self.add_ai_lock = threading.Lock()
                
        self.server_in_lock = threading.Lock()
        self.bufs = {}
        self.result_locks = {}
        self.running = False
        
    def start(self, args = ["openttd",
                            "-D",
                            "-d 5"]):
        if self.running:
            #OhNoes!
            #construir exceção/retornar algo?
            raise
        self.server = subprocess.Popen(args,
                                       stdin  = subprocess.PIPE,
                                       stdout = subprocess.PIPE,
                                       stderr = subprocess.STDOUT)
        self.read_thread = threading.Thread(target = self.read_output)
        self.read_thread.start()
        self.running = True
                
    def start_ai(self, ai, ai_id):

        #management stuff
        self.add_ai_lock.acquire()
        self.handler_lock.acquire()
        self.started_ais += 1
        self.active_ais += 1
        self.handler_lock.release()
        if self.started_ais < self.ais_per_round:
            self.add_ai_lock.release()
            
        self.result_locks[ai_id] = threading.Lock()
        self.result_locks[ai_id].acquire()
        
        #server communication
        cmd = "rescan_ai"
        self.write_to_server(cmd)
        cmd = "start_ai {}".format(ai)
        self.write_to_server(cmd)
        
    def stop_ai(self, ttd_id):
        cmd = "stop_ai {}".format(ttd_id + 1) #reasons
        self.write_to_server(cmd)
        self.active_ais -= 1
        if self.active_ais == 0 and self.started_ais == self.ais_per_round:
            self.reset_server()
        self.result_locks[ai_id].release()

        
    def read_output(self):
        while True:
            last_line = self.server.stdout.readline()
            print last_line
            if last_line == '':
                break
            ai_id, ttd_id, content = self.parse(last_line)
            if ai_id == None:
                continue
            self.bufs[ai_id] = content
            self.stop_ai(ttd_id)

    def parse(self, line):
        #AIs: começam com [script]
        #São da forma [script][<ID>][<Error/Warning/Info>] <Texto>
        #AIs devem ter output da froma [<Tuner ID>][<Resultado>] for
        #simplicity's sake
        tmp = line.split(']')
        for field in tmp:
            field.strip('[')
        if tmp != 'script' or len(tmp) < 5:
            return None, None, None
        #Campos restantes são irrelevantes para nossos propósitos
        #TODO: Possivelmente certificar que vai continuar funcionando
        #no futuro
        ai_id = tmp[3]
        ttd_id = tmp[1]
        content = tmp[4]
        print "{} {} {}".format(ai_id, ttd_id, content)

        return ai_id, ttd_id, content
            
    def result(self, ai_id):
        #temp codez
#        print "Heyoooooooooooooooooooo"
#        time.sleep(100)
#        return 10
        #real codez
        #TODO: cleanup de coisas relacionadas à ai que vai morrer

        self.result_locks[ai_id].acquire()
        res = self.bufs[ai_id]        
        self.result_locks[ai_id].release()

        self.bufs[ai_id] = None
        self.result_locks[ai_id] = None

        return res
        
    def shutdown(self):
        #TODO: cleanup
        self.write_to_server("quit")
        self.running = False

    def reset_server(self):
        self.write_to_server("restart")
        self.started_ais = 0
        self.active_ais = 0
        self.add_ai_lock.release()
        
    def write_to_server(self, msg):
        sleep_time = 0.5
        #Coderproofing
        msg += '\n'
        self.server_in_lock.acquire()
        print('to server ->' + msg)
        self.server.stdin.write(msg)
        time.sleep(sleep_time)
        self.server_in_lock.release()
