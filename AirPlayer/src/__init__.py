from enigma import getDesktop
from skin import loadSkin
import os
from sys import version_info
from Components.config import config, ConfigSubsection, ConfigSelection
import ctypes
import plistlib
import shutil
import subprocess

def getSkins():
    print '[AirPlayer] search for Skins'
    skins = []
    skindir = '/usr/lib/enigma2/python/Plugins/Extensions/AirPlayer/Skins/'
    for o in os.listdir(skindir):
        if os.path.isdir(skindir + o):
            print '[AirPlayer] found Skin', o
            skins.append((o, o))

    return skins


def getSkinPath(name):
    skinName = name
    dSize = getDesktop(0).size()
    skinpath = '/usr/lib/enigma2/python/Plugins/Extensions/AirPlayer/Skins/%s/%sx%s/skin.xml' % (skinName, str(dSize.width()), str(dSize.height()))
    if os.path.exists(skinpath):
        return skinpath
    else:
        print '[AirPlayer] skin ', skinpath, 'does not exist'
        return None
        return None


config.plugins.airplayer = ConfigSubsection()
config.plugins.airplayer.skin = ConfigSelection(default='Classic', choices=getSkins())
skinPath = getSkinPath('Classic')
try:
    path = getSkinPath(config.plugins.airplayer.skin.value)
    if path is not None:
        skinPath = path
except Exception as e:
    print '[AirPlayer] error reading skin ', e

print '[AirPlayer] using skin ', skinPath
loadSkin(skinPath)
print '[AirPlayer] running python ', version_info

try:
    if os.path.exists('/etc/avahi/services/airplay.service'):
        print '[AirPlayer] try to remove avahi service file'
        os.remove('/etc/avahi/services/airplay.service')
except Exception:
    pass
