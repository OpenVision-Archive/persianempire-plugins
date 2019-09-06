from enigma import *
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Button import Button
from Screens.MessageBox import MessageBox
from Extra.MountPoints import MountPoints
from Extra.ExtraMessageBox import ExtraMessageBox
import os
import sys
import re
from __init__ import _
from Components.Console import Console

class HddMount(Screen):

    def __init__(self, session, device, partition):
        Screen.__init__(self, session)
        self.device = device
        self.partition = partition
        self.mountpoints = MountPoints()
        self.mountpoints.read()
        self.list = []
        self.list.append('Mount as main hdd')
        self.list.append('Mount as /media/usb')
        self.list.append('Mount as /media/usb1')
        self.list.append('Mount as /media/usb2')
        self.list.append('Mount as /media/usb3')
        self.list.append('Mount as /media/cf')
        self.list.append('Mount as /media/mmc1')
        self.list.append('Mount on custom path')
        self['menu'] = MenuList(self.list)
        self['key_green'] = Button('')
        self['key_red'] = Button(_('Ok'))
        self['key_blue'] = Button(_('Exit'))
        self['key_yellow'] = Button('')
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'blue': self.quit,
         'red': self.ok,
         'ok': self.ok,
         'cancel': self.quit}, -2)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('Devicemanager Mountpoints'))

    def ok(self):
        try:
            os.chmod('/usr/bin/mountct', 493)
            os.chmod('/etc/init.d/mountctall', 493)
            os.symlink('/etc/init.d/mountctall', '/etc/rcS.d/S49mountctall')
        except OSError:
            print '[PEPanel] symlink already exists. do nothing.'

        selected = self['menu'].getSelectedIndex()
        if selected == 0:
            self.setMountPoint('/media/hdd')
        elif selected == 1:
            self.setMountPoint('/media/usb')
        elif selected == 2:
            self.setMountPoint('/media/usb1')
        elif selected == 3:
            self.setMountPoint('/media/usb2')
        elif selected == 4:
            self.setMountPoint('/media/usb3')
        elif selected == 5:
            self.setMountPoint('/media/cf')
        elif selected == 6:
            self.setMountPoint('/media/mmc1')
        elif selected == 7:
            self.session.openWithCallback(self.customPath, VirtualKeyBoard, title=_('Insert mount point:'), text='/media/custom')

    def customPath(self, result):
        if result and len(result) > 0:
            result = result.rstrip('/')
            Console().ePopen('mkdir -p %s' % result)
            self.setMountPoint(result)

    def setMountPoint(self, path):
        self.cpath = path
        if self.mountpoints.exist(path):
            self.session.openWithCallback(self.setMountPointCb, ExtraMessageBox, 'Selected mount point is already used by another drive.', 'Mount point exist!', [['Change old drive with this new drive', 'ok.png'], ['Mantain old drive', 'cancel.png']])
        else:
            self.setMountPointCb(0)

    def setMountPointCb(self, result):
        if result == 0:
            if self.mountpoints.isMounted(self.cpath):
                if not self.mountpoints.umount(self.cpath):
                    self.session.open(MessageBox, _('Cannot umount current drive.\nA record in progress, timeshit or some external tools (like samba, swapfile and nfsd) may cause this problem.\nPlease stop this actions/applications and try again'), MessageBox.TYPE_ERROR)
                    self.close()
                    return
            self.mountpoints.delete(self.cpath)
            self.mountpoints.add(self.device, self.partition, self.cpath)
            self.mountpoints.write()
            if not self.mountpoints.mount(self.device, self.partition, self.cpath):
                self.session.open(MessageBox, _('Cannot mount new drive.\nPlease check filesystem or format it and try again'), MessageBox.TYPE_ERROR)
            elif self.cpath == '/media/hdd':
                Console().ePopen('mkdir /hdd/movie')
                Console().ePopen('mkdir /hdd/music')
                Console().ePopen('mkdir /hdd/picture')
            self.close()

    def quit(self):
        self.close()
