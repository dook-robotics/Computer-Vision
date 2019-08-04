import sys
import os

# A writes, C reads
wpath = "fifoca" # name of the fifo i had created using mkfifo command in my terminal 'mkfifo fifobc'
rpath = "fifoac" # name of the fifo i had created using mkfifo command in my terminal 'mkfifo fifobc'

fd = os.open(rpath, os.O_RDONLY) #C type open a file and return an int file descriptor
os.set_blocking(fd, False) # setting the reader to NON_BLOCKING so if it reads from an empty pipe it does not yield until it receives data (continues its own code)

while True:
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
                    if readSomething is not True:
                        buffer = None
                    else:
                        doneReading = True;# we read everything in the pipe
                else:
                    raise  # otherwise raise the exception because it is not something we were expecting/handling ourselves

            if buffer is not None: #if we read something, print that what we read and that we are done reading
                readSomething = True;
                string = string + buffer.decode()
                if(string != "" and string[len(string)-1] == '\n'):
                    buffer = None
                    if(string == "sendb"):
                        print("send message to b")
                    else:
                        print("c: ", string)
                        string = ""
    else:
        print(rpath + " is not readable")

os.close(fd)
