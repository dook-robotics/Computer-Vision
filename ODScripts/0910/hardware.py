import time
import RPi.GPIO as GPIO
from hx711 import HX711

# Relay Pin
RELAIS_1_GPIO = 25

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
    except (KeyboardInterrupt, SystemExit):
        print("Error: Load Cell")
    return

def voltage():
    print("Voltage Check")
    return

def LoadCellInit():
    hx = HX711(5, 6)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(464)
    hx.reset()
    hx.tare()
    print("setup")
    return hx

hx = LoadCellInit()
LoadCell(hx)
