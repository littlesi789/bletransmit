echo "This script is to setup the Raspberry Pi BLE scan service"
echo "!!! sudo needed to run this script!!!"

echo "Install Linux Bluetooth package"
sudo apt-get -y install libbluetooth-dev libcap2-bin

sudo setcap 'cap_net_raw,cap_net_admin+eip' "$(readlink -f "$(which python3)")"

echo "Install python requirements..."
sudo pip3 install -r requirements.txt  

echo "Setup service file"
current_dir=`pwd`
python_dir=`which python3`
user_name=pi
python3 service_file.py $current_dir $python_dir $user_name # set up workingDirector in the service file

echo "Move service files to systemd"
sudo mv ble_scan.service /lib/systemd/system/
sudo mv ble_upload.service /lib/systemd/system/
sudo mv ble_upload.timer /lib/systemd/system/

echo "Start systemd service for server and pull data"
sudo systemctl enable ble_scan.service
sudo systemctl start ble_scan
sudo systemctl enable ble_upload.timer
sudo systemctl start ble_upload.timer

sudo systemctl daemon-reload
