#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from struct import pack
from enigma import *
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Screens.ChoiceBox import ChoiceBox
from Components.ScrollLabel import ScrollLabel
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Label import Label, MultiColorLabel
from Components.GUIComponent import *
from Components.MenuList import MenuList
from Components.Input import Input
from Components.ConfigList import ConfigList
from Components.Button import Button
from Components.Label import Label
from Screens.Console import Console
from Plugins.Plugin import PluginDescriptor
from Screens.ServiceInfo import *
from Plugins.Plugin import PluginDescriptor
from Tools import Notifications
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.config import *
import os
from time import *
import time
import datetime

crushlog_lines = 27
crushlog_bottomline = 0
crushlog_topline = 0
crushfile = ''
session = None
crush_pluginversion = '0.3'

def autostart(reason, **kwargs):
    global session
    if reason == 0 and kwargs.has_key('session'):
        session = kwargs['session']


def main(session, **kwargs):
    session.open(CrashReader)


def Plugins(**kwargs):
    return [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=autostart), PluginDescriptor(name='Crush', description='Enigma2 Crushdump Reader', where=PluginDescriptor.WHERE_PLUGINMENU, icon='crush.png', fnc=main)]


class CrashReader(Screen):
    global HD_Res
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    if HD_Res == True:
        skin = '\n        \t<screen name="CrashReader" position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frame.png" position="0,0" size="920,600"/>\n\t\t\n\n                <widget name="list" position="30,30" size="860,300" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<!--eLabel position="130,140" zPosition="-1" size="160,109" backgroundColor="#222222" /-->\n                <widget name="info" position="0,360" zPosition="2" size="920,140" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t        <ePixmap name="red"    position="70,520"   zPosition="2" size="140,40" pixmap="~/ddbuttons/red.png" transparent="1" alphatest="on" />\n\t        <ePixmap name="green"  position="270,520" zPosition="2" size="140,40" pixmap="~/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t        <ePixmap name="yellow" position="470,520" zPosition="2" size="140,40" pixmap="~/ddbuttons/yellow.png" transparent="1" alphatest="on" /> \n        \t<ePixmap name="blue"   position="670,520" zPosition="2" size="140,40" pixmap="~/ddbuttons/blue.png" transparent="1" alphatest="on" /> \n\n        \t<widget name="key_red" position="70,530" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> \n        \t<widget name="key_green" position="270,530" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> \n                <widget name="key_yellow" position="470,530" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />\n        \t<widget name="key_blue" position="670,530" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />\n                </screen>'
    else:
        skin = '\n        \t<screen name="CrashReader" position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\n\t\t\n\n                <widget name="list" position="50,30" size="564,270" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<!--eLabel position="82,140" zPosition="-1" size="100,81" backgroundColor="#222222" /-->\n                <widget name="info" position="0,270" zPosition="4" size="640,120" font="Regular;18" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t        <ePixmap name="red"    position="59,390"   zPosition="2" size="88,30" pixmap="~/ddbuttons/red.png" transparent="1" alphatest="on" />\n\t        <ePixmap name="green"  position="185,390" zPosition="2" size="88,30" pixmap="~/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t        <ePixmap name="yellow" position="311,390" zPosition="2" size="88,30" pixmap="~/ddbuttons/yellow.png" transparent="1" alphatest="on" /> \n        \t<ePixmap name="blue"   position="437,390" zPosition="2" size="88,30" pixmap="~/ddbuttons/blue.png" transparent="1" alphatest="on" /> \n\n        \t<widget name="key_red" position="59,397" size="88,30" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> \n        \t<widget name="key_green" position="172,397" size="120,30" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> \n                <widget name="key_yellow" position="302,397" size="110,30" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />\n        \t<widget name="key_blue" position="437,397" size="88,30" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />\n                </screen>'

    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        self.skin = CrashReader.skin
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok': self.close,
         'cancel': self.close,
         'green': self.deleteall,
         'red': self.deletecrash,
         'blue': self.readfull,
         'yellow': self.readshort}, -1)
        self['key_green'] = Button(_('delete all'))
        self['key_blue'] = Button(_('show full'))
        self['key_red'] = Button(_('delete'))
        self['key_yellow'] = Button(_('show short'))
        self['info'] = Label()
        list = []
        self['list'] = MenuList(list)
        self['list'].onSelectionChanged.append(self.selectionChanged)
        self.onShown.append(self.filllist)

    def readshort(self):
        try:
            selection = self['list'].getCurrent()[0]
            self.session.open(PurePrestigereaderScreen, self.cfile, 'short')
        except:
            pass

    def readfull(self):
        try:
            selection = self['list'].getCurrent()[0]
            self.session.open(ShowCrushLog, self.cfile, 'full')
        except:
            pass

    def deleteall(self):
        try:
            for name in os.listdir('/media/hdd'):
                if name.endswith('.log'):
                    os.remove('/media/hdd/' + name)

        except:
            pass

        self.filllist()

    def deletecrash(self):
        try:
            os.remove(self.cfile)
        except:
            pass

        self.filllist()

    def selectionChanged(self):
        info = ''
        try:
            selection = self['list'].getCurrent()[0]
            print(selection)
            self.crushfile = selection
            info = self.getcrushtime()
            print(info)
            self.cfile = self['list'].getCurrent()[1]
            self['info'].setText(info)
        except:
            print(info)
            self['info'].setText(info)

    def filllist(self):
        list = self.getCrushList()
        self['list'].setList(list)

    def getcrushtime(self):
        parts = []
        parts2 = []
        parts = self.crushfile.split('_')
        parts2 = parts[2].split('.')
        print(int(parts2[0]))
        crushtime = time.ctime(int(parts2[0]))
        return crushtime

    def getCrushList(self):
        list = []
        try:
            for name in os.listdir('/media/hdd'):
                if (name.endswith('.log') or name.endswith('.xml')) and (name.startswith('enigma2') or name.startswith('gemini2')):
                    list.append((name, '/media/hdd/%s' % name))

            for name in os.listdir('/tmp'):
                if (name.endswith('.log') or name.endswith('.xml')) and (name.startswith('enigma2') or name.startswith('gemini2')):
                    list.append((name, '/tmp/%s' % name))

            list.sort(reverse=True)
        except:
            self['info'].setText('Error in getting crush list.may be /media/hdd is not available')

        return list


class ShowCrushLog(Screen):
    global HD_Res
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    if HD_Res == True:
        skin = '\n        \t\n                <screen name="PurePrestigereaderScreen" position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frametop.png" position="0,0" size="920,600"/>\t\n                <ePixmap pixmap="~/images/frameleft.png" position="0,10" size="10,580"/>\t\n                <ePixmap pixmap="~/images/frameright.png" position="910,10" size="10,580"/>\t\n                <ePixmap pixmap="~/images/framebottom.png" position="0,590" size="920,10"/>\t\n                \n\t\t<widget name="showcrushlog" position="30,30" size="865,555" font="Regular;22"  transparent="1" zPosition="2"  />\n                </screen>'
    else:
        skin = '\n        \t\n                <screen name="PurePrestigereaderScreen" position="center,center" size="580,450" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frametop.png" position="0,0" size="580,450"/>\t\n                <ePixmap pixmap="~/images/frameleft.png" position="0,7" size="6,435"/>\t\n                <ePixmap pixmap="~/images/frameright.png" position="573,7" size="6,435"/>\t\n                <ePixmap pixmap="~/images/framebottom.png" position="0,442" size="580,7"/>\t\n                \n\t\t<widget name="showcrushlog" position="20,20" size="540,410" font="Regular;22"  transparent="1" zPosition="2"  />\n                </screen>'

    def __init__(self, session, cfile = None, type = None):
        global crushlog_bottomline
        global crushfile
        global crushlog_lines
        global crushlog_topline
        Screen.__init__(self, session)
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        self.skin = ShowCrushLog.skin
        crushlog_topline = 0
        crushfile = cfile
        f = open(crushfile, 'r')
        crushlog_bottomline = 1
        line = f.readline()
        print(line)
        while line:
            if len(line) > 1:
                crushlog_bottomline = crushlog_bottomline + 1
            line = f.readline()
            print(line)

        f.close()
        if crushlog_bottomline < crushlog_lines:
            crushlog_topline = 0
            crushlog_bottomline = crushlog_lines
        self['showcrushlog'] = ScrollLabel('\n')
        self.showCrushLogPage()
        self.pagebackward
        self['setupActions'] = ActionMap(['ColorActions', 'SetupActions', 'InfobarMovieListActions'], {'red': self.cancel,
         'cancel': self.cancel,
         'ok': self.cancel,
         'left': self.pagebackward,
         'right': self.pageforward,
         'up': self.backward,
         'down': self.forward})

    def setWindowTitle(self):
        self.setTitle(_('Display Crush Logfile %s') % crushfile)

    def showCrushLogPage(self):
        f = open(crushfile, 'r')
        crushlogtext = ''
        i = 0
        while i < crushlog_topline + crushlog_lines:
            if i > crushlog_topline - 1:
                text = f.readline()
                if len(text) > 1:
                    crushlogtext = crushlogtext + text
            else:
                text = f.readline()
            i = i + 1

        f.close
        self['showcrushlog'].setText(crushlogtext)

    def cancel(self):
        self.close(False)

    def backward(self):
        global crushlog_topline
        crushlog_topline = crushlog_topline - 1
        if crushlog_topline < 0:
            crushlog_topline = 0
        self.showCrushLogPage()

    def forward(self):
        global crushlog_topline
        crushlog_topline = crushlog_topline + 1
        if crushlog_topline > crushlog_bottomline - crushlog_lines:
            crushlog_topline = crushlog_bottomline - crushlog_lines
        self.showCrushLogPage()

    def pagebackward(self):
        global crushlog_topline
        crushlog_topline = crushlog_topline - crushlog_lines
        if crushlog_topline < 0:
            crushlog_topline = 0
        self.showCrushLogPage()

    def pageforward(self):
        global crushlog_topline
        crushlog_topline = crushlog_topline + crushlog_lines
        if crushlog_topline > crushlog_bottomline - crushlog_lines:
            crushlog_topline = crushlog_bottomline - crushlog_lines
        self.showCrushLogPage()


class PurePrestigereaderScreen(Screen):
    global HD_Res
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    if HD_Res == True:
        skin = '\n        \t\n                <screen name="PurePrestigereaderScreen" position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frametop.png" position="0,0" size="920,600"/>\t\n                <ePixmap pixmap="~/images/frameleft.png" position="0,10" size="10,580"/>\t\n                <ePixmap pixmap="~/images/frameright.png" position="910,10" size="10,580"/>\t\n                <ePixmap pixmap="~/images/framebottom.png" position="0,590" size="920,10"/>\t\n                \n\t\t<widget name="text" position="30,30" size="865,555" font="Regular;22"  transparent="1" zPosition="2"  />\n                </screen>'
    else:
        skin = '\n        \t\n                <screen name="PurePrestigereaderScreen" position="center,center" size="580,450" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frametop.png" position="0,0" size="580,450"/>\t\n                <ePixmap pixmap="~/images/frameleft.png" position="0,7" size="6,435"/>\t\n                <ePixmap pixmap="~/images/frameright.png" position="573,7" size="6,435"/>\t\n                <ePixmap pixmap="~/images/framebottom.png" position="0,442" size="580,7"/>\t\n                \n\t\t<widget name="text" position="20,20" size="540,410" font="Regular;22"  transparent="1" zPosition="2"  />\n                </screen>'

    def __init__(self, session, cfile = None, type = None):
        self.skin = PurePrestigereaderScreen.skin
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        Screen.__init__(self, session)
        info = ''
        self.cfile = cfile
        self['text'] = ScrollLabel(info)
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'ok': self.close,
         'cancel': self.close,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown,
         'left': self['text'].pageUp,
         'right': self['text'].pageDown}, -1)
        self.timer = eTimer()
        if type == 'short':
            self.timer.callback.append(self.readcrashshort)
        else:
            self.timer.callback.append(self.readcrashfull)
        self.timer.start(100, 1)

    def readcrashfull(self):
        global crushlog_bottomline
        global crushlog_topline
        crushlog_topline = 0
        f = open(self.cfile, 'r')
        crushlog_bottomline = 1
        line = f.readline()
        print(line)
        alllines = ''
        while line:
            if len(line) > 1:
                crushlog_bottomline = crushlog_bottomline + 1
            line = f.readline()
            alllines = alllines + '\n' + line
            print(line)

        f.close()
        if crushlog_bottomline < crushlog_lines:
            crushlog_topline = 0
            crushlog_bottomline = crushlog_lines
        self['text'].setText('\n')
        f = open(self.cfile, 'r')
        crushlogtext = ''
        i = 0
        while i < crushlog_topline + crushlog_lines:
            if i > crushlog_topline - 1:
                text = f.readline()
                if len(text) > 1:
                    crushlogtext = crushlogtext + text
            else:
                text = f.readline()
            i = i + 1

        f.close
        self['text'].setText(crushlogtext)

    def readcrashshort(self):
        print('short')
        f = open(self.cfile, 'r')
        line = f.readline()
        error = None
        crushfollow = 6
        while line and error is None:
            if line.startswith('Plugin  Extensions/BlockContent failed to load:'):
                error = line
                next = 0
                while next < crushfollow:
                    line = f.readline()
                    if len(line) > 1:
                        error = error + line
                        next = next + 1

            elif line.startswith('FATAL:'):
                error = line
                next = 0
                while next < crushfollow:
                    line = f.readline()
                    if len(line) > 1:
                        error = error + line
                        next = next + 1

            elif line.startswith('EXCEPTION IN PYTHON STARTUP CODE:'):
                error = line
                next = 0
                while next < crushfollow:
                    line = f.readline()
                    if len(line) > 1:
                        error = error + line
                        next = next + 1

            elif line.startswith('PC:'):
                error = line
                next = 0
                while next < crushfollow:
                    line = f.readline()
                    if len(line) > 1:
                        error = error + line
                        next = next + 1

            elif line.startswith('Traceback (most recent call last):'):
                error = line
                next = 0
                while next < crushfollow:
                    line = f.readline()
                    if len(line) > 1:
                        error = error + line
                        next = next + 1

            line = f.readline()

        f.close
        if error:
            print(error)
            f = open('/tmp/crush.log', 'w')
            f.write(error)
            f.close
            self['text'].setText(error)
        else:
            self['text'].setText('no standard error found - better see full Crushlog')
        return

    def readcrash2(self):
        try:
            fp = open(self.cfile, 'r')
            count = 0
            self.labeltext = ''
            while 1:
                s = fp.readline()
                count += 1
                self.labeltext += str(s)
                if not s:
                    break

            fp.close()
            self['text'].setText(self.labeltext)
        except:
            self['text'].setText('unable to read data')
