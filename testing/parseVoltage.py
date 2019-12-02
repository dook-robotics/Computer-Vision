import numpy as np
import time
import datetime
import csv
import argparse

# ---------- Add command line arguments ----------
parser = argparse.ArgumentParser(
                                 description = 'Dook Robotics - Object Detection Master Script',
                                 epilog = "Dook Robotics - https://github.com/dook-robotics"
                                )

parser.add_argument(
                               '--battery',
                     dest    = 'batteryNumCLA',
                     required = True,
                     help    = 'Battery number.'
                    )

args = parser.parse_args()

voltageReadings = []
voltageTiming = []

voltageHistoryFile = open("voltageHistory" + args.batteryNumCLA + ".txt", "r")
content = voltageHistoryFile.read()
content = content.split('\n')

count = -1
maxLen = 0
currLen = 0
# voltageReadings.append([])
# voltageTiming.append([])
lastTime = 0
lastVoltage = 0
currentTime = datetime.datetime.now()
for i, line in enumerate(content):
    if "=" in line:
        if "(N)" in line:
            if currLen > maxLen:
                maxLen = currLen
                currLen = 0
            line = line.replace("(N)", "")
            count += 1
            voltageReadings.append([])
            voltageTiming.append([])
        line = line.replace("=", "")
        currentTime = datetime.datetime.strptime(line, " %Y-%m-%d %H:%M:%S ")
        # voltageTiming[count].append(currentTime.strftime("%Y-%m-%d %H:%M:%S"))
    elif "Motor" in line:
        content.remove(line)
    elif "Battery" in line:
        currLen += 1
        if currLen != 1:
            delta = currentTime - datetime.datetime.strptime(lastTime, "%H:%M:%S")
            # print(delta.seconds)
            if delta.seconds-1 > 1:
                for i in range(delta.seconds-1):
                    voltageReadings[count].append(lastVoltage)
                    voltageTiming[count].append((datetime.datetime.strptime(lastTime, "%H:%M:%S") + datetime.timedelta(seconds=i+1)).strftime("%H:%M:%S"))
                    pass
        vReading = line.split("|")[1].replace("v", "")
        voltageReadings[count].append(vReading)
        voltageTiming[count].append(currentTime.strftime("%H:%M:%S"))
        print(voltageTiming)
        lastTime = voltageTiming[count][len(voltageTiming[count]) -1]
        lastVoltage = voltageReadings[count][len(voltageReadings[count]) -1]
        currentTime = datetime.datetime.strptime(line.split('(')[0], "%Y-%m-%d %H:%M:%S ")

# print(voltageReadings)
# print("")
print(voltageTiming)

if maxLen == 0:
    maxLen = currLen

with open("voltagecsv" + args.batteryNumCLA + ".csv", mode='w') as vcsv:
    voltage_writer = csv.writer(vcsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    voltage_writer.writerow(np.arange(maxLen))
    for row in voltageReadings:
        voltage_writer.writerow(row)
