swapoff /hdd/swapfile
echo "**************************************"
dd if=/dev/zero of=/hdd/swapfile bs=1024 count=512000
mkswap /hdd/swapfile
echo "**************************************"
swapon /hdd/swapfile
echo "**************************************"
free
