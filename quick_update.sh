echo "This is the quick setup, will NOT install all dependancies!!!"
echo "!!! sudo needed to run this script!!!"

sudo setcap 'cap_net_raw,cap_net_admin+eip' "$(readlink -f "$(which python3)")"

echo "Setup service file"
current_dir=`pwd`
python_dir=`which python3`
user_name=$(logname)
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
