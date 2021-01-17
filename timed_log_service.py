import os, threading
import csv
import pymongo
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler


mongo_db_uri = "mongodb://:27017/BBCT" # TODO: change this...
#---------------------------------Connection-------------------------------------
try:
    assert mongo_db_uri is not None
except:
    raise Exception("\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\
                    \nYou need to change the above 'mongo_db_uri' from None to the ip of the database.\
                    \nYou can use ifconfig command in linux to find the ip address...\
                    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
myclient = pymongo.MongoClient(mongo_db_uri, connectTimeoutMS=1000, serverSelectionTimeoutMS=1100)
mydb = myclient["BBCT"] # db names
mycol = mydb["beacons"] # collection names
myip = mydb['ip']

error_file1 = "logs/error_tier_1.log"
error_file2 = "logs/error_tier_2.log"


#---------------------------------Helper Functions-------------------------------------
def _write_file_to_database(filename, error_file, append=False, endTime = None):
    try:
        ip = os.popen("hostname -I").read().strip()
        print(ip)
        x = myip.insert_one({'ip':ip})
    except Exception as e:
        print("Failed to write ip address to db. Continue...")

    # First to write error data last time
    "Save a log in csv format to json and upload to the database"
    if append:
        write_mode = 'a'
    else:
        write_mode = 'w'
    error_list = []
    # Read the file and write the database
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
                    x = mycol.insert_one(_ent)
                except Exception as e:
                    print("Writing errors to db:", _ent, e)
                    _ent["time"] = _ent["time"].isoformat()
                    error_list.append(_ent)
            else:
                print("Writing time to db exceeded:", _ent)
                error_list.append(_ent)
        # Search 
        os.remove(filename)
        print("===")
    
    print("Error list contains {} entries.".format(len(error_list)))
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
    end_time_part_1 = datetime.now() + timedelta(seconds=int(interval * 0.4))
    end_time_part_2 = datetime.now() + timedelta(seconds=int(interval * 0.8))
    # First write the last error files 
    if os.path.exists(error_file1):
        print("Rewrite the 1st tier error file")
        _write_file_to_database(error_file1, error_file2, append=True, endTime=end_time_part_1)

    # Then write the current logfile
    print("Write the current log", filename)
    _write_file_to_database(filename, error_file1, endTime=end_time_part_2)



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
