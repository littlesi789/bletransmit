from beacontools import BeaconScanner, EddystoneTLMFrame, EddystoneFilter, IBeaconFilter, IBeaconAdvertisement

import logging, os
import time
from datetime import datetime
import timed_log_service as log_service

#---------------------------------Configuration-------------------------------------
send_interval_to_database = 10 # in interval_unit
interval_unit = 's'     # S - Seconds
                        # M - Minutes
                        # H - Hours
                        # D - Days
                        # midnight - roll over at midnight
                        # W{0-6} - roll over on a certain day; 0 - Monday
backupCount = 2 # Required but not used. It will not affect anything.
if not os.path.exists('logs'):
    os.makedirs('logs')
log_file = "logs/timed_test.log"
rpi_mac = log_service.rpi_mac

def callback(bt_addr, rssi, packet, additional_info):
    timestamp = datetime.now()
    print( "New entry:", timestamp.isoformat(), bt_addr, rssi, packet.tx_power, packet.major, packet.minor, additional_info)
    # print("New entry:", timestamp.isoformat())
    logger.info("{},{},{},{},{},{},{},{}".format(timestamp.isoformat(), bt_addr, rpi_mac, 0, packet.major, packet.minor, rssi, packet.tx_power)) 


if __name__ == "__main__":

    print("Get Raspberry Pi MAC address...")
    print(rpi_mac)

    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)

    handler = log_service.myTimeRotateFileHandler(log_file,
                                        when=interval_unit,
                                        interval=send_interval_to_database,
                                        backupCount=backupCount)
    logger.addHandler(handler)

    # scan for all TLM frames of beacons in the namespace "12345678901234678901"
    scanner = BeaconScanner(callback,
        # remove the following line to see packets from all beacons
        device_filter=None,
        packet_filter=IBeaconAdvertisement
    )
    scanner.start()
    print("Start to scan for beacons... (New beacon messages should appear very quickly)\n\
            If not, check the URI of mongodb, the bluetooth and the beacons.")

