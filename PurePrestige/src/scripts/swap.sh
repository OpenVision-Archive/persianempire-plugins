location=$1
size=$2   
dd if=/dev/zero of=$location/swapfile bs=1024 count=$size
mkswap $location/swapfile
swapon $location/swapfile


