import os, threading
import csv, codecs
import pymongo
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
import time, socket, fcntl, struct
import traceback


mongo_db_uri = "mongodb://piclient:82p9vjhk4akp2fd2@bbct-cpsl.engr.wustl.edu:27017/BBCT" # TODO: change this...
#---------------------------------Connection-------------------------------------
try:
    assert mongo_db_uri is not None
except:
    raise Exception("\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\
                    \nYou need to change the above 'mongo_db_uri' from None to the ip of the database.\
                    \nYou can use ifconfig command in linux to find the ip address...\
                    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
myclient = pymongo.MongoClient(mongo_db_uri, 
                                connectTimeoutMS=300,
                                serverSelectionTimeoutMS=300, 
                                socketTimeoutMS=300
                            )
mydb = myclient["BBCT"] # db names
mycol = mydb["beacons"] # collection names
myip = mydb['ip']

error_file1 = "logs/error_tier_1.log"
error_file2 = "logs/error_tier_2.log"


ip = os.popen("hostname -I").read().strip()
hostname = socket.gethostname()

#---------------------------------Helper Functions-------------------------------------
error_file1_lock = threading.Lock() # to protect the error log.


def getHwAddr(ifname = 'wlan0'):
    '''
    Return the MAC address of the device.
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
    return ':'.join('%02x' % b for b in info[18:24])

rpi_mac = getHwAddr()


def _write_file_to_database(filename, error_file, append=False, endTime = None):

    # First to write error data last time
    "Save a log in csv format to json and upload to the database"
    if append:
        write_mode = 'a'
    else:
        write_mode = 'w'
    error_list = []
    # Read the file and write the database
    try: 
        with open(filename,  newline='') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=["time", "beacon_MAC", "pi_MAC", "uuid", "major", "minor", "RSSI", "tx_power"])
            log_list = []
            
            for row in reader:
                log_list.append(row)
                
            for _ent in log_list:
                if endTime is not None and datetime.now() < endTime:
                    # _ent["_id"] = 1 # Used for test writing error
                    _ent["time"] = datetime.fromisoformat(_ent["time"])
                    try:
                        x = mycol.update_one({"beacon_MAC":_ent["beacon_MAC"], "pi_MAC":_ent["pi_MAC"], "time":_ent["time"]}, 
                                            {"$set":_ent}, upsert=True) # Notice here _ent is no longer the previous _ent. An '_id' key will be injected by the mongodb.
                    except Exception as e:
                        print("Writing errors to db:", _ent, e)
                        _ent["time"] = _ent["time"].isoformat()
                        _ent.pop('_id') # We need to delete the auto-generated '_id' entry to keep consistent with the previous dic format.
                        error_list.append(_ent)
                else:
                    print("Writing time to db exceeded:", _ent, endTime)
                    error_list.append(_ent)
            # Search 
            os.remove(filename)
    except Exception as e:
        print("File error:",e)
        traceback.print_exc()
    
    print("Error_list contains {} entries.".format(len(error_list)))
    if len(error_list) != 0:
        # Write the entries with saving error. 
        with open(error_file, mode=write_mode, newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=error_list[0].keys())
            writer.writerows(error_list)


def _save_to_database(filename, interval):
    """
    Write the history data to the database.
    
    Two tier error files to save entries that fail to be saved to DB
    """
    try:
        
        print({'rpi_MAC':rpi_mac,'ip':ip})
        x = myip.update_one({'rpi_MAC':rpi_mac},{"$set":{'rpi_MAC':rpi_mac,'ip':ip, 'hostname':hostname, "last_updated_time":datetime.now()}}, upsert=True)
    except Exception as e:
        print("Failed to write ip address to db. Continue...", e)


    end_time_part_1 = datetime.now() + timedelta(seconds=int(interval * 0.4))
    end_time_part_2 = datetime.now() + timedelta(seconds=int(interval * 0.8))
    error_file1_lock.acquire()
    # First write the last error files 
    if os.path.exists(error_file1):
        print("Rewrite the 1st tier error file")
        _write_file_to_database(error_file1, error_file2, append=True, endTime=end_time_part_1)

    # Then write the current logfile
    print("Write the current log", filename)
    _write_file_to_database(filename, error_file1, endTime=end_time_part_2)
    error_file1_lock.release()
    print("===")


class myTimeRotateFileHandler(TimedRotatingFileHandler):
    '''
    This is class is overwriting the TimedRotatingFileHandler
    '''
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
                sendFunc = threading.Thread(target=_save_to_database, args=(dest, self.interval,))
                sendFunc.start()
        else:
            self.rotator(source, dest)

    def getFilesToDelete(self):
        return []
