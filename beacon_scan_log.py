from beacontools import BeaconScanner, EddystoneTLMFrame, EddystoneFilter, IBeaconFilter, IBeaconAdvertisement

import logging, os
import time, threading
from datetime import datetime
import timed_log_service as log_service, db_ip_col, error_file2

#---------------------------------Configuration-------------------------------------
send_interval_to_database = 20 # in interval_unit
interval_unit = 's'     # S - Seconds
                        # M - Minutes
                        # H - Hours
                        # D - Days
                        # midnight - roll over at midnight
                        # W{0-6} - roll over on a certain day; 0 - Monday
backupCount = 2 # Required but not used. It will not affect anything.
heartbeat_interval = 10
log_dir = "logs"
log_file = "logs/timed_test.log"


if not os.path.exists(log_dir):
    os.makedirs(log_dir)
rpi_mac = getHwAddr()
ip = os.popen("hostname -I").read().strip()
hostname = socket.gethostname()


def callback(bt_addr, rssi, packet, additional_info):
    timestamp = datetime.now()
    print( "New entry:", timestamp.isoformat(), bt_addr, rssi, packet.tx_power, packet.major, packet.minor, additional_info)
    # print("New entry:", timestamp.isoformat())
    logger.info("{},{},{},{},{},{},{},{}".format(timestamp.isoformat(), bt_addr, rpi_mac, 0, packet.major, packet.minor, rssi, packet.tx_power)) 

def getHwAddr(ifname = 'wlan0'):
    '''
    Return the MAC address of the device.
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
    return ':'.join('%02x' % b for b in info[18:24])


class Heartbeat(threading.Thread):
    """
    Background service to update the status of the Pi
    """
    def __init__(self, interval):
        threading.Thread.__init__(self)
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        try:
            error_file2_size = 0
            if os.path.exists(error_file2):
                error_file2_size = os.path.getsize(error_file2)
            num_log_files = len(os.listdir(log_dir))
        except:
            print("Read log info error")
        try:
            x = db_ip_col.update_one({'pi_MAC':rpi_mac},{"$set":{'pi_MAC':rpi_mac,'ip':ip, 'hostname':hostname, 
                                "num_log_files": num_log_files, "error2_size": error_file2_size,
                                "last_heartbeat_time":datetime.now()}}, upsert=True)
        except:
            print("Write heartbeat info error")
        time.sleep(self.interval)


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
    hr_service = Heartbeat(heartbeat_interval)

    # scan for all TLM frames of beacons in the namespace "12345678901234678901"
    scanner = BeaconScanner(callback,
        # remove the following line to see packets from all beacons
        device_filter=None,
        packet_filter=IBeaconAdvertisement
    )
    scanner.start()
    print("Start to scan for beacons... (New beacon messages should appear very quickly)\n\
            If not, check the URI of mongodb, the bluetooth and the beacons.")

