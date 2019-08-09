import sys
import os
import atexit
from apscheduler.scheduler import Scheduler

print("c.py started")

def stopSch():
    sched.shutdown()
    os.close(fd)

def sendMessage():
    global message
    fd = os.open(wpath, os.O_WRONLY) #C type open a file and return an int file descriptor
    os.write(fd,str.encode(message))
    os.close(fd)
    message = "001000emptyC#"
    return

## Start Script ##

message = "010000emptyC#"

wpath = "010000"
rpath = "000010"

atexit.register(stopSch)

sched = Scheduler()
sched.start()
sched.add_interval_job(sendMessage, seconds = .1)

fd = os.open(rpath, os.O_RDONLY) #C type open a file and return an int file descriptor
os.set_blocking(fd, False) # setting the reader to NON_BLOCKING so if it reads from an empty pipe it does not yield until it receives data (continues its own code)

while True:
    doneReading = False
    readSomething = False
    string = ""
    if fd >= 0:
        i = 0
        while not doneReading:
            try:
                buffer = os.read(fd,1) #C type read of read from int file descriptor and read a number of bytes i.e 1
            except OSError as err:
                if err.errno == os.errno.EAGAIN or err.errno == os.errno.EWOULDBLOCK: #If one of these errors is detected treat it as nothing and reset our read variable to nothing
                    if readSomething is not True:
                        buffer = None
                    else:
                        doneReading = True;# we read everything in the pipe
                else:
                    raise  # otherwise raise the exception because it is not something we were expecting/handling ourselves

            if buffer is not None: #if we read something, print that what we read and that we are done reading
                readSomething = True;
                string = string + buffer.decode()
                if(string != "" and string[len(string)-1] == '#'):
                    buffer = None
                    if("$" in string):
                        message = "010000TestC#"
                        string = ""
                    else:
                        print("C: ", string)
                        string = ""
    else:
        print(rpath + " is not readable")
