import logging
import time
from datetime import datetime
import os
import random
import threading
import csv
from logging.handlers import TimedRotatingFileHandler
import pymongo

# Connection to the database
mongo_db_ip_address = '192.168.0.152' # TODO: change this...
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

#---------------------------------Simulate-------------------------------------
def token_simu(mac_address, logger):
    """
    A token instance simulation sending signal to the receiver.
    """
    uuid = "fda50693-a4e2-4fb1-afcf-c6eb07647825"
    for i in range(50):
        # print(i)
        zeroone = random.uniform(0, 1)
        if zeroone < 0.6:
            logger.info("{},{},{},{},{},{},{},{}".format(datetime.now(), mac_address, sample_raspi_mac_address[0], uuid, 10000, 101, int(random.uniform(-40,-60)), -59)) 
            #"time", "beacon_MAC", "pi_MAC", "uuid", "major", "minor", "RSSI", "tx_power"
        time.sleep(0.5)

def create_timed_rotating_log(path):
    """"""
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    
    handler = myTimeRotateFileHandler(path,
                                       when="s",
                                       interval=5,
                                       backupCount=5)
    logger.addHandler(handler)
    
    tokens = []
    for i in range(5):
        temp = threading.Thread(target=token_simu, args=[sample_token_mac_address[i], logger])
        tokens.append(temp)
    
    for i in range(5):
        tokens[i].start()

    
#----------------------------------------------------------------------
if __name__ == "__main__":
    log_file = "timed_test.log"
    create_timed_rotating_log(log_file)