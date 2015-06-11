
import subprocess
import threading
import sys

class TTDHandler():
    def start(self):
        print "gonna start"
        self.server = subprocess.Popen(["openttd", "-D"],
                                       stdin  = subprocess.PIPE,
                                       stdout = sys.stdout,
                                       stderr = sys.stderr)
        
        
    def add_ai(self, ai):
        #ignore ai for now
        print "hurrrrrr"
        self.server.stdin.write("start_ai\n")

    def shutdown(self):
        self.server.stdin.write("quit")
