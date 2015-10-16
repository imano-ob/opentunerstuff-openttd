
# -*- coding: UTF-8 -*-

import subprocess
import threading
import sys
import time
import os
import config

class TTDHandler():
    def __init__(self,
                 #Maximo 15
                 ais_per_round = 8):

        self.ais_per_round = ais_per_round
        self.started_ais = 0
        self.active_ais = 0
        self.running = False
        
        self.bufs = {}
                
        #Mutex de variaveis internas do handler
        self.handler_lock = threading.Lock()

        #Lock para não ter mais IAs do que o permitido rodando
        self.add_ai_lock = threading.Lock()

        #Mutex de escrita no servidor
        self.server_in_lock = threading.Lock()

        #Locks de espera de resultados
        self.result_locks = {}

        #Mutex de coisas que dependem de resposta de servidor
        self.res_lock = threading.Lock()
        
        #Lock para esperar servidor estar rodando
        self.wait_lock = threading.Lock()
        self.server_started = threading.Condition(self.wait_lock)

        #Lock para esperar AI morrer
        #self.stop_ai_lock = threading.Lock()
        #self.ai_stopped = threading.Condition(self.stop_ai_lock)
        
        #Esperas de resposta de server
        self.waiting = {}
        
        #Mutex de escrita de log
        self.log_lock = threading.Lock()
        
        #Log de resultados
        self.start_time = time.time()
        i = 0
        logname = "logfile{}.log".format(i) 
        while os.path.exists(logname):
            i += 1
            logname = "logfile{}.log".format(i) 
        self.logfile = open(logname, "w")

        self.ttd_command = config.ttd_command

################################################
# start
################################################
        
    def start(self, args = None):
        if self.running:
            #OhNoes!
            #construir exceção/retornar algo?
            raise
        if args == None:
            args = [self.ttd_command,
                    "-D",
                    "-d5"]
            print "heyo"
            #para caso shell = True
       #     args = self.ttd_command + " -D -d script=5"
        else:
            print "huh"
        self.server = subprocess.Popen(args,
                                       #Dunno
                                       # shell = True,
                                       #Dunno as well
                                       bufsize = 1,
                                       stdin  = subprocess.PIPE,
                                       stdout = subprocess.PIPE,
                                       stderr = subprocess.STDOUT)
        self.read_thread = threading.Thread(target = self.read_output)
        self.server_started.acquire()
        self.read_thread.start()
        self.server_started.wait(10)
        self.running = True

################################################
# start_ai
################################################
        
    def start_ai(self, ai, ai_id):

        #management stuff
        print "starting AI"
        self.add_ai_lock.acquire()
        self.handler_lock.acquire()
        self.started_ais += 1
        self.active_ais += 1
        if ai_id not in self.bufs.keys():
            self.bufs[ai_id] = []
        self.handler_lock.release()
        if self.started_ais < self.ais_per_round:
            self.add_ai_lock.release()

        print "start and get result lock {}".format(ai_id)
        self.result_locks[ai_id] = threading.Lock()
        self.result_locks[ai_id].acquire()
#        print "self result locks -> ",self.result_locks
#        print "self result lock[id]-> ",self.result_locks[ai_id]
        
        #server communication
        cmd = "rescan_ai"
        self.write_to_server(cmd)
        cmd = "start_ai {}".format(ai)
        self.write_to_server(cmd)

################################################
# stop_ai
################################################
        
    def stop_ai(self, ttd_id, ai_id):
        cmd = "stop_ai {}".format(ttd_id + 1) #reasons
        print "Gonna stop an AI"
        self.write_and_wait_response(cmd, "AI stopped")
        self.active_ais -= 1
        if self.active_ais == 0 and self.started_ais == self.ais_per_round:
            print "Resettin'"
            self.reset_server()
        print "Release the lock {}".format(ai_id)
        print "self result locks -> ",self.result_locks
        print "self result lock[id]-> ",self.result_locks[ai_id]
        self.result_locks[ai_id].release()

################################################
# read_output
################################################

    def read_output(self):
        while True:
            self.res_lock.acquire()
            last_line = self.server.stdout.readline()
            self.res_lock.release()
            if last_line == '':
                return
            #Easier on the eyes on debugs
            last_line = last_line.replace('\n', '')
#            print last_line
            for k in self.waiting.keys():
                if k in last_line:
                    #print last_line
                    self.waiting[k].acquire()
                    self.waiting[k].notify()
                    self.waiting[k].release()
                    del(self.waiting[k])
            if "[tuner]" in last_line:
                ai_id, ttd_id, content = self.parse(last_line)
            else:
                continue
            print "I got something"
            self.bufs[ai_id].append(content)
            self.stop_ai(ttd_id, ai_id)

################################################
# parse
################################################

    def parse(self, line):
        #AIs: output começa com <alguma coisa>[script] <-- Eu acho que o alguma coisa é dbg:
        #São da forma <alguma coisa>[script][<ID>][<Error/Warning/Info>] <Texto>
        #AIs devem ter output da forma [tuner][<Tuner ID>][<Resultado>] for
        #simplicity's sake

        #Redundancia
        if not "[tuner]" in line:
            return None, None, None
        tmp = line.split(']')
        #Campos restantes são irrelevantes para nossos propósitos
        #TODO: Possivelmente certificar que vai continuar funcionando
        #no futuro
        for i in tmp:
            print i
        ai_id = int(tmp[4].replace('[', ''))
        print "ai id -> ", ai_id
        ttd_id = int(tmp[1].replace('[',''))
        print "ttd id -> ", ttd_id
        content = int(tmp[5].replace('[',''))
        print "content -> ", content
        print "handler leu -> {} {} {}".format(ai_id, ttd_id, content)

        return ai_id, ttd_id, content

################################################
# result
################################################

    def result(self, ai_id):
        print "waiting for result"
        self.result_locks[ai_id].acquire()
        res = int(self.bufs[ai_id].pop())
        print "result get"
        self.result_locks[ai_id].release()

        #print "Getting rid of locks yo"
        #del self.bufs[ai_id]
        #del self.result_locks[ai_id]

        timediff = time.time() - self.start_time
        self.log_lock.acquire()
        self.logfile.write("id: {}, time: {}, res: {}\n".format(ai_id, timediff, res))
        self.logfile.flush()
        os.fsync(self.logfile.fileno())
        self.log_lock.release()
        return res

################################################
# shutdown
################################################
    
    def shutdown(self):
        #TODO: cleanup
        self.write_to_server("quit")
        self.running = False
        self.logfile.close()

################################################
# reset_server
################################################

    def reset_server(self):
        #self.write_to_server("restart")
        self.write_and_wait_response("restart", "game started")
        self.handler_lock.acquire()
        self.started_ais = 0
        self.active_ais = 0
        self.handler_lock.release()
        self.add_ai_lock.release()
        
################################################
# write_and_wait_response
################################################

    def write_and_wait_response(self, msg, response, condition = None, timeout = 10):
        if not condition:
            condition = threading.Condition()
        self.res_lock.acquire()
        self.waiting[response] = condition
        condition.acquire()
        self.res_lock.release()
        self.write_to_server(msg)
        condition.wait(timeout)
        
################################################
# write_to_server
################################################

    def write_to_server(self, msg):
        #Tempo para garantir que o server leu e entendeu a mensagem
        sleep_time = 0.5
        #Coderproofing
        msg += '\n'
        self.server_in_lock.acquire()
        print('to server ->' + msg)
        self.server.stdin.write(msg)
        time.sleep(sleep_time)
        self.server_in_lock.release()
