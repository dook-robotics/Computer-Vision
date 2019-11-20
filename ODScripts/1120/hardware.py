## motors.py ##
## functions for the general hardware ##
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
import board
import busio
import RPi.GPIO as GPIO
import adafruit_ads1x15.ads1115 as ADS
from hx711 import HX711
from adafruit_ads1x15.analog_in import AnalogIn

# Relay Pin
RELAIS_1_GPIO = 25

# Servo Pin
servoPin = 12
GPIO.setup(servoPin, GPIO.OUT)

cameraSetting = 0
cameraSpeed   = 5
cameraServo   = GPIO.PWM(servoPin, 50)
cameraServo.start(0)

#setup for voltage senosr
#I2C BUS0
i2c   = busio.I2C(board.SCL, board.SDA)
ads   = ADS.ADS1115(i2c)
chan0 = AnalogIn(ads, ADS.P0) # Pin for pi
chan1 = AnalogIn(ads, ADS.P1) # pins for motors: motor 1
#chan2 = AnalogIn(ads, ADS.P2) # pins for motors: motor 2

R1 = 10000
R2 = 1000

def servo(camDir):
    if(camDir == 1):
        cameraSetting += cameraSpeed
    if(camDir == -1):
	    cameraSetting -= cameraSpeed
    cameraServo.ChangeDutyCycle(cameraSetting)
    return

def relay():
    print("Relay On")
    GPIO.setup(RELAIS_1_GPIO, GPIO.OUT)
    GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
    GPIO.output(RELAIS_1_GPIO, GPIO.HIGH)
    return time.time()

def relayTurnOff():
    print("Relay Off")
    GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
    return

def LoadCell(hx):
    try:
        print("Load Cell Check")
        val = hx.get_weight(5)
        print(val)
        hx.power_down()
        hx.power_up()
        return val
    except (KeyboardInterrupt, SystemExit):
        print("Error: Load Cell")
    return -1

def voltage():
    print("Voltage Check")
    batteryVoltage = chan0.voltage * ((R1 + R2) / R2)
    motor1Current = (chan1.voltage - 2.55) * 10
    # motor2Current = (chan2.voltage -2.55)*10
    print("chan0 value: {:>5}\t chan0 voltage: {:>5.3f}\t Battery voltage: {:>5.3f}".format(chan0.value, chan0.voltage, batteryVoltage))
    print("chan1 value: {:>5}\t chan1 current: {:>5.3f}".format(chan1.value, motor1Current))
    # print("chan2 value: {:>5}\t chan2 voltage: {:>5.3f}".format(chan2.value, motor2Current))
    return batteryVoltage, motor1Current, motor2Current

def LoadCellInit():
    hx = HX711(5, 6)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(464)
    hx.reset()
    hx.tare()
    print("setup")
    return hx

#hx = LoadCellInit()
#LoadCell(hx)
