swapoff /media/usb/swapfile
echo "**************************************"
dd if=/dev/zero of=/media/usb/swapfile bs=1024 count=128000
mkswap /media/usb//swapfile
echo "**************************************"
swapon /media/usb/swapfile 
echo "**************************************"
free 
