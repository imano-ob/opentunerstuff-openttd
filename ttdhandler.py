
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
        self.wait_lock = threading.Lock()

        self.start_time = time.time()
        self.logfile = open("logfile.log", "w")
        
    def start(self, args = ["openttd",
                            "-D",
                            "-d script 5"]):
        if self.running:
            #OhNoes!
            #construir exceção/retornar algo?
            raise
        self.server = subprocess.Popen(args,
                                       stdin  = subprocess.PIPE,
                                       stdout = subprocess.PIPE,
                                       stderr = subprocess.STDOUT)
        self.read_thread = threading.Thread(target = self.read_output)
        self.wait_lock.acquire()
        self.read_thread.start()
        self.wait_lock.acquire()
        self.wait_lock.release()
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
            
#        self.result_locks[ai_id] = threading.Lock()
#        self.result_locks[ai_id].acquire()
        
        #server communication
        cmd = "rescan_ai"
        self.write_to_server(cmd)
        cmd = "start_ai {}".format(ai)
        self.write_to_server(cmd)
        
    def stop_ai(self, ttd_id, ai_id):
        cmd = "stop_ai {}".format(ttd_id + 1) #reasons
        self.write_to_server(cmd)
        self.active_ais -= 1
        if self.active_ais == 0 and self.started_ais == self.ais_per_round:
            self.reset_server()
#        self.result_locks[ai_id].release()

        
    def read_output(self):
        while True:
            last_line = self.server.stdout.readline()
            print last_line
            if last_line == '':
                return
            if last_line.find('starting game') != -1:
                self.wait_lock.release()
            ai_id, ttd_id, content = self.parse(last_line)
            if ai_id == None:
                continue
            self.bufs[ai_id] = content
            self.stop_ai(ttd_id, ai_id)

    def parse(self, line):
        #AIs: começam com [script]
        #São da forma [script][<ID>][<Error/Warning/Info>] <Texto>
        #AIs devem ter output da forma [tuner][<Tuner ID>][<Resultado>] for
        #simplicity's sake
        if not "tuner" in line:
            return None, None, None
        tmp = line.split(']')
        #Campos restantes são irrelevantes para nossos propósitos
        #TODO: Possivelmente certificar que vai continuar funcionando
        #no futuro
        for i in tmp:
            print i
        ai_id = tmp[4].replace('[', '')#.strip('[')
        print "ai id -> ", ai_id
        ttd_id = int(tmp[1].replace('[',''))
        print "ttd id -> ", ttd_id
        content = tmp[5].replace('[','')
        print "content -> ", content
        print "handler leu -> {} {} {}".format(ai_id, ttd_id, content)

        return ai_id, ttd_id, content
            
    def result(self, ai_id):
        #TODO: cleanup de coisas relacionadas à ai que vai morrer

        self.result_locks[ai_id].acquire()
        res = int(self.bufs[ai_id])        
        self.result_locks[ai_id].release()

        self.bufs[ai_id] = None
        self.result_locks[ai_id] = None

        timediff = time.time() - self.start_time
        self.logfile.write("time: {}, res: {}\n".format(timediff, res))

        return res
        
    def shutdown(self):
        #TODO: cleanup
        self.write_to_server("quit")
        self.running = False

    def reset_server(self):
        self.wait_lock.acquire()
        self.write_to_server("restart")
        self.wait_lock.acquire()
        self.wait_lock.release()
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
