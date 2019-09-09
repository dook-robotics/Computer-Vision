def relay():
    print("Turning on relay")
    GPIO.setup(RELAIS_1_GPIO, GPIO.OUT)
    GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
    GPIO.output(RELAIS_1_GPIO, GPIO.HIGH)
    time.sleep(4)
    GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
    return

def LoadCell():
    try:
        print("Load Cell Check")
        val = hx.get_weight(5)
        print(val)
        hx.power_down()
        hx.power_up()
        #time.sleep(0.1)
        #print(val)
    except (KeyboardInterrupt, SystemExit):
        print("Error: Load Cell")
    return

def voltage():
    print("Voltage Check")
    return

def LoadCellInit(hx):
    hx = HX711(5, 6)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(464)
    hx.reset()
    hx.tare()
    LoadCell()
    return
