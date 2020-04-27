#!/usr/bin/python
# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
import xml.dom.minidom
import os
from Components.Button import Button
from Tools.Directories import fileExists
from Components.ScrollLabel import ScrollLabel
from enigma import eListboxPythonMultiContent, getDesktop, gFont, loadPNG
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Screens.MessageBox import MessageBox
import urllib
from Components.Label import Label
from Tools.LoadPixmap import LoadPixmap
from Plugins.Extensions.PurePrestige.Console2 import *
from Tools.Directories import resolveFilename, SCOPE_LIBDIR, SCOPE_PLUGINS

def freespace():
    try:
        diskSpace = os.statvfs('/')
        capacity = float(diskSpace.f_bsize * diskSpace.f_blocks)
        available = float(diskSpace.f_bsize * diskSpace.f_bavail)
        fspace = round(float(available / 1048576.0), 2)
        tspace = round(float(capacity / 1048576.0), 1)
        spacestr = 'Free space(' + str(fspace) + 'MB) Total space(' + str(tspace) + 'MB)'
        return spacestr
    except:
        return ''


class PurePrestigeaddonsScreen(Screen):
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w > 1200:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    if HD_Res:
        skin = '\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frame.png" position="0,0" size="920,600" transparent="1"/>\t\n\t\t\t  <widget name="ButtonBluetext" position="40,20" size="200,40" valign="center" halign="left" zPosition="10" font="Regular;22" transparent="1" />\n\t\t\t  <widget name="ButtonBlue" pixmap="~/images/button_blue.png" position="20,30" zPosition="10" size="100,100" transparent="1" alphatest="on" />\n                          <widget name="info" position="250,20" zPosition="4" size="650,65" font="Regular;20" foregroundColor="yellow" transparent="1" halign="left" valign="center" />\n                          <widget name="menu" position="20,70" size="880,500" scrollbarMode="showOnDemand"  transparent="1" zPosition="2" />\n\t                  \n        \t</screen>\n\t\t'
    else:
        skin = '\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520" transparent="1"/>\t\n\t\t\t  <widget name="ButtonBluetext" position="30,10" size="100,40" valign="center" halign="left" zPosition="10" font="Regular;25" transparent="1" />\n\t\t\t  <widget name="ButtonBlue" pixmap="~/images/button_blue.png" position="10,20" zPosition="10" size="100,100" transparent="1" alphatest="on" />\n                          <widget name="info" position="200,10" zPosition="4" size="400,45" font="Regular;20" foregroundColor="yellow" transparent="1" halign="left" valign="center" />\n                          <widget name="menu" position="10,50" size="560,375" scrollbarMode="showOnDemand"  transparent="1" zPosition="2" />\n\t                  \n        \t</screen>\n\t\t'

    def __init__(self, session):
        self.skin = PurePrestigeaddonsScreen.skin
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        Screen.__init__(self, session)
        list = []
        self['menu'] = MenuList(list)
        self['ButtonBlue'] = Pixmap()
        self['ButtonBluetext'] = Label(_('Remove'))
        self['info'] = Label()
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'blue': self.prompt,
         'ok': self.prompt,
         'cancel': self.close}, -2)
        self.fillplugins()

    def getfreespace(self):
        fspace = freespace()
        self.freespace = fspace
        self['info'].setText(self.freespace)

    def fillplgfolders(self):
        fname = resolveFilename(SCOPE_PLUGINS, 'Extensions')
        list = []
        plgfolders = []
        self['menu'].setList(plgfolders)
        path = resolveFilename(SCOPE_PLUGINS, 'Extensions/')
        self.path = path
        for x in os.listdir(path):
            if os.path.isfile(path + x):
                pass
            else:
                plgfolders.append(x)

        self.listfolders(plgfolders)
        self.getfreespace()

    def listfolders(self, plgfolders):
        plgfolders.sort()
        if len(plgfolders) > 0:
            self['menu'].setList(plgfolders)
            self['ButtonBluetext'].show()
        else:
            self['ButtonBluetext'].hide()

    def fillplugins(self):
        fname = resolveFilename(SCOPE_LIBDIR, 'opkg/status')
        packs = []
        status = []
        netpack = []
        for line in open(fname, 'r').readlines():
            if line.startswith('Package'):
                packs.append(line)
            if line.startswith('Status'):
                status.append(line)

        i = 0
        for x in status:
            if 'user' in x:
                f = packs[i]
                f = f.replace('Package:', '')
                f = f.strip()
                netpack.append(f)
            i = i + 1

        self.netpacks = netpack
        self.fillplgfolders()

    def getpack(self, folder):
        path = resolveFilename(SCOPE_PLUGINS, 'Extensions/')
        folderpath = path + folder
        for x in self.netpacks:
            fname = resolveFilename(SCOPE_LIBDIR, 'opkg/info/' + x + '.list')
            if fileExists(fname):
                for line in open(fname, 'r').readlines():
                    if folderpath in line:
                        return x

        return ''

    def prompt(self):
        path = resolveFilename(SCOPE_PLUGINS, 'Extensions/')
        instr = 'Please wait while plugin being  uninstalled or removed...'
        endstr = 'Press OK to exit'
        try:
            selectedfolder = self['menu'].getCurrent()
            pack = self.getpack(selectedfolder)
            folderpath = path + selectedfolder
            if pack == '':
                dom = selectedfolder
                com = folderpath
                self.session.open(Console2.PurePrestigeConsole2, _('Removing: %s') % dom, ['rm -rf %s' % com], self.fillplugins, False, instr, endstr)
            else:
                dom = pack
                com = pack
                self.session.open(Console2.PurePrestigeConsole2, _('Removing: %s') % dom, ['opkg remove %s' % com], self.fillplugins, False, instr, endstr)
        except:
            pass
