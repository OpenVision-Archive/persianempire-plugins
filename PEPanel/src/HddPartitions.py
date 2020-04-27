#!/usr/bin/python
# -*- coding: utf-8 -*-
from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Button import Button
from Extra.ExtrasList import ExtrasList
from Screens.MessageBox import MessageBox
from Extra.Disks import Disks
from Extra.ExtraActionBox import ExtraActionBox
from Extra.MountPoints import MountPoints
from HddMount import HddMount
import os
import sys
from __init__ import _

def PartitionEntry(description, size):
    res = [(description, size)]
    picture = resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/partitionmanager.png')
    if fileExists(picture):
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(48, 48), png=loadPNG(picture)))
    res.append(MultiContentEntryText(pos=(65, 10), size=(360, 38), font=0, text=description))
    res.append(MultiContentEntryText(pos=(435, 10), size=(125, 38), font=0, text=size))
    return res


class HddPartitions(Screen):

    def __init__(self, session, disk):
        self.session = session
        Screen.__init__(self, session)
        self.disk = disk
        self.refreshMP(False)
        self['menu'] = ExtrasList(self.partitions)
        self['menu'].onSelectionChanged.append(self.selectionChanged)
        self['key_red'] = Button('')
        self['key_green'] = Button('')
        self['key_yellow'] = Button('')
        self['key_blue'] = Button(_('Exit'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'blue': self.quit,
         'yellow': self.yellow,
         'green': self.green,
         'red': self.red,
         'cancel': self.quit}, -2)
        self.onShown.append(self.setWindowTitle)
        if len(self.disk[5]) > 0:
            if self.disk[5][0][2] == 'Linux':
                self['key_green'].setText(_('Check'))
                self['key_yellow'].setText(_('Format'))
        if self.disk[5][0][2] == 'Linux swap':
            self['key_red'].setText('')
        else:
            mp = self.mountpoints.get(self.disk[0], 1)
            if len(mp) > 0:
                self.mounted = True
                self['key_red'].setText(_('Umount'))
            else:
                self.mounted = False
                self['key_red'].setText(_('Mount'))

    def setWindowTitle(self):
        self.setTitle(_('Devicemanager Partitions'))

    def selectionChanged(self):
        self['key_green'].setText('')
        self['key_yellow'].setText('')
        if len(self.disk[5]) > 0:
            index = self['menu'].getSelectionIndex()
            if self.disk[5][index][2] == 'Linux':
                self['key_green'].setText(_('Check'))
                self['key_yellow'].setText(_('Format'))
            if self.disk[5][index][2] == 'Linux swap':
                self['key_red'].setText('')
            else:
                mp = self.mountpoints.get(self.disk[0], index + 1)
                if len(mp) > 0:
                    self.mounted = True
                    self['key_red'].setText(_('Umount'))
                else:
                    self.mounted = False
                    self['key_red'].setText(_('Mount'))

    def chkfs(self):
        disks = Disks()
        ret = disks.chkfs(self.disk[5][self.index][0][:3], self.index + 1)
        if ret == 0:
            self.session.open(MessageBox, _('Check disk terminated with success'), MessageBox.TYPE_INFO)
        elif ret == -1:
            self.session.open(MessageBox, _('Cannot umount current drive.\nA record in progress, timeshit or some external tools (like samba, swapfile and nfsd) may cause this problem.\nPlease stop this actions/applications and try again'), MessageBox.TYPE_ERROR)
        else:
            self.session.open(MessageBox, _('Error checking disk. The disk may be damaged'), MessageBox.TYPE_ERROR)

    def mkfs(self):
        disks = Disks()
        ret = disks.mkfs(self.disk[5][self.index][0][:3], self.index + 1)
        if ret == 0:
            self.session.open(MessageBox, _('Format terminated with success'), MessageBox.TYPE_INFO)
        elif ret == -2:
            self.session.open(MessageBox, _('Cannot format current drive.\nA record in progress, timeshit or some external tools (like samba, swapfile and nfsd) may cause this problem.\nPlease stop this actions/applications and try again'), MessageBox.TYPE_ERROR)
        else:
            self.session.open(MessageBox, _('Error formatting disk. The disk may be damaged'), MessageBox.TYPE_ERROR)

    def green(self):
        if len(self.disk[5]) > 0:
            index = self['menu'].getSelectionIndex()
            if self.disk[5][index][2] == 'Linux':
                self.index = index
                self.session.open(ExtraActionBox, 'Checking disk %s' % self.disk[5][index][0], 'Checking disk', self.chkfs)

    def yellow(self):
        if len(self.disk[5]) > 0:
            index = self['menu'].getSelectionIndex()
            if self.disk[5][index][2] == 'Linux':
                self.index = index
                self.session.open(ExtraActionBox, 'Formatting disk %s' % self.disk[5][index][0], 'Formatting disk', self.mkfs)

    def refreshMP(self, uirefresh = True):
        self.partitions = []
        self.mountpoints = MountPoints()
        self.mountpoints.read()
        count = 1
        for part in self.disk[5]:
            capacity = '%d MB' % (part[1] / 1048576)
            mp = self.mountpoints.get(self.disk[0], count)
            if len(mp) > 0:
                self.partitions.append(PartitionEntry('Partition %d - %s (%s)' % (count, part[2], mp), capacity))
            else:
                self.partitions.append(PartitionEntry('Partition %d - %s' % (count, part[2]), capacity))
            count += 1

        if uirefresh:
            self['menu'].setList(self.partitions)

    def red(self):
        if len(self.disk[5]) > 0:
            index = self['menu'].getSelectionIndex()
            if self.disk[5][index][2] == 'Linux swap':
                return
        if len(self.partitions) > 0:
            self.sindex = self['menu'].getSelectedIndex()
            if self.mounted:
                mp = self.mountpoints.get(self.disk[0], self.sindex + 1)
                if len(mp) > 0:
                    if self.mountpoints.isMounted(mp):
                        if self.mountpoints.umount(mp):
                            self.mountpoints.delete(mp)
                            self.mountpoints.write()
                        else:
                            self.session.open(MessageBox, _('Cannot umount device.\nA record in progress, timeshit or some external tools (like samba, swapfile and nfsd) may cause this problem.\nPlease stop this actions/applications and try again'), MessageBox.TYPE_ERROR)
                    else:
                        self.mountpoints.delete(mp)
                        self.mountpoints.write()
                self.refreshMP()
            else:
                self.session.openWithCallback(self.refreshMP, HddMount, self.disk[0], self.sindex + 1)

    def quit(self):
        self.close()
