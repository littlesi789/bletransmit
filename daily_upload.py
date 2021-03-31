import  os, time, random
from datetime import datetime, timedelta


error_file1 = "logs/error_tier_2.log"
if __name__ == "__main__":
    print("Running daily upload")
    offset_time = random.randint(0, 60*5)
    print(f"Wait {offset_time} seconds to start")
    time.sleep(offset_time)
    print("PWD:", os.getcwd())
    if os.path.exists(error_file1):
        print("Writing tier2 error logs")
        import timed_log_service
        timed_log_service._write_file_to_database(error_file1, error_file1, endTime=datetime.now() + timedelta(seconds=60*55))