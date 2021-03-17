import os, threading, copy
import csv, codecs
import pymongo
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
import time, socket, fcntl, struct
import traceback
from beacon_scan import rpi_mac, ip, hostname

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
db_ip_col = mydb['ip']

error_file1 = "logs/error_tier_1.log"
error_file2 = "logs/error_tier_2.log"
batch_size = 30


#---------------------------------Helper Functions-------------------------------------
error_file1_lock = threading.Lock() # to protect the error log.


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
            intervals = list(range(0, len(log_list), batch_size)) + [len(log_list)]
            for _idx in range(0, len(intervals) - 1):
                batch_entry = log_list[intervals[_idx]:intervals[_idx+1]]
                batch_copy = copy.deepcopy(batch_entry) # For insert fail backup
                if endTime is not None and datetime.now() < endTime:
                    for _ent in batch_entry:
                        _ent["time"] = datetime.fromisoformat(_ent["time"])
                    try:
                        x = mycol.insert_many(batch_entry)
                    except Exception as e:
                        print("Writing errors to db:", e)
                        error_list += batch_copy 
                else:
                    print("Writing time to db exceeded:", endTime)
                    error_list += batch_copy 
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
        x = db_ip_col.update_one({'pi_MAC':rpi_mac},{"$set":{'pi_MAC':rpi_mac,'ip':ip, 'hostname':hostname, "last_updated_time":datetime.now()}}, upsert=True)
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
