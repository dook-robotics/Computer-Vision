import os
import atexit
from pynput import keyboard
started = False
listen = True
i = 0
j = 0

def stopListen():
    listener.stop()
    print("Listener stoped")
atexit.register(stopListen)

def on_press(key):
    global started
    global i
    global j
    global listen
    try:
        if('{0}'.format(key.char) == 's' and not started):
            started = True
            start()
        if('{0}'.format(key.char) == 'l'):
            listen = False
        if('{0}'.format(key.char) == 'c' and started):
            fd = os.open('fifoac', os.O_WRONLY) #C type open a file and return an int file descriptor
            string = "From A to C: " + str(i) + "\n" #the String we will write to the pipe
            os.write(fd,str.encode(string))
            i = i + 1
            os.close(fd)
        if('{0}'.format(key.char) == 'b' and started):
            fd = os.open('fifoab', os.O_WRONLY) #C type open a file and return an int file descriptor
            string = "From A to B: " + str(j) + "\n" #the String we will write to the pipe
            os.write(fd,str.encode(string))
            j = j + 1
            os.close(fd)

    except AttributeError:
        return

def start():
    print()
    child_pid = os.fork()
    if(child_pid == 0):
        os.system('python3 c.py') #Same as writing a command in the terminal to start a python program
        listen = False
    else:
        child_pid = os.fork()
        if(child_pid == 0):
            os.system('python3 b.py') #Same as writing a command in the terminal to start a python program
            listen = False

listener = keyboard.Listener(on_press=on_press)
listener.start()

while listen:
    continue
