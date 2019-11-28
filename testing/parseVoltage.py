import numpy as np
import time
import datetime
import csv



voltageReadings = []
voltageTiming = []

voltageHistoryFile = open("voltageHistory2.txt", "r")
content = voltageHistoryFile.read()
content = content.split('\n')

count = 0
maxLen = 0
currLen = 0
voltageReadings.append([])
voltageTiming.append([])
currentTime = datetime.datetime.now()
for line in (content):
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
        line = line.split("|")[1].replace("v", "")
        voltageReadings[count].append(line)
        voltageTiming[count].append(currentTime.strftime("%H:%M:%S"))
        currentTime = currentTime + datetime.timedelta(seconds=1)

print(voltageReadings)
print("")
print(voltageTiming)

if maxLen == 0:
    maxLen = currLen

with open('voltagecsv2.csv', mode='w') as vcsv:
    voltage_writer = csv.writer(vcsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    voltage_writer.writerow(np.arange(maxLen))
    for row in voltageReadings:
        voltage_writer.writerow(row)
