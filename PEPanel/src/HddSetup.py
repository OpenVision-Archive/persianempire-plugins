# -*- coding: utf-8 -*-
from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Tools.Directories import fileExists
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Button import Button
from .Extra.ExtrasList import ExtrasList
from Screens.MessageBox import MessageBox
from .HddPartitions import HddPartitions
from .HddInfo import HddInfo
from .Extra.Disks import Disks
from .Extra.ExtraMessageBox import ExtraMessageBox
from .Extra.ExtraActionBox import ExtraActionBox
from .Extra.MountPoints import MountPoints
import os
import sys
from .__init__ import _
from Components.Console import Console
from Tools.Directories import resolveFilename, SCOPE_PLUGINS


def DiskEntry(model, size, removable):
    res = [(model, size, removable)]
    if removable:
        picture = resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/diskusb.png')
    else:
        picture = resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/disk.png')
    if fileExists(picture):
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(48, 48), png=loadPNG(picture)))
    res.append(MultiContentEntryText(pos=(65, 10), size=(360, 38), font=0, text=model))
    res.append(MultiContentEntryText(pos=(435, 10), size=(125, 38), font=0, text=size))
    return res


class HddSetup(Screen):

    def __init__(self, session, args=0):
        self.session = session
        Screen.__init__(self, session)
        self.disks = list()
        self.mdisks = Disks()
        for disk in self.mdisks.disks:
            capacity = '%d MB' % (disk[1] / 1048576)
            self.disks.append(DiskEntry(disk[3], capacity, disk[2]))

        self['menu'] = ExtrasList(self.disks)
        self['key_red'] = Button(_('Partitions'))
        self['key_green'] = Button('Info')
        self['key_yellow'] = Button(_('Initialize'))
        self['key_blue'] = Button(_('Exit'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'blue': self.quit,
         'yellow': self.yellow,
         'green': self.green,
         'red': self.red,
         'cancel': self.quit}, -2)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('Devicemanager Main'))

    def mkfs(self):
        self.formatted += 1
        return self.mdisks.mkfs(self.mdisks.disks[self.sindex][0], self.formatted)

    def refresh(self):
        self.disks = list()
        self.mdisks = Disks()
        for disk in self.mdisks.disks:
            capacity = '%d MB' % (disk[1] / 1048576)
            self.disks.append(DiskEntry(disk[3], capacity, disk[2]))

        self['menu'].setList(self.disks)

    def checkDefault(self):
        mp = MountPoints()
        mp.read()
        if not mp.exist('/hdd'):
            mp.add(self.mdisks.disks[self.sindex][0], 1, '/hdd')
            mp.write()
            mp.mount(self.mdisks.disks[self.sindex][0], 1, '/hdd')
            Console().ePopen('mkdir /hdd/movie')
            Console().ePopen('mkdir /hdd/music')
            Console().ePopen('mkdir /hdd/picture')

    def format(self, result):
        if result != 0:
            self.session.open(MessageBox, _('Cannot format partition %d' % self.formatted), MessageBox.TYPE_ERROR)
        if self.result == 0:
            if self.formatted > 0:
                self.checkDefault()
                self.refresh()
                return
        elif self.result > 0 and self.result < 3:
            if self.formatted > 1:
                self.checkDefault()
                self.refresh()
                return
        elif self.result == 3:
            if self.formatted > 2:
                self.checkDefault()
                self.refresh()
                return
        elif self.result == 4:
            if self.formatted > 3:
                self.checkDefault()
                self.refresh()
                return
        self.session.openWithCallback(self.format, ExtraActionBox, _('Formatting partition %d') % (self.formatted + 1), 'Initialize disk', self.mkfs)

    def fdiskEnded(self, result):
        if result == 0:
            self.format(0)
        elif result == -1:
            self.session.open(MessageBox, _('Cannot umount device.\nA record in progress, timeshit or some external tools (like samba, swapfile and nfsd) may cause this problem.\nPlease stop this actions/applications and try again'), MessageBox.TYPE_ERROR)
        else:
            self.session.open(MessageBox, _('Partitioning failed!'), MessageBox.TYPE_ERROR)

    def fdisk(self):
        return self.mdisks.fdisk(self.mdisks.disks[self.sindex][0], self.mdisks.disks[self.sindex][1], self.result)

    def initialaze(self, result):
        if result != 5:
            self.result = result
            self.formatted = 0
            mp = MountPoints()
            mp.read()
            mp.deleteDisk(self.mdisks.disks[self.sindex][0])
            mp.write()
            self.session.openWithCallback(self.fdiskEnded, ExtraActionBox, _('Partitioning...'), _('Initialize disk'), self.fdisk)

    def yellow(self):
        if len(self.mdisks.disks) > 0:
            self.sindex = self['menu'].getSelectedIndex()
            self.session.openWithCallback(self.initialaze, ExtraMessageBox, _('Please select your preferred configuration.'), _('HDD Partitioner'), [[_('One partition'), 'partitionmanager.png'],
             [_('Two partitions (50% - 50%)'), 'partitionmanager.png'],
             [_('Two partitions (75% - 25%)'), 'partitionmanager.png'],
             [_('Three partitions (33% - 33% - 33%)'), 'partitionmanager.png'],
             [_('Four partitions (25% - 25% - 25% - 25%)'), 'partitionmanager.png'],
             [_('Cancel'), 'cancel.png']], 1, 5)

    def green(self):
        if len(self.mdisks.disks) > 0:
            self.sindex = self['menu'].getSelectedIndex()
            self.session.open(HddInfo, self.mdisks.disks[self.sindex][0])

    def red(self):
        if len(self.mdisks.disks) > 0:
            self.sindex = self['menu'].getSelectedIndex()
            self.session.open(HddPartitions, self.mdisks.disks[self.sindex])

    def quit(self):
        self.close()
