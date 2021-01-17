
### logging_mongo_many.py: 
Sending logs to the mongodb server. No BLE is involved.

### beacon_scan_log.py: 
Scan BLE, log and send to the mongodb server. Need to run RASPI Zero.

### Mongodb.docx: 
How to setup the db and connect from Pi.

### timed_log_service.py: 
core for uploading to the mongodb.

### Mongodb:
* Name: BBCT
* Collection: Beacons
  * Fields: ["time", "beacon_MAC", "pi_MAC", "uuid", "major", "minor", "RSSI", "tx_power"]
  * Sample entry in Beacons: 
  ```
  { "_id" : ObjectId("60012a0e073eb7d978485d99"), "time" : ISODate("2021-01-14T23:35:21.604Z"), "beacon_MAC" : "ac:23:3f:65:4a:db", "pi_MAC" : "b8:27:eb:26:73:88", "uuid" : "0", "major" : "10001", "minor" : "19641", "RSSI" : "-49", "tx_power" : "-59" }
  ```
* Collection: ip
  * Fields: ["rpi_MAC", "ip"]
  * Sample entry in ip: 
  ```
  { "_id" : ObjectId("600492742ca2e2adec158ee9"), "rpi_MAC" : "b8:27:eb:26:73:88", "ip" : "192.168.0.109" }
  ```
