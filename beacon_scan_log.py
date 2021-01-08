
import numpy as np
import matplotlib.pyplot as plt
from beacontools import BeaconScanner, EddystoneTLMFrame, EddystoneFilter

import logging
import time
from datetime import datetime
import os
import random
import threading
import csv
from logging.handlers import TimedRotatingFileHandler
import pymongo

#---------------------------------Configuration-------------------------------------
send_interval_to_database = 10 # in seconds
interval_unit = 's'     # S - Seconds
                        # M - Minutes
                        # H - Hours
                        # D - Days
                        # midnight - roll over at midnight
                        # W{0-6} - roll over on a certain day; 0 - Monday
backupCount = 5
total_scan_time_second = 30


mongo_db_ip_address = None # TODO: change this...

#---------------------------------Connection-------------------------------------
try:
    assert mongo_db_ip_address is not None
except:
    raise Exception("\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\
                    \nYou need to change the above 'mongo_db_ip_address' from None to the ip of the database.\
                    \nYou can use ifconfig command in linux to find the ip address...\
                    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
myclient = pymongo.MongoClient(mongo_db_ip_address, 27017)
mydb = myclient["mydatabase"]
mycol = mydb["customers"]

# Some mac addresses 
sample_token_mac_address = ["00:11:22:33:44:D{}".format(i) for i in [1, 2, 3, 4, 5, 6, 7, 8, 9]]
sample_raspi_mac_address = ["09:FB:9B:F0:EF:D{}".format(i) for i in [1, 2, 3, 4, 5, 6, 7, 8, 9]]

#---------------------------------Helper Functions-------------------------------------
def _save_to_database(filename):
    "Save a log in csv format to json and upload to the database"
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=["time", "beacon_MAC", "pi_MAC", "uuid", "major", "minor", "RSSI", "tx_power"])
        log_list = []
        for row in reader:
            log_list.append(row)
        
        # Option 1: using insert_many
        # Cannot know which item is not inserted.
        # x = mycol.insert_many(log_list)
        # print(x)

        # Option 2: Insert one-by-one
        # TODO: handle the circumstance of loss of internet connection...
        for _ent in log_list:
            x = mycol.insert_one(_ent)
            print(x)

        # print(log_list)
        os.remove(filename)


class myTimeRotateFileHandler(TimedRotatingFileHandler):
    def rotate(self, source, dest):
        """
        When rotating, rotate the current log.

        The default implementation calls the 'rotator' attribute of the
        handler, if it's callable, passing the source and dest arguments to
        it. If the attribute isn't callable (the default is None), the source
        is simply renamed to the destination.

        :param source: The source filename. This is normally the base
                       filename, e.g. 'test.log'
        :param dest:   The destination filename. This is normally
                       what the source is rotated to, e.g. 'test.log.1'.
        """
        if not callable(self.rotator):
            # Issue 18940: A file may not have been created if delay is True.
            if os.path.exists(source):
                os.rename(source, dest)
                print("New saved log file: {}".format(dest))
                sendFunc = threading.Thread(target=_save_to_database, args=(dest,))
                sendFunc.start()
        else:
            self.rotator(source, dest)

    def getFilesToDelete(self):
        return []

#---------------------------------main program-------------------------------------
# Create logger
time_log = []
rssi_log = []

log_file = "timed_test.log"
logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.INFO)

handler = myTimeRotateFileHandler(log_file,
                                    when=interval_unit,
                                    interval=send_interval_to_database,
                                    backupCount=backupCount)
logger.addHandler(handler)

def callback(bt_addr, rssi, packet, additional_info):
    timestamp = datetime.now()
    time_str = datetime.now().strftime("%Y-%m-%d-%H:%M:%S.%f")
    # print("<%s, %d, %s>\n  %s\n %s\n" % (bt_addr, rssi, time_str, packet, additional_info))
    print( timestamp.isoformat(), bt_addr, rssi, packet.tx_power, packet.major, packet.minor, additional_info)

    logger.info("{},{},{},{},{},{},{},{}".format(datetime.now(), bt_addr, sample_raspi_mac_address[0], 0, packet.major, packet.minor, rssi, packet.tx_power)) 
    #"time", "beacon_MAC", "pi_MAC", "uuid", "major", "minor", "RSSI", "tx_power"
    time_log.append(time.time())
    rssi_log.append(rssi)

# scan for all TLM frames of beacons in the namespace "12345678901234678901"
scanner = BeaconScanner(callback,
    # remove the following line to see packets from all beacons
    device_filter=None,
    packet_filter=None
)
scanner.start()
print("Start to scan for {} secnods".format(total_scan_time_second))
time.sleep(total_scan_time_second)
scanner.stop()


#---------------------------------plots for debug-------------------------------------
# print (rssi_log)


# tt = np.array(time_log)
# rr = np.array(rssi_log)

# np.save("time", tt)
# np.save("rssi", rr)

# plt.plot(tt - tt[0], rr)
# plt.show()
