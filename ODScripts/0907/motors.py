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
