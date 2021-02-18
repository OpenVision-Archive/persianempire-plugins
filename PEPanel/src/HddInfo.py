#!/usr/bin/python
# -*- coding: utf-8 -*-
from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config
from Extra.BoxInfo import BoxInfo
import os
import sys
import re
from __init__ import _
from Components.Console import Console


class HddInfo(ConfigListScreen, Screen):

    def __init__(self, session, device):
        Screen.__init__(self, session)
        boxinfo = BoxInfo()
        self.device = device
        self.list = []
        self.list.append(getConfigListEntry(_('Standby timeout:'), config.usage.hdd_standby))
        ConfigListScreen.__init__(self, self.list)
        self['key_green'] = Button('')
        self['key_red'] = Button(_('Ok'))
        self['key_blue'] = Button(_('Exit'))
        self['key_yellow'] = Button('')
        self['model'] = Label('Model: unknow')
        self['serial'] = Label('Serial: unknow')
        self['firmware'] = Label('Firmware: unknow')
        self['cylinders'] = Label('Cylinders: unknow')
        self['heads'] = Label('Heads: unknow')
        self['sectors'] = Label('Sectors: unknow')
        self['readDisk'] = Label('Read disk speed: unknow')
        self['readCache'] = Label('Read disk cache speed: unknow')
        self['temp'] = Label('Disk temperature: unknow')
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'blue': self.keyCancel,
         'red': self.keySave,
         'cancel': self.keyCancel}, -2)
        self.onLayoutFinish.append(self.drawInfo)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('Devicemanager Details'))

    def drawInfo(self):
        device = '/dev/%s' % self.device
        modelRe = re.compile('Model Number:\\s*([\\w\\-]+)')
        serialRe = re.compile('Serial Number:\\s*([\\w\\-]+)')
        firmwareRe = re.compile('Firmware Revision:\\s*([\\w\\-]+)')
        cylindersRe = re.compile('cylinders\\s*(\\d+)\\s*(\\d+)')
        headsRe = re.compile('heads\\s*(\\d+)\\s*(\\d+)')
        sectorsRe = re.compile('sectors/track\\s*(\\d+)\\s*(\\d+)')
        readDiskRe = re.compile('Timing buffered disk reads:\\s*(.*)')
        readCacheRe = re.compile('Timing buffer-cache reads:\\s*(.*)')
        tempRe = re.compile('%s:.*:(.*)' % device)
        Console().ePopen('/sbin/hdparm -S 0 %s' % device)
        hdparm = os.popen('/sbin/hdparm -I %s' % device)
        for line in hdparm:
            model = re.findall(modelRe, line)
            if model:
                self['model'].setText('Model: %s' % model[0].lstrip())
            serial = re.findall(serialRe, line)
            if serial:
                self['serial'].setText('Serial: %s' % serial[0].lstrip())
            firmware = re.findall(firmwareRe, line)
            if firmware:
                self['firmware'].setText('Firmware: %s' % firmware[0].lstrip())
            cylinders = re.findall(cylindersRe, line)
            if cylinders:
                self['cylinders'].setText('Cylinders: %s (max) %s (current)' % (cylinders[0][0].lstrip(), cylinders[0][1].lstrip()))
            heads = re.findall(headsRe, line)
            if heads:
                self['heads'].setText('Heads: %s (max) %s (current)' % (heads[0][0].lstrip(), heads[0][1].lstrip()))
            sectors = re.findall(sectorsRe, line)
            if sectors:
                self['sectors'].setText('Sectors: %s (max) %s (current)' % (sectors[0][0].lstrip(), sectors[0][1].lstrip()))

        hdparm.close()
        hdparm = os.popen('/sbin/hdparm -t %s' % device)
        for line in hdparm:
            readDisk = re.findall(readDiskRe, line)
            if readDisk:
                self['readDisk'].setText('Read disk speed: %s' % readDisk[0].lstrip())

        hdparm.close()
        hdparm = os.popen('/sbin/hdparm -T %s' % device)
        for line in hdparm:
            readCache = re.findall(readCacheRe, line)
            if readCache:
                self['readCache'].setText('Read disk cache speed: %s' % readCache[0].lstrip())

        hdparm.close()
        hddtemp = os.popen('/var/sbin/hddtemp -q %s' % device)
        for line in hddtemp:
            temp = re.findall(tempRe, line)
            if temp:
                self['temp'].setText('Disk temperature: %s' % temp[0].lstrip())

        hddtemp.close()
