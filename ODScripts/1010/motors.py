import time
import RPi.GPIO as GPIO

# Motor Pins
PWM1=17
DIR1=22
PWM2=23
DIR2=24

# US Pins
TRIG_L = 18
ECHO_L = 27

TRIG_R = 19
ECHO_R = 26

USCNT = 0

# programming the GPIO by BCM pin numbers
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# initialize GPIO Pins for Motor
GPIO.setup(DIR1,GPIO.OUT)
GPIO.setup(PWM1,GPIO.OUT)
GPIO.setup(DIR2,GPIO.OUT)
GPIO.setup(PWM2,GPIO.OUT)

# initialize GPIO Pins for US
GPIO.setup(TRIG_L,GPIO.OUT)
GPIO.setup(ECHO_L,GPIO.IN)

GPIO.setup(TRIG_R,GPIO.OUT)
GPIO.setup(ECHO_R,GPIO.IN)


# Set frequency of PWM
pwm = GPIO.PWM(PWM1, 100)
pwm2 = GPIO.PWM(PWM2, 100)

# Initialize
pwm.start(0)
pwm2.start(0)

def setMotors(pwmval, pwm2val, PWM1val, DIR1val, PWM2val, DIR2val):
    pwm.ChangeDutyCycle(pwmval) # Left
    pwm2.ChangeDutyCycle(pwm2val) # Right
    GPIO.output(PWM1, PWM1val)
    GPIO.output(DIR1, DIR1val)
    GPIO.output(PWM2, PWM2val)
    GPIO.output(DIR2, DIR2val)
    return

def stop():
    print("Stop")
    pwm.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)

def forward():
    print("Forward")
    pwm.ChangeDutyCycle(25)
    pwm2.ChangeDutyCycle(25)
    GPIO.output(PWM1,GPIO.HIGH)
    GPIO.output(DIR1,GPIO.LOW)
    GPIO.output(PWM2,GPIO.HIGH)
    GPIO.output(DIR2,GPIO.LOW)

def back():
    print("Back")
    pwm.ChangeDutyCycle(25)
    pwm2.ChangeDutyCycle(25)
    GPIO.output(PWM1,GPIO.LOW)
    GPIO.output(DIR1,GPIO.HIGH)
    GPIO.output(PWM2,GPIO.LOW)
    GPIO.output(DIR2,GPIO.HIGH)

def left():
    print("Left")
    pwm.ChangeDutyCycle(25)
    pwm2.ChangeDutyCycle(0)
    GPIO.output(PWM1,GPIO.HIGH)
    GPIO.output(DIR1,GPIO.LOW)
    GPIO.output(PWM2,GPIO.LOW)
    GPIO.output(DIR2,GPIO.LOW)

def right():
    print("Right")
    pwm2.ChangeDutyCycle(25)
    pwm.ChangeDutyCycle(0)
    GPIO.output(PWM1,GPIO.LOW)
    GPIO.output(DIR1,GPIO.LOW)
    GPIO.output(PWM2,GPIO.HIGH)
    GPIO.output(DIR2,GPIO.LOW)



def idle():
    print("IDLING")

    global USCNT
    i = 0 # Needed?
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

    print("USL:", avgDistance1)
    i = 0
    
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
  
    print("USR:", avgDistance2)

    # Check whether the distance is within 45 cm range
    # This could be a much better alg, without sleeps...
    flag = 0
    if avgDistance1 < 45 or avgDistance2 < 45:
        USCNT = USCNT + 1
        stop()
        back()
        if (USCNT == 3) & (flag == 0):
            USCNT = 0
            right()
            flag = 1
        else:
            left()
            flag = 0
            stop()
    else:
        forward()
        flag = 0
    return
