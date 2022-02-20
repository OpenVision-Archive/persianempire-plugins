#!/usr/bin/python
# -*- coding: utf-8 -*-
from .BoxInfo import BoxInfo
import os
import re
from Tools.Directories import fileExists
from Components.Console import Console


class MountPoints:

    def __init__(self):
        self.entries = []
        boxinfo = BoxInfo()
        self.settingsMounts = boxinfo.settingsMounts

    def read(self):
        self.entries = []
        try:
            if not fileExists('/etc/settings.mounts'):
                fp = open('/etc/settings.mounts', 'w')
                fp.close()
        except IOError:
            self.session.open(MessageBox, _('Could not create the Mountpoint Mappingfile.'), MessageBox.TYPE_ERROR, 5)

        conf = open(self.settingsMounts, 'r')
        for line in conf:
            res = line.strip().split(':')
            if res and len(res) == 4:
                self.entries.append(res)

        conf.close()

    def write(self):
        conf = open(self.settingsMounts, 'w')
        for entry in self.entries:
            conf.write('%s:%s:%s:%s\n' % (entry[0],
             entry[1],
             entry[2],
             entry[3]))

        conf.close()

    def checkPath(self, path):
        for entry in self.entries:
            if entry[0] == path:
                return True

        return False

    def isMounted(self, path):
        mounts = open('/proc/mounts')
        for mount in mounts:
            res = mount.split(' ')
            if res and len(res) > 1:
                if res[1] == path:
                    mounts.close()
                    return True

        mounts.close()
        return False

    def umount(self, path):
        return Console().ePopen('umount %s' % path) == 0

    def mount(self, device, partition, path):
        return Console().ePopen('[ ! -d %s ] && mkdir %s\nmount /dev/%s%d %s' % (path,
         path,
         device,
         partition,
         path)) == 0

    def exist(self, path):
        for entry in self.entries:
            if entry[0] == path:
                return True

        return False

    def delete(self, path):
        for entry in self.entries:
            if entry[0] == path:
                self.entries.remove(entry)

    def deleteDisk(self, device):
        for i in range(1, 4):
            res = self.get(device, i)
            if len(res) > 0:
                self.delete(res)

    def add(self, device, partition, path):
        vendor = open('/sys/block/%s/device/vendor' % device, 'r').read().strip()
        model = open('/sys/block/%s/device/model' % device, 'r').read().strip()
        for entry in self.entries:
            if entry[1] == model and entry[2] == vendor and int(entry[3]) == partition:
                entry[0] = path
                return

        self.entries.append([path,
         model,
         vendor,
         str(partition)])

    def get(self, device, partition):
        vendor = open('/sys/block/%s/device/vendor' % device, 'r').read().strip()
        model = open('/sys/block/%s/device/model' % device, 'r').read().strip()
        for entry in self.entries:
            if entry[1] == model and entry[2] == vendor and int(entry[3]) == partition:
                return entry[0]

        return ''
