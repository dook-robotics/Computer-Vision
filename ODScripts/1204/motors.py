## motors.py ##
## functions for the motors ##
#
# Authors:
#   Mikian Musser      - https://github.com/mm909
#   Eric Becerril-Blas - https://github.com/lordbecerril
#   Zoyla Orellana     - https://github.com/ZoylaO
#   Austin Janushan    - https://github.com/Janushan-Austin
#   Giovanny Vazquez   - https://github.com/giovannyVazquez
#   Ameera Essaqi      - https://github.com/AmeeraE
#   Brandon Herrera    - herrer10@unlv.nevada.edu
#   Esdras Morales     - morale2@unlv.nevada.edu
#
# Organization:
#   Dook Robotics - https://github.com/dook-robotics

import time
import math
import RPi.GPIO as GPIO

# Motor Power
ManPower  = 60 #25.0
AutoPower = 15

# LEFT Motor Pins
PWM1 = 17
DIR1 = 22

# RIGHT Motor Pins
PWM2 = 23
DIR2 = 24

# US Pins
TRIG_L = 18
ECHO_L = 27
TRIG_R = 19
ECHO_R = 26

# Counter for US frames
USCNT = 0

# Programming the GPIO by BCM pin numbers
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Initialize GPIO Pins for Motor
GPIO.setup(DIR1,GPIO.OUT)
GPIO.setup(PWM1,GPIO.OUT)
GPIO.setup(DIR2,GPIO.OUT)
GPIO.setup(PWM2,GPIO.OUT)

# Initialize GPIO Pins for US
GPIO.setup(TRIG_L,GPIO.OUT)
GPIO.setup(ECHO_L,GPIO.IN)
GPIO.setup(TRIG_R,GPIO.OUT)
GPIO.setup(ECHO_R,GPIO.IN)

# Set frequency of PWM
pwm  = GPIO.PWM(PWM1, 750)
pwm2 = GPIO.PWM(PWM2, 750)

# Initialize
pwm.start(0)
pwm2.start(0)

oldL = 0
oldR = 0

def manMotors(ud, lr):
    global oldL
    global oldR
    savedUD = ud
    savedLR = lr

    hyp     = math.sqrt(ud * ud + lr * lr)
    normhyp = min(1, hyp)

    if(hyp != 0):
        scale = normhyp / hyp
    else:
        scale = 1

    ud *= scale
    lr *= scale
    hyp = normhyp
    ud  = abs(ud)

    powerR = 0
    powerL = 0
    if lr > 0:
        powerL = hyp
        powerR = ud
    else:
        powerR = hyp
        powerL = ud

    dir1 = 0
    dir2 = 0

    if ud >= -0.1 and ud <= 0.1:
        ud = 0.0
    if savedUD <= 0.0:
       dir2 = GPIO.HIGH
       dir1 = GPIO.LOW
    elif savedUD > 0.0:
        dir2 = GPIO.LOW
        dir1 = GPIO.HIGH

    powerL = round(powerL,2) * ManPower
    powerR = round(powerR,2) * ManPower

    if oldR != powerR or oldL != powerL:
        oldR = powerR
        oldL = powerL
        print(oldL, oldR)
        setMotors(powerL, powerR, GPIO.HIGH, dir1, GPIO.HIGH, dir2)

def setMotors(pwmval, pwm2val, PWM1val, DIR1val, PWM2val, DIR2val):
    pwm.ChangeDutyCycle(pwmval)   # Left
    pwm2.ChangeDutyCycle(pwm2val) # Right
    GPIO.output(PWM1, GPIO.HIGH)
    GPIO.output(PWM2, GPIO.HIGH)
    GPIO.output(DIR1, DIR1val)
    GPIO.output(DIR2, DIR2val)
    return

# This function needs to be changed to non blocking
def runMotorsNonBlocking():
    startTime = time.time()
    pwm.ChangeDutyCycle(AutoPower)
    pwm2.ChangeDutyCycle(AutoPower)
    GPIO.output(PWM1,GPIO.HIGH)
    GPIO.output(DIR1,GPIO.LOW)
    GPIO.output(PWM2,GPIO.HIGH)
    GPIO.output(DIR2,GPIO.HIGH)
    return startTime

def runMotors(seconds):
    print("Running motors for " + str(seconds) + " seconds.")
    startTime = time.time();
    elapsedTime = time.time() - startTime
    pwm.ChangeDutyCycle(AutoPower)
    pwm2.ChangeDutyCycle(AutoPower)
    GPIO.output(PWM1,GPIO.HIGH)
    GPIO.output(DIR1,GPIO.LOW)
    GPIO.output(PWM2,GPIO.HIGH)
    GPIO.output(DIR2,GPIO.HIGH)
    while elapsedTime < seconds:
        elapsedTime = time.time() - startTime
    stop()
    return


def stop():
    print("Stop")
    pwm.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)

def forward():
    print("Forward")
    pwm.ChangeDutyCycle(AutoPower + 6.25)
    pwm2.ChangeDutyCycle(AutoPower)
    GPIO.output(PWM1,GPIO.HIGH)
    GPIO.output(DIR1,GPIO.LOW)
    GPIO.output(PWM2,GPIO.HIGH)
    GPIO.output(DIR2,GPIO.HIGH)

def back():
    print("Back")
    pwm.ChangeDutyCycle(AutoPower + 5 + 6.25)
    pwm2.ChangeDutyCycle(AutoPower + 5)
    GPIO.output(PWM1,GPIO.LOW)
    GPIO.output(DIR1,GPIO.HIGH)
    GPIO.output(PWM2,GPIO.LOW)
    GPIO.output(DIR2,GPIO.LOW)

def left():
    print("Left")
    pwm.ChangeDutyCycle(16)
    pwm2.ChangeDutyCycle(8)
    GPIO.output(PWM1,GPIO.HIGH)
    GPIO.output(DIR1,GPIO.HIGH)
    GPIO.output(PWM2,GPIO.HIGH)
    GPIO.output(DIR2,GPIO.HIGH)

def right(boost = 0):
    print("Right")
    pwm2.ChangeDutyCycle(10 + boost)
    pwm.ChangeDutyCycle(8 + boost)
    GPIO.output(PWM1,GPIO.HIGH)
    GPIO.output(DIR1,GPIO.LOW)
    GPIO.output(PWM2,GPIO.HIGH)
    GPIO.output(DIR2,GPIO.LOW)



def idle():
    print("IDLING")
    
    #stop()
    #time.sleep(0.5)
    #i = 0 # Needed?
    avgDistance1 = 0

    for i in range(5):
        notRead = False

        # Take US Reading
        GPIO.output(TRIG_L, False)

        time.sleep(0.00001)
        GPIO.output(TRIG_L, True)

        time.sleep(0.00001)
        GPIO.output(TRIG_L, False)


        # Check whether the ECHO is LOW
        while GPIO.input(ECHO_L) == 0:
            pulse_start1 = time.time()


        if GPIO.input(ECHO_L) != 1:
            notRead = True

        # Check whether the ECHO is HIGH
        while GPIO.input(ECHO_L) == 1:
            pulse_end1 = time.time()

        if not notRead:
                 # Time to get back the pulse to sensor
            pulse_duration1 = pulse_end1 - pulse_start1


            #Multiply pulse duration by 17150 (34300/2) to get distance
            distance1 = pulse_duration1 * 17150
            distance1 = round(distance1, 2)
            avgDistance1 = avgDistance1 + distance1
        else:
            avgDistance1 = -5

    avgDistance1 = avgDistance1 / 5

    #print("USL:", avgDistance1)
    #i = 0

    avgDistance2 = 0
    for i in range(5):
        notRead = False
        # Take US Reading

        GPIO.output(TRIG_R, False)
        time.sleep(0.00001)

        GPIO.output(TRIG_R, True)
        time.sleep(0.00001)

        GPIO.output(TRIG_R, False)

        # Check whether the ECHO is LOW

        while(GPIO.input(ECHO_R) == 0):
            pulse_start2 = time.time()

        # Check whether the ECHO is HIGH

        if GPIO.input(ECHO_R) != 1:
            notRead = True

        while GPIO.input(ECHO_R) == 1:
            pulse_end2 = time.time()

        # Time to get back the pulse to sensor

        if not notRead:
            pulse_duration2 = pulse_end2 - pulse_start2

            #Multiply pulse duration by 17150 (34300/2) to get distance
            distance2 = pulse_duration2 * 17150
            distance2 = round(distance2, 2)
            avgDistance2 = avgDistance2 + distance2
        else:
            avgDistance2 = -5


    avgDistance2 = avgDistance2 / 5

    #print("USR:", avgDistance2)
    print("USL:", avgDistance1, "USR:", avgDistance2)
    
    # Check whether the distance is within 45 cm range
    # This could be a much better alg, without sleeps...
    if avgDistance1 < 30 and avgDistance2 < 30:
        #exit()
        #back()
	#uninteruptable back
        currIdleTime = time.time()
        back()
        time.sleep(3)
        #while time.time() - currIdleTime < 1.0:
            
            
         #   sleep(0.2)
        return time.time()
    else:
        forward()
        return 0

