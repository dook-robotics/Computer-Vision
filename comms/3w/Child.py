import sys
import os
import atexit
#from apscheduler.scheduler import Scheduler

print("b.py started")

'''def stopSch():
   sched.shutdown()
    os.close(fd)'''

def sendMessage():
    global message
    fd = os.open(wpath, os.O_WRONLY) #C type open a file and return an int file descriptor
    os.write(fd,str.encode(message))
    os.close(fd)
    message = "001000emptyB#"
    return

## Start Script ##

message = "001000emptyB#"

rpath = "000001"
wpath = "001000"

atexit.register(stopSch)

'''sched = Scheduler()
sched.start()
sched.add_interval_job(sendMessage, seconds = 1)'''

fd = os.open(rpath, os.O_RDONLY) #C type open a file and return an int file descriptor
os.set_blocking(fd, False) # setting the reader to NON_BLOCKING so if it reads from an empty pipe it does not yield until it receives data (continues its own code)

while True:
    doneReading = False
    string = ""
    if fd >=0: #check for error on opening the file
        while not doneReading:
            try:  #using a try catch block for if the reader opens the fifo before the writer and trys reading, the program wont crash due to an unneccessary error
                buffer = os.read(fd,1) #C type read of read from int file descriptor and read a number of bytes i.e 1
            except OSError as err:
                if err.errno == os.errno.EAGAIN or err.errno == os.errno.EWOULDBLOCK: #If one of these errors is detected treat it as nothing and reset our read variable to nothing
                    buffer = None
                    doneReading = True;# we read everything in the pipe
                else:
                    raise  # otherwise raise the exception because it is not something we were expecting/handling ourselves

            if buffer is not None: #if we read something, print that what we read and that we are done reading
                string = string + buffer.decode()
				
		if(string != "" and string[len(string)-1] == '#'):
            if("$" in string):
				message = "001000TestB#"
				sendMessage()
				string = ""
			else:
				print("B: ", string)
				string = ""
		else if string!="":
			print("Failure to end message in fifo with \'#\'")
			
    else:
        print( path + " is not readable")