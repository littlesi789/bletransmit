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


