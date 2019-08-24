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

import RPi.GPIO as GPIO                    #Import GPIO library
import time
import atexit

## Movement Setup ##

idleBool = True
#Import time library
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)                    # programming the GPIO by BCM pin numbers

TRIG = 18
ECHO = 27

PWM1=17
DIR1=22
PWM2=23
DIR2=24           

GPIO.setup(TRIG,GPIO.OUT)                  # initialize GPIO Pin as outputs
GPIO.setup(ECHO,GPIO.IN)                   # initialize GPIO Pin as input

GPIO.setup(DIR1,GPIO.OUT)
GPIO.setup(PWM1,GPIO.OUT)
GPIO.setup(DIR2,GPIO.OUT)
GPIO.setup(PWM2,GPIO.OUT)

pwm=GPIO.PWM(PWM1,100)
pwm2=GPIO.PWM(PWM2,100)
pwm.start(0)
pwm2.start(0)

#time.sleep(5)

USCNT = 0
## Finish movement setup ##

def stop():
    print("stop")
    pwm.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)
#    GPIO.output(PWM1,GPIO.LOW)
#    GPIO.output(DIR1,GPIO.LOW)
#    GPIO.output(PWM2,GPIO.LOW)
#    GPIO.output(DIR2,GPIO.LOW)

def forward():
    pwm.ChangeDutyCycle(25)
    pwm2.ChangeDutyCycle(25)
    GPIO.output(PWM1,GPIO.HIGH)
    GPIO.output(DIR1,GPIO.LOW)
    GPIO.output(PWM2,GPIO.HIGH)
    GPIO.output(DIR2,GPIO.LOW)
    print("Forward")

def back():
    pwm.ChangeDutyCycle(25)
    pwm2.ChangeDutyCycle(25)
    GPIO.output(PWM1,GPIO.LOW)
    GPIO.output(DIR1,GPIO.HIGH)
    GPIO.output(PWM2,GPIO.LOW)
    GPIO.output(DIR2,GPIO.HIGH)
    print("back")

def left():
    pwm.ChangeDutyCycle(25)
    pwm2.ChangeDutyCycle(0)
    GPIO.output(PWM1,GPIO.HIGH)
    GPIO.output(DIR1,GPIO.LOW)
    GPIO.output(PWM2,GPIO.LOW)
    GPIO.output(DIR2,GPIO.LOW)
    print("left")

def right():
    pwm2.ChangeDutyCycle(25)
    pwm.ChangeDutyCycle(0)
    GPIO.output(PWM1,GPIO.LOW)
    GPIO.output(DIR1,GPIO.LOW)
    GPIO.output(PWM2,GPIO.HIGH)
    GPIO.output(DIR2,GPIO.LOW)
    print("right")

def idle():
    global USCNT
    print("idling")
    i=0
    avgDistance=0
    for i in range(5):
        GPIO.output(TRIG, False)                 #Set TRIG as LOW
        time.sleep(0.1)                                   #Delay

        GPIO.output(TRIG, True)                  #Set TRIG as HIGH
        time.sleep(0.00001)                           #Delay of 0.00001 seconds
        GPIO.output(TRIG, False)                 #Set TRIG as LOW

        while GPIO.input(ECHO)==0:              #Check whether the ECHO is LOW

            pulse_start = time.time()

        while GPIO.input(ECHO)==1:              #Check whether the ECHO is HIGH

            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start #time to get back the pulse to sensor

        distance = pulse_duration * 17150        #Multiply pulse duration by 17150 (34300/2) to get distance
        distance = round(distance,2)                 #Round to two decimal points
        avgDistance=avgDistance+distance

    avgDistance=avgDistance/5
    print (avgDistance)
    flag=0


    if avgDistance < 45:      #Check whether the distance is within 45 cm range
        USCNT=USCNT+1
        stop()
        #time.sleep(1)
        back()
        #time.sleep(1.5)
        if (USCNT ==3) & (flag==0):
            USCNT = 0
            right()
            flag=1
        else:
            left()
            flag=0
            #time.sleep(1.5)
            stop()
            #time.sleep(1)
    else:
        forward()
        flag=0
    return

def handleMessage(message):
    print(message)
    global idleBool
    if message == "L":
        left()
        idleBool = False
    elif message == "R":
        right()
        idleBool = False
    elif message == "F":
        forward()
        idleBool = False
    elif message == "I":
        #idle()
        idleBool = True
    elif message == "B":
        back()
        idleBool = False
    else:
        print("Error")
    return



# Loop to read from fifo
def listen():
    #print("listening")
    global fd
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
                    
                    buffer = b''
                else:
                    doneReading = True
            else:
                raise

        if buffer != b'':
            #print("read something")
            readSomthing = True
            string = string + buffer.decode()
            if string != "" and string[len(string)-1] == '#':
                buffer = None
                if "$" in string:
                    # Send message
                    handleMessage(string[1])
                    string = ""
                else:
                    print("Unknown Syntax:", string)
                    string = ""
        else:
            #print("read nothing")
            doneReading = True
        
    return

def stopListen():
    GPIO.cleanup()
    os.close(fd)
    return

atexit.register(stopListen)

# Open pipe
fifo = 'fifo1'
fd = os.open(fifo, os.O_RDONLY | os.O_NONBLOCK)
if fd >= 0:
    print("Pipe open")
else:
    print("Error: No pipe named", fifo)
#os.set_blocking(fd, False)
while True:
    listen()
    if idleBool:
        idle()
    
    


