
# -*- coding: UTF-8 -*-

import subprocess
import threading
import sys
import time

class TTDHandler():
    def __init__(self,
                 #Maximo 15
                 ais_per_round = 8):
        #Not currently used
        self.ais_per_round = ais_per_round

        self.server_in_lock = threading.Lock()
        self.bufs = {}
        self.result_locks = {}
        
    def start(self):
        self.server = subprocess.Popen(["openttd",
                                        "-D",
                                        "-d 5"],
                                       stdin  = subprocess.PIPE,
                                       stdout = subprocess.PIPE,
                                       stderr = subprocess.STDOUT)
        self.read_thread = threading.Thread(target = self.read_output)
        self.read_thread.start()
                
    def add_ai(self, ai, ai_id):

        #management stuff
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
        if tmp != 'script':
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
        print "Heyoooooooooooooooooooo"
        time.sleep(100)
        return 10
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

    def write_to_server(self, msg):
        sleep_time = 0.5
        #Coderproofing
        msg += '\n'
        self.server_in_lock.acquire()
        self.server.stdin.write(msg)
        time.sleep(sleep_time)
        self.server_in_lock.release()
