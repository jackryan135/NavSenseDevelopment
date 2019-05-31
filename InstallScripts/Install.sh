#!/bin/bash

# General
sudo apt-get update
sudo apt-get upgrade
sudo rpi-update

# TFMini
mv /boot/config.txt temp.txt
cat temp.txt config_edits.txt > config.txt
mv config.txt /boot/config.txt
rm temp.txt

# Google Coral Accelerator
sudo apt-get install feh
cd ~/
wget https://dl.google.com/coral/edgetpu_api/edgetpu_api_latest.tar.gz -O edgetpu_api.tar.gz --trust-server-names
tar xzf edgetpu_api.tar.gz
rm edgetpu_api.tar.gz
cd edgetpu_api
echo "Press N key and then Enter"
bash ./install.sh

sudo reboot
