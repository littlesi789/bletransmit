echo "This script is to setup the Raspberry Pi BLE scan service"
echo "!!! sudo needed to run this script!!!"

echo "Install python requirements..."
sudo pip install -r requirements.txt  

echo "Setup service file"
current_dir=`pwd`
python_dir=`which python`
user_name=$(logname)
python service_file.py $current_dir $python_dir $user_name # set up workingDirector in the service file

echo "Move service files to systemd"
sudo mv ble_scan.service /lib/systemd/system/


echo "Start systemd service for server and pull data"
sudo systemctl enable ble_scan.service
sudo systemctl start ble_scan
