import time
import statistics
import sys, os
import math
from beacontools import BeaconScanner, EddystoneTLMFrame, EddystoneFilter, IBeaconFilter


#how many command line arguments are needed
if (len(sys.argv))!=3:
    sys.exit("Usage: durationInSeconds minor")
#how long reading lasts
readDuration = int(sys.argv[1])
#minor of the specific BLE
minorVal = int(sys.argv[2])
averageRssi = []


def callback(bt_addr, rssi, packet, additional_info):
    averageRssi.append(rssi)


#time.sleep(3)
scanner = BeaconScanner(callback, device_filter = IBeaconFilter(minor = minorVal))
scanner.start()
time.sleep(readDuration)
scanner.stop()


readings = len(averageRssi)
print ("length of test: ", readDuration, " seconds")
print ("BLE minor: ", minorVal)
print ("readings recieved: ", readings)
