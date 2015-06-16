
import subprocess
import threading
import sys
import time

class TTDHandler():
    def __init__(self):
        self.server_in_lock = threading.Lock()
        self.server_out_locks = {}
        self.server_in_locks = {}
        self.bufs = {}
        
    def start(self):
        self.server = subprocess.Popen(["openttd",
                                        "-D"],
                                       stdin  = subprocess.PIPE,
                                       stdout = subprocess.PIPE,
                                       stderr = subprocess.STDOUT)
        self.read_thread = threading.Thread(target = self.read_output)
                
    def add_ai(self, ai, ai_id):

        #management stuff
        self.server_out_locks[ai_id] = threading.Lock()
        self.server_in_locks[ai_id] = threading.Lock()

        #server communication
        self.server_in_lock.acquire()   
        self.server.stdin.write("start_ai {}\n".format(ai))
        self.server_in_lock.release()

    def read_output(self):
        while True:
            last_line = self.server.stdout.readline()
            ai_id, content = self.parse(last_line)
            if ai_id == None:
                continue
            self.server_out_locks[ai_id].acquire()
            #...huh. acho que isso pode nao fazer sentido
            #depende se a ai no final vai cuspir mais de uma mensagem?
            self.bufs[ai_id] = content
            self.server_out_locks[ai_id].release()
            self.server_in_locks[ai_id].release()
        
    def result(self, ai_id):
        #temp codez
        time.sleep(10)
        return 10
        #real codez
        #TODO: cleanup
        self.server_in_locks[ai_id].acquire()
        return self.bufs[ai_id]
        
    def shutdown(self):
        #TODO: cleanup
        self.server.stdin.write("quit\n")
