
import sys
import time
import os

derpfile = open("derpfile", "a")
derpfile.write("{} {}\n".format(sys.argv[1], sys.argv[2]))
derpfile.flush()
os.fsync(derpfile.fileno())
time.sleep(30)
print('10')
