#!/bin/sh
echo "startip"
ifconfig | grep   addr:
echo "endip"
echo "startdrivers"
opkg list | grep dvb-modules
echo "enddrivers"
echo "startkernel"
cat /proc/version
echo "endkernel"
echo "start2stage"
opkg list | grep secondstage
echo "end2stage"
echo "startuptime"
uptime
echo "enduptime"
echo "starthostname"
hostname
echo "endhostname"
echo "startmac"
ifconfig | grep HWaddr
echo "endmac"
exit 0