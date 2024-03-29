# -*- coding: utf-8 -*-
from enigma import *
from Screens.Screen import Screen
from Components.Label import Label
from Components.Button import Button
from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import *
from .Extra.BoxInfo import BoxInfo
import os
import re
import string
from .__init__ import _
from Components.Console import Console


class Swap(ConfigListScreen, Screen):

    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        self.enable = 0
        self.size = '131072'
        self.place = '/media/usb'
        self.filename = 'swapfile'
        boxinfo = BoxInfo()
        self.settingsSwap = boxinfo.settingsSwap
        self.load()
        self.list = []
        self.list.append(getConfigListEntry(_('Enabled:'), ConfigYesNo(default=self.enable)))
        self.list.append(getConfigListEntry(_('Size:'), ConfigSelection(default=self.size, choices=[('8192', _('8 MB')),
         ('16384', _('16 MB')),
         ('32768', _('32 MB')),
         ('65536', _('64 MB')),
         ('131072', _('128 MB')),
         ('262144', _('256 MB')),
         ('524288', _('512 MB')),
         ('1048576', _('1 GB'))])))
        self.list.append(getConfigListEntry(_('Place:'), ConfigSelection(choices=['/media/hdd',
         '/media/usb',
         '/media/usb1',
         '/media/usb2',
         '/media/usb3',
         '/media/cf',
         '/media/mmc1'], default=self.place)))
        self.list.append(getConfigListEntry(_('File name:'), ConfigText(default=self.filename, fixed_size=False)))
        ConfigListScreen.__init__(self, self.list)
        self['key_red'] = Button(_('Ok'))
        self['key_green'] = Button('')
        self['key_yellow'] = Button('')
        self['key_blue'] = Button(_('Exit'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'CiSelectionActions'], {'red': self.ok,
         'ok': self.ok,
         'blue': self.cancel,
         'cancel': self.cancel}, -2)
        self['status'] = Label()
        swaps = self.getActivedSwaps()
        if len(swaps) > 0:
            self['status'].setText(_('Actived on %s (%s bytes)') % (swaps[0][0], swaps[0][2]))
        else:
            self['status'].setText(_('Not active'))

    def getActivedSwaps(self):
        ret = list()
        counter = 0
        swaps = open('/proc/swaps')
        regexp = re.compile('\\s+')
        for line in swaps:
            if counter > 0:
                ret.append(regexp.split(line))
            counter += 1

        return ret

    def ok(self):
        self.enable = self.list[0][1].getValue()
        self.size = self.list[1][1].getValue()
        self.place = self.list[2][1].getValue()
        self.filename = self.list[3][1].getValue()
        self.save()
        swaps = self.getActivedSwaps()
        for swap in swaps:
            Console().ePopen('/sbin/swapoff %s' % swap[0])

        if self.enable:
            Console().ePopen('/bin/dd if=/dev/zero of=%s bs=1024 count=%s' % (os.path.join(self.place, self.filename), self.size))
            Console().ePopen('/sbin/mkswap %s' % os.path.join(self.place, self.filename))
            Console().ePopen('/sbin/swapon %s' % os.path.join(self.place, self.filename))
        self.close()

    def cancel(self):
        self.close(False)

    def load(self):
        try:
            f = open(self.settingsSwap, 'r')
        except Exception as e:
            return

        import re
        commentRe = re.compile('#(.*)')
        entryRe = re.compile('(.*)=(.*)')
        for line in f.readlines():
            comment = re.findall(commentRe, line)
            if not comment:
                entry = re.findall(entryRe, line)
                if entry:
                    key = entry[0][0].strip()
                    value = entry[0][1].strip()
                    if key == 'enable':
                        self.enable = int(value)
                    elif key == 'size':
                        self.size = value
                    elif key == 'place':
                        self.place = value
                    elif key == 'filename':
                        self.filename = value

        f.close()

    def save(self):
        try:
            f = open(self.settingsSwap, 'w')
        except Exception as e:
            return

        f.write('enable=%d\n' % self.enable)
        f.write('size=%s\n' % self.size)
        f.write('place=%s\n' % self.place)
        f.write('filename=%s\n' % self.filename)
        f.close()
        try:
            os.chmod('/etc/init.d/swap', 493)
            os.symlink('/etc/init.d/swap', '/etc/rcS.d/S60swap')
        except OSError:
            print('[PEPanel] symlink already exists. do nothing.')
