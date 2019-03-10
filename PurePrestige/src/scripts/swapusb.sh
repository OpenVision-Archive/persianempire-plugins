dd if=/dev/zero of=/media/usb/swapfile bs=1024 count=256000
mkswap /media/usb/swapfile
swapon /media/usb/swapfile
swapoff /media/usb/swapfile