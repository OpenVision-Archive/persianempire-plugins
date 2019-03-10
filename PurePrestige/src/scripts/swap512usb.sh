swapoff /media/usb//swapfile
echo "**************************************"
dd if=/dev/zero of=/hdd/swapfile bs=1024 count=512000
mkswap /media/usb/swapfile
echo "**************************************"
swapon /media/usb/swapfile
echo "**************************************"
free
