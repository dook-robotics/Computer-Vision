import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from hx711 import HX711

# Relay Pin
RELAIS_1_GPIO = 25

#setup for voltage senosr
#I2C BUS0
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan0 = AnalogIn(ads, ADS.P0)# Pin for pi
chan1 = AnalogIn(ads, ADS.P1) #pins for motors: motor 1
#chan2 = AnalogIn(ads, ADS.P2) #pins for motors: motor 2

R1 = 10000
R2 = 1000



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
    batteryVoltage = chan0.voltage * ((R1 + R2)/R2)
    motor1Current = (chan1.voltage - 2.55)*10
    # motor2Current = (chan2.voltage -2.55)*10        
    print("chan0 value: {:>5}\t chan0 voltage: {:>5.3f}\t Battery voltage: {:>5.3f}".format(chan0.value, chan0.voltage, batteryVoltage))
    print("chan1 value: {:>5}\t chan1 current: {:>5.3f}".format(chan1.value, motor1Current))
    # print("chan2 value: {:>5}\t chan2 voltage: {:>5.3f}".format(chan2.value, motor2Current))
    return

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
