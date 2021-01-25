import sys

#
# Write web server service
# ##
BLE_scan_service="""[Unit]
Description=BLE_scan systemd service.

[Service]
WorkingDirectory={0}
User={2}
Type=simple
ExecStart={1}  {0}/beacon_scan_log.py 
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

BLE_scan_service = BLE_scan_service.format(sys.argv[1],sys.argv[2],sys.argv[3])
file = open("ble_scan.service","w")
file.write(BLE_scan_service)
file.close()


#
# Write daily upload service
# ##
ble_upload_service="""[Unit]
Description=BLE_scan daily upload service.


[Service]
Type=oneshot
WorkingDirectory={0}
User={2}
ExecStart={1}  {0}/daily_upload.py 
"""

ble_upload_service = ble_upload_service.format(sys.argv[1],sys.argv[2],sys.argv[3])
file = open("ble_upload.service","w")
file.write(BLE_scan_service)
file.close()

# Write daily upload service timer
# ##
ble_upload_timer="""[Unit]
Description=BLE_scan daily upload service timer

[Timer]
OnCalendar=*-*-* 00:05:00
Persistent=true
[Install]
WantedBy=timers.target
"""
file = open("ble_upload.timer","w")
file.write(ble_upload_timer)
file.close()
