import time
import datetime
import argparse
import numpy as np


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

args = parser.parse_args()

voltageHistoryFile = open("voltageHistory.txt", "a")
value = datetime.datetime.fromtimestamp(time.time())
voltageHistoryFile.write("\n========== " + value.strftime('%Y-%m-%d %H:%M:%S') + " ==========\n\n")
v = np.random.randint(40, 45)
m1 = 2
m2 = 3
voltageTime = 4
value = datetime.datetime.fromtimestamp(time.time())
voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Battery: " + args.batteryNumCLA + ") | " + str(v) + "v\n")
voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Motor1)     | " + str(m1) + "v\n")
voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Motor2)     | " + str(m2) + "v\n")
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
        voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Motor1)     | " + str(m1) + "v\n")
        voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Motor2)     | " + str(m2) + "v\n")
        voltageHistoryFile.write("\n")
