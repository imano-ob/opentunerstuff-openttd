
import subprocess
import threading
import sys

class TTDHandler():
    def __init__(self):
        self.lock = threading.Lock()
    
    def start(self):
        print "gonna start"
        self.server = subprocess.Popen(["openttd", "-D"],
                                       stdin  = subprocess.PIPE,
                                       stdout = sys.stdout,
                                       stderr = sys.stderr)
        
        
    def add_ai(self, ai):
        #ignore ai for now
        self.lock.acquire()
        print threading.activeCount()
        self.server.stdin.write("start_ai\n")
        self.lock.release()

    def shutdown(self):
        self.server.stdin.write("quit")
