#!/bin/sh
sudo ip link set can0 up type can bitrate 500000
sudo ip link set can1 up type can bitrate 500000
sudo ifconfig can0 txqueuelen 65536
sudo ifconfig can1 txqueuelen 65536
candump -tA can0 >> /media/pi/FLASHDRIVE/canlog.txt &
