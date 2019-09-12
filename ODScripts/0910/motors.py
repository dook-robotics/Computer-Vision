import time
import RPi.GPIO as GPIO

# Motor Pins
PWM1=17
DIR1=22
PWM2=23
DIR2=24

# US Pins
TRIG = 18
ECHO = 27

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
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

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
    print("Idling")

    global USCNT
    i = 0 # Needed?
    avgDistance = 0
    for i in range(5):

        # Take US Reading
        GPIO.output(TRIG, False)
        time.sleep(0.0001)
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        # Check whether the ECHO is LOW
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        # Check whether the ECHO is HIGH
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        # Time to get back the pulse to sensor
        pulse_duration = pulse_end - pulse_start

        #Multiply pulse duration by 17150 (34300/2) to get distance
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        avgDistance = avgDistance + distance

    avgDistance = avgDistance / 5
    print(avgDistance)

    # Check whether the distance is within 45 cm range
    # This could be a much better alg, without sleeps...
    flag = 0
    if avgDistance < 45:
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
