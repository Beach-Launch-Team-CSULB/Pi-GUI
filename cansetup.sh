#!/bin/sh
sudo ip link set can0 up type can bitrate 500000
sudo ip link set can1 up type can bitrate 500000
sudo ifconfig can0 txqueuelen 65536
sudo ifconfig can1 txqueuelen 65536
echo "candump to terminal"
candump -tA can0 >> can0Log.txt& #start candump in background
candump -tA can1 >> can1Log.txt& #start candump in background
echo thread start worked
#cansend can1 1F334455#1122334455667788 #extended ID CAN send
#cansend can1 0FF#1122334455667788 #extended ID CAN send

#echo $(date +"%m/%d/%y %T.%6N") #can be used to display time with microsecond precision
