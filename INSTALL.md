# Setup

## Format SD card

https://www.sdcard.org/downloads/formatter_4/eula_mac/

## Install Linux distribution

http://www.raspberrypi.org/downloads

Copy the files into the SD card
Connect power supply
Follow instructions to install Raspbian OS

sudo raspi-config to reconfigure

## Download Wifi drivers

http://paulwallis.com/34/configuring-zyxel-nwd2105-wireless-usb-network-adaptor

sudo apt-get update
sudo aptitude -t squeeze-backports install firmware-realtek
sudo apt-get install firmware-ralink
sudo apt-get install wicd

## Install project dependencies

sudo apt-get install python3 python3-dev libncurses5-dev git
curl "python-distribute.org/distribute_setup.py" | sudo python3
sudo easy_install-3.2 pip readline
sudo pip install virtualenv ipython ipdb

## Deploy project

cd /opt
pyvenv lot && cd lot
source lot/bin/activate
curl "python-distribute.org/distribute_setup.py" | python
easy_install pip readline

pip install -r python-lot/requirements.txt
git clone https://github.com/jminuscula/python-lot

## Configure project

copy init script
sudo chmod 755 /opt/lot/python-lot/src/init.d/lot
sudo chmod 755 /opt/lot/python-lot/src/init.d/run
sudo cp /opt/lot/python-lot/src/init.d/lot /etc/init.d/
sudo update-rc.d lot start
