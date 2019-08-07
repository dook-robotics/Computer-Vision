import os
import atexit
from pynput import keyboard

# Define exit function
def stopListen():
    listener.stop()
    print("Listener stoped")

# Define key listener
def on_press(key):
    global started
    global listen
    global doneReading

    try:
        if('{0}'.format(key.char) == 's' and not started):
            started = True
            start()

        if('{0}'.format(key.char) == 'l'):
            doneReading = True
            listen = False

        if('{0}'.format(key.char) == 'c' and started):
            fd = os.open(PARENT + C, os.O_WRONLY)
            string = PARENT + C + "Message#"
            os.write(fd,str.encode(string))
            os.close(fd)

        if('{0}'.format(key.char) == 'b' and started):
            fd = os.open(PARENT + B, os.O_WRONLY)
            string = PARENT + B + "Message#"
            os.write(fd,str.encode(string))
            os.close(fd)

        if('{0}'.format(key.char) == 'd' and started):
            fd = os.open(PARENT + C, os.O_WRONLY)
            string = PARENT + C + "$Message#"
            os.write(fd,str.encode(string))
            os.close(fd)

        if('{0}'.format(key.char) == 'g' and started):
            fd = os.open(PARENT + B, os.O_WRONLY)
            string = PARENT + B + "$Message#"
            os.write(fd,str.encode(string))
            os.close(fd)

    except AttributeError:
        return

def start():
    print("Starting Children...")
    child_pid = os.fork()
    if(child_pid == 0):
        os.system('python3 c.py')
        listen = False
    else:
        child_pid = os.fork()
        if(child_pid == 0):
            os.system('python3 b.py')
            listen = False


def listenForChildren(child):
    global doneReading
    buffer = ""
    childID = children[child % len(children)]
    print("listening", childID)
    fd = os.open(childID + PARENT, os.O_RDONLY) #C type open a file and return an int file descriptor
    os.set_blocking(fd, False) # setting the reader to NON_BLOCKING so if it reads from an empty pipe it does not yield until it receives data (continues its own code)

    doneReading = False
    readSomething = False
    string = ""

    if fd >=0: #check for error on opening the file
        i =0;
        while not doneReading:
            try:  #using a try catch block for if the reader opens the fifo before the writer and trys reading, the program wont crash due to an unneccessary error
                buffer = os.read(fd,1) #C type read of read from int file descriptor and read a number of bytes i.e 1
            except OSError as err:
                if err.errno == os.errno.EAGAIN or err.errno == os.errno.EWOULDBLOCK: #If one of these errors is detected treat it as nothing and reset our read variable to nothing
                    if not readSomething:
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
                    decodeMessage(string)
                    string = ""
            # else:
            #     doneReading = True
    else:
        print(rpath + " is not readable")
    os.close(fd)

def decodeMessage(string):
    sender = string[:3]
    if(sender == PARENT):
        handleMessage(string[6:])
    else:
        sendMessage(string)
    return

def sendMessage(string):
    sender = string[:3]
    rec = string[3:6]
    fd = os.open(PARENT+rec, os.O_WRONLY) #C type open a file and return an int file descriptor
    os.write(fd,str.encode(string))
    os.close(fd)
    return

def handleMessage(string):
    print(PARENT,"Handler:", string)
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

listener = keyboard.Listener(on_press=on_press)
listener.start()

c = 0
while listen:
    if(started):
        listenForChildren(c)
        print("Listening to next child")
        c = c+1
    continue
