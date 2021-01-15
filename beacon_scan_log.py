from beacontools import BeaconScanner, EddystoneTLMFrame, EddystoneFilter

import logging
import time, socket, fcntl, struct
from datetime import datetime
import log_service

#---------------------------------Configuration-------------------------------------
send_interval_to_database = 10 # in interval_unit
interval_unit = 's'     # S - Seconds
                        # M - Minutes
                        # H - Hours
                        # D - Days
                        # midnight - roll over at midnight
                        # W{0-6} - roll over on a certain day; 0 - Monday
backupCount = 2

log_file = "logs/timed_test.log"
rpi_mac = None

def callback(bt_addr, rssi, packet, additional_info):
    timestamp = datetime.now()
    print( timestamp.isoformat(), bt_addr, rssi, packet.tx_power, packet.major, packet.minor, additional_info)

    logger.info("{},{},{},{},{},{},{},{}".format(timestamp.isoformat(), bt_addr, rpi_mac, 0, packet.major, packet.minor, rssi, packet.tx_power)) 

def getHwAddr(ifname = 'wlan0'):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
    return ':'.join('%02x' % b for b in info[18:24])

if __name__ == "__main__":

    print("Get Raspberry Pi MAC address...")
    rpi_mac = getHwAddr()
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
        packet_filter=None
    )
    scanner.start()
    print("Start to scan for beacons...")

