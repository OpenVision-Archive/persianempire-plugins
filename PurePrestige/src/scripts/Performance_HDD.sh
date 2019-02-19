#!/bin/sh
#DESCRIPTION=This script will show you the performance of your HDD
hdparm -Tt /dev/ide/host0/bus0/target0/lun0/disc
echo ""
exit 0
