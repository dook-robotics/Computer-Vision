## Comms Parent ##
# Authors: Mikian, Austin

import os
import atexit
from pynput import keyboard

# Define exit function
# Stop Keyboard listeners
# TODO: Should send signals to children to stop schd
def stopListen():
    listener.stop()
    for index in range(0,len(children)):
        os.close(fdr[index])
        # os.close(fdw[index])
    print("Listeners Stoped")
    print("Program Exit Successfully")

# Start child processes
# TODO: Make this into a loop through child names
def start():
    print("Starting Children...")
    child_pid = os.fork()
    if(child_pid == 0):
        os.system('python3 c.py')
        exit()
    else:
        child_pid = os.fork()
        if(child_pid == 0):
            os.system('python3 b.py')
            exit()

# Main listen loop/Function
def listenForChildren(child):
    buffer = None
    childID = child % len(children)
    #os.set_blocking(fd, False) # setting the reader to NON_BLOCKING so if it reads from an empty pipe it does not yield until it receives data (continues its own code)
    doneReading = False
    string = ""
    if fdr[childID] >=0: #check for error on opening the file
        while not doneReading:
            try:  #using a try catch block for if the reader opens the fifo before the writer and trys reading, the program wont crash due to an unneccessary error
                buffer = os.read(fdr[childID],1) #C type read of read from int file descriptor and read a number of bytes i.e 1
            except OSError as err:
                print("error.errno is ", err.errno)
                if err.errno == os.errno.EAGAIN or err.errno == os.errno.EWOULDBLOCK: #If one of these errors is detected treat it as nothing and reset our read variable to nothing

                    buffer = None
                    doneReading = True
                else:
                    print("here in else")
                      # otherwise raise the exception because it is not something we were expecting/handling ourselves

            # print(buffer is not None) this is true most of the time even when not reading...
            if buffer is not None: #if w3e read something, print that what we read and that we are done reading
                if(buffer.decode() == "#"):
                    doneReading = True
                string = string + buffer.decode()

        if(string != "" and string[len(string)-1] == '#'):
            buffer = None
            decodeMessage(string)
            string = ""
        elif string !="":
            print("Failure to end message in fifo with \'#\'")

    else:
        print(rpath + " is not readable")

def decodeMessage(string):
    rec = string[3:6]
    if(rec == PARENT):
        handleMessage(string[6:])
    else:
        sendMessage(string)
    return

def sendMessage(string):
    sender = string[:3]
    rec = string[3:6]
    index =0
    for index in range(0,len(children)):
        if children[index] == rec:
            break
    os.write(fdr[index],str.encode(string))
    return

def handleMessage(string):
    print(PARENT,"Handler:", string)
    return

# Define key listener
def on_press(key):
    global started
    try:
        # Start child scripts
        if('{0}'.format(key.char) == 's' and not started):
            started = True
            start()

        # Send message to C
        if('{0}'.format(key.char) == 'c' and started):
            fd = os.open(PARENT + C, os.O_WRONLY)
            string = PARENT + C + "Message#"
            os.write(fd,str.encode(string))
            os.close(fd)

        # Send message to B
        if('{0}'.format(key.char) == 'b' and started):
            fd = os.open(PARENT + B, os.O_WRONLY)
            string = PARENT + B + "Message#"
            os.write(fd,str.encode(string))
            os.close(fd)

        # Send message to C to send a message to B
        if('{0}'.format(key.char) == 'd' and started):
            fd = os.open(PARENT + C, os.O_WRONLY)
            string = PARENT + C + "$Message#"
            os.write(fd,str.encode(string))
            os.close(fd)

        # Send message to B to send a message to C
        if('{0}'.format(key.char) == 'g' and started):
            fd = os.open(PARENT + B, os.O_WRONLY)
            string = PARENT + B + "$Message#"
            os.write(fd,str.encode(string))
            os.close(fd)

    except AttributeError:
        return

## START SCRIPT ##

# set exit function
atexit.register(stopListen)

# Define Program IDs
PARENT = "000"
B      = "001"
C      = "010"

# Children of parent
children = [B, C]

# Define bools for loops
doneReading = False
started = False
listen = True

os.system('python s.py')

fdr = []
for index in range(0,len(children)):
    fdr.append(os.open(children[index] + PARENT, os.O_RDONLY | os.O_NONBLOCK))

listener = keyboard.Listener(on_press=on_press)
listener.start()

c = 0
while True:
    if(started):
        listenForChildren(c)
        c = c+1
    continue
