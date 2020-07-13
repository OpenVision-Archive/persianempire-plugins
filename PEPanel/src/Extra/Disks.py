#!/usr/bin/python
# -*- coding: utf-8 -*-
from BoxInfo import BoxInfo
import os
import re
from Components.Console import Console

class Disks:

    def __init__(self):
        self.disks = []
        self.readDisks()
        self.readPartitions()

    def readDisks(self):
        partitions = open('/proc/partitions')
        for part in partitions:
            res = re.sub('\\s+', ' ', part).strip().split(' ')
            if res and len(res) == 4:
                if len(res[3]) == 3 and res[3][:2] == 'sd':
                    self.disks.append([res[3],
                     int(res[2]) * 1024,
                     self.isRemovable(res[3]),
                     self.getModel(res[3]),
                     self.getVendor(res[3]),
                     []])

    def readPartitions(self):
        partitions = open('/proc/partitions')
        for part in partitions:
            res = re.sub('\\s+', ' ', part).strip().split(' ')
            if res and len(res) == 4:
                if len(res[3]) > 3 and res[3][:2] == 'sd':
                    for i in self.disks:
                        if i[0] == res[3][:3]:
                            i[5].append([res[3], int(res[2]) * 1024, self.isLinux(res[3])])
                            break

    def isRemovable(self, device):
        removable = open('/sys/block/%s/removable' % device, 'r').read().strip()
        if removable == '1':
            return True
        return False

    def isLinux(self, device):
        cmd = '/sbin/fdisk -l | grep "/dev/%s" | sed s/\\*// | awk \'{ print $6 " " $7 " " $8 }\'' % device
        fdisk = os.popen(cmd, 'r')
        res = fdisk.read().strip()
        fdisk.close()
        return res

    def getModel(self, device):
        return open('/sys/block/%s/device/model' % device, 'r').read().strip()

    def getVendor(self, device):
        return open('/sys/block/%s/device/vendor' % device, 'r').read().strip()

    def isMounted(self, device):
        mounts = open('/proc/mounts')
        for mount in mounts:
            res = mount.split(' ')
            if res and len(res) > 1:
                if res[0][:8] == '/dev/%s' % device:
                    mounts.close()
                    return True

        mounts.close()
        return False

    def isMountedP(self, device, partition):
        mounts = open('/proc/mounts')
        for mount in mounts:
            res = mount.split(' ')
            if res and len(res) > 1:
                if res[0][:9] == '/dev/%s%s' % (device, partition):
                    mounts.close()
                    return True

        mounts.close()
        return False

    def getMountedP(self, device, partition):
        mounts = open('/proc/mounts')
        for mount in mounts:
            res = mount.split(' ')
            if res and len(res) > 1:
                if res[0] == '/dev/%s%d' % (device, partition):
                    mounts.close()
                    return res[1]

        mounts.close()

    def umount(self, device):
        mounts = open('/proc/mounts')
        for mount in mounts:
            res = mount.split(' ')
            if res and len(res) > 1:
                if res[0][:8] == '/dev/%s' % device:
                    if Console().ePopen('umount %s' % res[0]) != 0:
                        mounts.close()
                        return False

        mounts.close()
        return True

    def umountP(self, device, partition):
        if Console().ePopen('umount /dev/%s%s' % (device, partition)) != 0:
            return False
        return True

    def mountP(self, device, partition, path):
        if Console().ePopen('mount /dev/%s%s %s' % (device, partition, path)) != 0:
            return False
        return True

    def mount(self, fdevice, path):
        if Console().ePopen('mount /dev/%s %s' % (fdevice, path)) != 0:
            return False
        return True

    def fdisk(self, device, size, type):
        if self.isMounted(device):
            if not self.umount(device):
                return -1
        if type == 0:
            flow = '0,\n;\n;\n;\ny\n'
        elif type == 1:
            psize = size / 1048576 / 2
            flow = ',%d\n;\n;\n;\ny\n' % psize
        elif type == 2:
            psize = size / 1048576 / 4 * 3
            flow = ',%d\n;\n;\n;\ny\n' % psize
        elif type == 3:
            psize = size / 1048576 / 3
            flow = ',%d\n,%d\n;\n;\ny\n' % (psize, psize)
        elif type == 4:
            psize = size / 1048576 / 4
            flow = ',%d\n,%d\n,%d\n;\ny\n' % (psize, psize, psize)
        boxinfo = BoxInfo()
        cmd = '%s -f -uM /dev/%s' % (boxinfo.sfdiskBin, device)
        sfdisk = os.popen(cmd, 'w')
        sfdisk.write(flow)
        if sfdisk.close():
            return -2
        return 0

    def chkfs(self, device, partition):
        fdevice = '%s%d' % (device, partition)
        if self.isMountedP(device, partition):
            oldmp = self.getMountedP(device, partition)
            if not self.umountP(device, partition):
                return -1
        else:
            oldmp = ''
        if self.isMountedP(device, partition):
            return -1
        ret = Console().ePopen('/sbin/fsck /dev/%s' % fdevice)
        if len(oldmp) > 0:
            self.mount(fdevice, oldmp)
        if ret == 0:
            return 0
        return -2

    def mkfs(self, device, partition):
        dev = '%s%d' % (device, partition)
        size = 0
        partitions = open('/proc/partitions')
        for part in partitions:
            res = re.sub('\\s+', ' ', part).strip().split(' ')
            if res and len(res) == 4:
                if res[3] == dev:
                    size = int(res[2])
                    break

        if size == 0:
            return -1
        if self.isMountedP(device, partition):
            oldmp = self.getMountedP(device, partition)
            if not self.umountP(device, partition):
                return -2
        else:
            oldmp = ''
        cmd = '/sbin/mkfs.ext3 '
        if size > 4294967296L:
            cmd += '-T largefile '
        cmd += '-m0 /dev/' + dev
        ret = Console().ePopen(cmd)
        if len(oldmp) > 0:
            self.mount(dev, oldmp)
        if ret == 0:
            return 0
        return -3
