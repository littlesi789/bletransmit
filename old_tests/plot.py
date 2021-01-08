import numpy as np
import matplotlib.pyplot as plt

time = np.load("time.npy").astype("double")
rssi = np.load("rssi.npy").astype("double")
print(rssi)

plt.plot(time-time[0], rssi, label="raw measurement")

rssi_avg = np.copy(rssi).astype("double")
window = 3
for i in range(window):
    rssi_avg[i] = np.average(rssi[0:i+1])
for i in range(window, len(rssi)):
    rssi_avg[i] = np.average(rssi[i-window+1:i+1])
plt.plot(time-time[0], rssi_avg, label="moving avg with window size {}".format(window))
plt.title("RSSI vs time")
plt.legend()
plt.xlabel("time (s)")
plt.ylabel("RSSI (dBm)")
plt.grid()
plt.savefig("rssi_moving_avg_{}.png".format(window))

plt.figure()
plt.plot(time-time[0], rssi, label="raw measurement")

rssi_avg = np.copy(rssi).astype("double")
window = 5
for i in range(window):
    rssi_avg[i] = np.average(rssi[0:i+1])
for i in range(window, len(rssi)):
    rssi_avg[i] = np.average(rssi[i-window+1:i+1])
plt.plot(time-time[0], rssi_avg, label="moving avg with window size {}".format(window))
plt.title("RSSI vs time")
plt.legend()
plt.xlabel("time (s)")
plt.ylabel("RSSI (dBm)")
plt.grid()
plt.savefig("rssi_moving_avg_{}.png".format(window))

plt.figure()
plt.plot(time-time[0], rssi, label="raw measurement")

rssi_avg8 = np.copy(rssi).astype("double")
window = 8
for i in range(window):
    rssi_avg8[i] = np.average(rssi[0:i+1])
for i in range(window, len(rssi)):
    rssi_avg8[i] = np.average(rssi[i-window+1:i+1])
plt.plot(time-time[0], rssi_avg8, label="moving avg with window size {}".format(window))
plt.title("RSSI vs time")
plt.legend()
plt.xlabel("time (s)")
plt.ylabel("RSSI (dBm)")
plt.grid()
plt.savefig("rssi_moving_avg_{}.png".format(window))

plt.close("all")
plt.figure()
plt.plot(time-time[0], rssi, label="raw measurement")
rssi_avg_log = np.zeros(0)
avg = rssi[0]
w = 2
w2 = 1
rth = 7
cth = 3
c = 0
# for rs in rssi:
#     if (np.abs(avg - rs) <= rth) :
#         avg = (w * avg + rs)/(w+1)
#         c = 0
#     elif (c > cth):
#         avg = (w2 * avg + rs)/(w2+1)
#         c = 0
#     else:
#         c += 1
#     rssi_avg_log = np.append(rssi_avg_log,avg)

for rs in rssi:
    if (np.abs(avg - rs) <= rth) or (c > cth):
        avg = (w * avg + rs)/(w+1)
        c = 0
    else:
        c += 1
    rssi_avg_log = np.append(rssi_avg_log,avg)
plt.plot(time-time[0], rssi_avg_log)
plt.show()