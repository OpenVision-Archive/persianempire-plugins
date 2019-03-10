swapoff /hdd/swapfile
echo "**************************************"
dd if=/dev/zero of=/hdd/swapfile bs=1024 count=256000
mkswap /hdd/swapfile
echo "**************************************"
swapon /hdd/swapfile
echo "**************************************"
free
