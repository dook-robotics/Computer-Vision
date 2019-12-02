import time
import datetime
import argparse
import numpy as np
import atexit

def leaving(v):
    lastV = open("lastVoltage.txt", "w")
    lastV.write(str(v))
    lastV.close()
    voltageHistoryFile.close()


lastV = open("lastVoltage.txt", "r")
contents = lastV.read()
lastV.close()


v = 45
if(contents != ""):
    if int(v) - int(contents) > 4:
        print("Error: New battery detected")
        exit()
m1 = 2
m2 = 3

atexit.register(leaving, v)

# ---------- Add command line arguments ----------
parser = argparse.ArgumentParser(
                                 description = 'Dook Robotics - Object Detection Master Script',
                                 epilog = "Dook Robotics - https://github.com/dook-robotics"
                                )

parser.add_argument(
                               '--debug',
                     dest    = 'debugCLA',
                     action  = 'store_true',
                     default = False,
                     help    = 'Prints out all debug messages.'
                    )

parser.add_argument(
                               '--hardwareOff',
                     dest    = 'hardwareCLA',
                     action  = 'store_true',
                     default = False,
                     help    = 'Allows hardware to be called.'
                    )

parser.add_argument(
                               '--battery',
                     dest    = 'batteryNumCLA',
                     required = True,
                     help    = 'Battery number.'
                    )

parser.add_argument(
                               '--newBattery',
                     dest    = 'newBatteryCLA',
                     action  = 'store_true',
                     default = False,
                     help    = 'If battery is recharged.'
                    )

args = parser.parse_args()

voltageHistoryFile = open("voltageHistory" + args.batteryNumCLA  + ".txt", "a")
value = datetime.datetime.fromtimestamp(time.time())
if args.newBatteryCLA:
    voltageHistoryFile.write("\n========== " + value.strftime('%Y-%m-%d %H:%M:%S') + " ========== (N)\n\n")
else:
    voltageHistoryFile.write("\n========== " + value.strftime('%Y-%m-%d %H:%M:%S') + " ==========\n\n")
# v = np.random.randint(40, 45)

voltageTime = 4
value = datetime.datetime.fromtimestamp(time.time())
voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Battery: " + args.batteryNumCLA + ") | " + str(v) + "v\n")
voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Motor1)     | " + str(m1) + "amps\n")
voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Motor2)     | " + str(m2) + "amps\n")
voltageHistoryFile.write("\n")

while True:
    if time.time() - voltageTime > 1:
        v -= np.random.random(1)[0]
        v = round(v, 2)
        m1 += m1
        m2 += m2
        voltageTime = time.time()
        value = datetime.datetime.fromtimestamp(time.time())
        voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Battery: " + args.batteryNumCLA + ") | " + str(v) + "v\n")
        voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Motor1)     | " + str(m1) + "amps\n")
        voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Motor2)     | " + str(m2) + "amps\n")
        voltageHistoryFile.write("\n")
