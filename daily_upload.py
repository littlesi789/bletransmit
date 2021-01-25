import timed_log_service, os
from datetime import datetime, timedelta


error_file1 = "logs/error_tier_2.log"
if __name__ == "__main__":
    if os.path.exists(error_file1):
        print("Writing tier2 error logs")
        timed_log_service._write_file_to_database(error_file1, error_file1, endTime=datetime.now() + timedelta(seconds=60*1))