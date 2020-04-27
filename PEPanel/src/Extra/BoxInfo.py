#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re

class BoxInfo:

    def __init__(self):
        self.isIPBOX = False
        self.isDMM = False
        self.scriptsPath = '/usr/script/'
        self.settingsMounts = '/etc/settings.mounts'
        self.settingsSwap = '/etc/settings.swap'
        self.settingsModules = '/etc/settings.modules'
        self.settingsHdparm = '/etc/settings.hdparm'
        self.sfdiskBin = '/usr/sbin/sfdisk'