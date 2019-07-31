# Do not call this program on its own. This program is a test to show that a parent process can start
# two new process and also test that those processes can have a channel of communication between them
# namely the fifo 'ReadWriteBuffer' use the program RootParentPython


import sys
import os


path = "ReadWriteBuffer" # name of the fifo i had created using mkfifo command in my terminal 'mkfifo ReadWriteBuffer'


def reader():
    fd = os.open(path, os.O_RDONLY) #C type open a file and return an int file descriptor
    os.set_blocking(fd, False) # setting the reader to NON_BLOCKING so if it reads from an empty pipe it does not yield until it receives data (continues its own code)
    doneReading = False
    readSomething = False
    string = ""
    if fd >=0: #check for error on opening the file
        i =0;
        print("Starting read")
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
            else:
                print("Still have not read anything") #when we read from the pipe, it was empty
    else:
        print( path + " is not readable")

    print("Done Reading!")
    os.close(fd)
    print(string)
    return



def writer():
    fd = os.open(path, os.O_WRONLY) #C type open a file and return an int file descriptor
    string = "Hello World!" #the String we will write to the pipe
    i =0
    while i != 100: #loop to make the writer stall before writing to test the reader's NON_BLOCKING status
        i = i+1
    os.write(fd,str.encode(string))
    print("Done Writing!")
    os.close(fd)
    return


if len(sys.argv) != 2: #Handle improper call of this program
	print("not enough arguments passed")
	exit()

if str(sys.argv[1]) == "Reader": #Handle Reader
    reader()
elif str(sys.argv[1]) == "Writer": #Handler Writer
    writer()

exit()
