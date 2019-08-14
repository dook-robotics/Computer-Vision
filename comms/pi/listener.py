## listener.py ##
## Listen for movement commands from OD script ##
#
# Authors:
#   Mikian Musser - https://github.com/mm909
#   Eric Becerril-Blas - https://github.com/lordbecerril
#   Zoyla O - https://github.com/ZoylaO
#   Austin Janushan - https://github.com/Janushan-Austin
#   Giovanny Vazquez - https://github.com/giovannyVazquez
#
# Organization:
#   Dook Robotics - https://github.com/dook-robotics
#
# Usage:
#   python listener.py
#
# Documentation:
#
#

import sys
import os
import errno

def handleMessage(message):
    return

# Open pipe
fifo = 'fifo1'
fd = os.open(fifo, os.O_RDONLY)
if fd >= 0:
    print("Pipe open")
else:
    print("Error: No pipe named", fifo)
os.set_blocking(fd, False)

# Loop to read from fifo
while True:

    doneReading = False
    readSomething = False
    string = ""
    i = 0

    while not doneReading:
        try:
            buffer = os.read(fd,1)
        except OSError as err:
            if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
                if not readSomething:
                    buffer = None
                else:
                    doneReading = True
            else:
                raise

        if buffer is not None:
            readSomthing = True
            string = string + buffer.decode()
            if string != "" and string[len(string)-1] == '#':
                buffer = None
                if "$" in string:
                    # Send message
                    handleMessage(string)
                    string = ""
                else:
                    print("Unknown Syntax:", string)
                    string = ""
    else:
        print("File not readable")

os.close(fd)
