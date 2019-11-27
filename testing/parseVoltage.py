import matplotlib.pyplot as plt
import numpy as np
import time
import datetime
import matplotlib.ticker as plticker
import pandas as pd


voltageReadings = []
voltageTiming = []

voltageHistoryFile = open("voltageHistory.txt", "r")
content = voltageHistoryFile.read()
content = content.split('\n')

count = -1
currentTime = datetime.datetime.now()
for line in (content):
    if "=" in line:
        voltageReadings.append([])
        voltageTiming.append([])
        count += 1
        line = line.replace("=", "")
        currentTime = datetime.datetime.strptime(line, " %Y-%m-%d %H:%M:%S ")
        # voltageTiming[count].append(currentTime.strftime("%Y-%m-%d %H:%M:%S"))
    elif "Motor" in line:
        content.remove(line)
    elif "Battery" in line:
        line = line.split("|")[1].replace("v", "")
        currentTime = currentTime + datetime.timedelta(seconds=1)
        voltageReadings[count].append(line)
        # voltageTiming[count].append(currentTime.strftime("%Y-%m-%d %H:%M:%S"))
        voltageTiming[count].append(currentTime.strftime("%H:%M:%S"))

        # print(time)

print(voltageTiming)
print('\n')
print(voltageReadings)

# create data
# values = np.cumsum(np.random.randn(1000,1))
values = voltageReadings

# use the plot function
# dates = plt.dates.date2num(voltageTiming)
miny = 100.0
maxy = 0
for value in values:
    if float(min(value)) < float(miny):
        miny = float(min(value))
    if float(max(value)) > float(maxy):
        maxy = float(max(value))
    pass
print(int(miny))
print(int(maxy))
print(values[0])

df=pd.DataFrame({'x': range(int(miny),int(maxy)), 'Battery 1': values[0], 'Battery 2': values[1] })
# style
plt.style.use('seaborn-darkgrid')

# create a color palette
palette = plt.get_cmap('Set1')

# for i, value in enumerate(values):
#     # plt.plot(value)
#     plt.plot(value)
#     # plt.plot_date(voltageTiming, value)
#     pass
#plt.xaxis.set_major_locator(ticker.MultipleLocator(1.00))

num=0
for column in df.drop('x', axis=1):
    num+=1
    plt.plot(df['x'], df[column], marker='', color=palette(num), linewidth=1, alpha=0.9, label=column)

plt.legend(loc=2, ncol=2)

# Add titles
plt.title("A (bad) Spaghetti plot", loc='left', fontsize=12, fontweight=0, color='orange')
plt.xlabel("Time")
plt.ylabel("Score")


# plt.yticks(np.arange(int(miny), int(maxy), 1.0))
# # plt.gcf().autofmt_xdate()
# plt.gca().invert_yaxis()
plt.show()

# for line in content:
#     print(line)
