#!/bin/sh

rm -rf /tmp/sundtek_installer_development.sh > /dev/null 2>&1
cd /tmp
wget http://www.sundtek.de/media/sundtek_installer_development.sh
chmod 755 sundtek_installer_development.sh > /dev/null 2>&1
/tmp/sundtek_installer_development.sh -easyvdr
rm -rf /tmp/sundtek_installer_development.sh > /dev/null 2>&1
