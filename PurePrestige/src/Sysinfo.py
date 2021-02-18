#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from enigma import ePicLoad, eTimer, getDesktop
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, pathExists, SCOPE_PLUGINS
from enigma import eTimer, eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, getDesktop, loadPNG, loadPic
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap, MovingPixmap
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.StaticText import StaticText
from Components.FileList import FileList
from Components.AVSwitch import AVSwitch
from Components.Sources.List import List
from Components.MenuList import MenuList
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.ScrollLabel import ScrollLabel
from Components.config import config, ConfigSubsection, ConfigInteger, ConfigSelection, ConfigText, ConfigEnableDisable, KEY_LEFT, KEY_RIGHT, KEY_0, getConfigListEntry
from os import popen, system, path, listdir, remove
from Screens.About import About as screenabout
from Components.About import about as compabout
import os
import sys
import Console2
from Tools.LoadPixmap import LoadPixmap
from Components.Console import Console

c7color = 11403055
c2color = 16753920
c1color = 16776960
c3color = 15657130
c5color = 16711680
c4color = 16729344
c6color = 65407
c8color = 13047173
c9color = 13789470

def getiteminfo(item):
    fname = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/ginfo.txt')
    fp = open(fname, 'r')
    lines = fp.readlines()
    fp.close()
    takeitem = False
    itemline = ''
    for fitem in lines:
        fitem = fitem.strip()
        if fitem == 'start' + item:
            itemline = ''
            takeitem = True
        if takeitem == True and not fitem == 'start' + item and not fitem == 'end' + item:
            if itemline:
                itemline = itemline + '$' + fitem
            else:
                itemline = fitem
        if fitem == 'end' + item:
            return itemline

        def GetFileData(self, fx):
            try:
                flines = open(fx, 'r')
                for line in flines:
                    self.list.append(line)

                flines.close()
                self.setTitle(fx)
            except:
                pass


def getfreespaceinfo():
    fname = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Free_Space.txt')
    flines = open(fname, 'r')
    list = []
    for line in flines:
        newlines = []
        newlines = line.split(' ')
        newitems = []
        for item in newlines:
            item = item.strip()
            if not item == '':
                newitems.append(item)

        list.append(newitems)

    return list
    itemline = ''
    itemslist = []
    totalitems = []
    for fitem in lines:
        fitem = fitem.strip()
        if not fitem == '':
            a = fitem.split(' ')
            for item in a:
                if not item == '':
                    itemslist.append(item)

        totalitems.append(itemslist)

    print(totalitems[0])
    return totalitems


def getdevicesinfo():
    fname = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/devices.txt')
    flines = open(fname, 'r')
    list = []
    for line in flines:
        newlines = []
        newlines = line.split(' ')
        newitems = []
        for item in newlines:
            item = item.strip()
            if line.startswith('   Device Boot') or line.startswith('/dev/'):
                if not item == '' and 'Boot' not in item:
                    newitems.append(item)
            else:
                newitems.append(line)

        print(newitems)
        list.append(newitems)

    return list


def getmountsinfo():
    fname = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Mountpoints.txt')
    flines = open(fname, 'r')
    list = []
    for line in flines:
        newlines = []
        newlines = line.split(' ')
        newitems = []
        for item in newlines:
            item = item.strip()
            if not item == '':
                newitems.append(item)

        list.append(newitems)

    return list


def getfreememoryinfo():
    fname = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Free_Memory.txt')
    flines = open(fname, 'r')
    list = []
    for line in flines:
        newlines = []
        newlines = line.split(' ')
        newitems = []
        for item in newlines:
            item = item.strip()
            if not item == '':
                newitems.append(item)

        list.append(newitems)

    return list


def getprocessinfo():
    fname = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Process_list.txt')
    flines = open(fname, 'r')
    list = []
    for line in flines:
        newlines = []
        newlines = line.split(' ')
        newitems = []
        for item in newlines:
            item = item.strip()
            if not item == '':
                newitems.append(item)

        list.append(newitems)

    return list


def getkernelinfo():
    fname = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Kernel_Modules.txt')
    flines = open(fname, 'r')
    list = []
    for line in flines:
        list.append(line)

    return list


def getScale():
    return AVSwitch().getFramebufferScale()


T_INDEX = 0
T_FRAME_POS = 1
T_PAGE = 2
T_NAME = 3
T_FULL = 4

class showPurePrestigeinfoscreenstandard(Screen):

    def __init__(self, session):
        self.folder = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/infobuttons/')
        self.fillplgfolders()
        piclist = self.fullpath
        path = self.folder
        lastindex = 0
        self.textcolor = config.PPrestige.textcolor.value
        self.color = config.PPrestige.bgcolor.value
        self.mtitle = ' Information'
        dwidth = getDesktop(0).size().width()
        size_w = getDesktop(0).size().width()
        size_h = getDesktop(0).size().height()
        if dwidth == 1280:
            size_w = 650
            size_h = 600
            textsize = 20
            self.spaceX = 35
            self.picX = 180
            self.spaceY = 20
            self.picY = 170
        else:
            textsize = 20
            self.spaceX = 30
            self.picX = 185
            self.spaceY = 20
            self.picY = 156
        self.thumbsX = 3
        self.thumbsY = 3
        self.thumbsC = self.thumbsX * self.thumbsY
        self.positionlist = []
        skincontent = ''
        posX = -1
        for x in range(self.thumbsC):
            posY = x / self.thumbsX
            posX += 1
            if posX >= self.thumbsX:
                posX = 0
            absX = self.spaceX + posX * (self.spaceX + self.picX)
            absY = self.spaceY + posY * (self.spaceY + self.picY)
            self.positionlist.append((absX, absY))
            if dwidth == 1280:
                pass
            skincontent += '<widget source="label' + str(x) + '" render="Label" position="' + str(absX - 25) + ',' + str(absY + self.picY - textsize + 5) + '" size="' + str(self.picX + 15) + ',' + str(textsize) + '" font="Regular;20" zPosition="2" transparent="1" noWrap="1" halign="' + 'center' + '" valign="' + 'center' + '"  foregroundColor="' + self.textcolor + '" />'
            skincontent += '<widget name="thumb' + str(x) + '" position="' + str(absX + 5) + ',' + str(absY + 5) + '" size="' + str(self.picX - 30) + ',' + str(self.picY - 20) + '" zPosition="2" transparent="1" alphatest="on" />'

        if dwidth == 1280:
            self.skin = '<screen position="center,77"  title="' + self.mtitle + '"  size="' + str(size_w) + ',' + str(size_h) + '" > \t\t\t<eLabel position="0,0" zPosition="0" size="' + str(size_w) + ',' + str(size_h) + '" backgroundColor="' + self.color + '" /><widget name="frame" position="20,20" size="145,145" pixmap="~/pic_frame.png" zPosition="1" alphatest="on" />' + skincontent + '</screen>'
        else:
            self.skin = '<screen position="20,center" flags="wfNoBorder" title="PurePrestige"  size="' + str(size_w) + ',' + str(size_h) + '" > \t\t\t<eLabel position="0,0" zPosition="0" size="' + str(size_w) + ',' + str(size_h) + '" backgroundColor="' + self.color + '" /><widget name="frame" position="20,20" size="145,145" pixmap="~/pic_frame.png" zPosition="1" alphatest="on" />' + skincontent + '</screen>'

        Screen.__init__(self, session)
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions',
         'DirectionActions',
         'MovieSelectionActions'], {'cancel': self.Exit,
         'ok': self.KeyOk,
         'left': self.key_left,
         'right': self.key_right,
         'up': self.key_up,
         'down': self.key_down}, -1)
        self['frame'] = MovingPixmap()
        for x in range(self.thumbsC):
            self['label' + str(x)] = StaticText()
            self['thumb' + str(x)] = Pixmap()

        self.Thumbnaillist = []
        self.filelist = []
        self.currPage = -1
        self.dirlistcount = 0
        self.path = path
        index = 0
        framePos = 0
        Page = 0
        for x in piclist:
            if x:
                self.filelist.append((index,
                 framePos,
                 Page,
                 x,
                 path + x))
                index += 1
                framePos += 1
                if framePos > self.thumbsC - 1:
                    framePos = 0
                    Page += 1
            else:
                self.dirlistcount += 1

        self.maxentry = len(self.filelist) - 1
        self.index = lastindex - self.dirlistcount
        if self.index < 0:
            self.index = 0
        self.picload = ePicLoad()
        self.onLayoutFinish.append(self.setPicloadConf)
        self.showPic

    def fillplgfolders(self):
        plgfolders = []
        fullpath = []
        for x in listdir(self.folder):
            if path.isfile(self.folder + x):
                if x.endswith('.png'):
                    plgfolders.append(x)
                    fullpath.append(x)

        self.fullpath = fullpath

    def setPicloadConf(self):
        sc = getScale()
        self.picload.setPara([self['thumb0'].instance.size().width(),
         self['thumb0'].instance.size().height(),
         sc[0],
         sc[1],
         config.PPrestige.cache.value,
         int(config.PPrestige.resize.value),
         self.color])
        self.initFrame()
        self.paintFrame()

    def initFrame(self):
        self.positionlist = []
        for x in range(self.thumbsC):
            frame_pos = self['thumb' + str(x)].getPosition()
            self.positionlist.append((frame_pos[0] - 5, frame_pos[1] - 5))

        frame_pos = self['thumb0'].getPosition()
        self['frame'].setPosition(frame_pos[0] - 5, frame_pos[1] - 5)

    def paintFrame(self):
        if self.maxentry < self.index or self.index < 0:
            return
        pos = self.positionlist[self.filelist[self.index][T_FRAME_POS]]
        self['frame'].moveTo(pos[0], pos[1], 1)
        self['frame'].startMoving()
        if self.currPage != self.filelist[self.index][T_PAGE]:
            self.currPage = self.filelist[self.index][T_PAGE]
            self.newPage()

    def newPage(self):
        self.Thumbnaillist = []
        for x in range(self.thumbsC):
            self['label' + str(x)].setText('')
            self['thumb' + str(x)].hide()

        for x in self.filelist:
            if x[T_PAGE] == self.currPage:
                self['label' + str(x[T_FRAME_POS])].setText('(' + str(x[T_INDEX] + 1) + ') ' + x[T_NAME])
                self.Thumbnaillist.append([0, x[T_FRAME_POS], x[T_FULL]])

        self['label0'].setText('Image Info')
        self['label1'].setText('General Info')
        self['label2'].setText('Kernel')
        self['label3'].setText('Kernel Modules')
        self['label4'].setText('Free Space')
        self['label5'].setText('Free Memory')
        self['label6'].setText('Process List')
        self['label7'].setText('Mountpoints')
        self['label8'].setText('Network')
        self.showPic()

    def showPic(self, picInfo=''):
        self['thumb' + str(self.Thumbnaillist[0][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/infobuttons/imageinfo.png'))
        self['thumb' + str(self.Thumbnaillist[0][1])].show()
        self['thumb' + str(self.Thumbnaillist[1][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/infobuttons/ginfo.png'))
        self['thumb' + str(self.Thumbnaillist[1][1])].show()
        self['thumb' + str(self.Thumbnaillist[2][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/infobuttons/kernel.png'))
        self['thumb' + str(self.Thumbnaillist[2][1])].show()
        self['thumb' + str(self.Thumbnaillist[3][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/infobuttons/kernelmodules.png'))
        self['thumb' + str(self.Thumbnaillist[3][1])].show()
        self['thumb' + str(self.Thumbnaillist[4][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/infobuttons/freespace.png'))
        self['thumb' + str(self.Thumbnaillist[4][1])].show()
        self['thumb' + str(self.Thumbnaillist[5][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/infobuttons/freememory.png'))
        self['thumb' + str(self.Thumbnaillist[5][1])].show()
        self['thumb' + str(self.Thumbnaillist[6][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/infobuttons/process.png'))
        self['thumb' + str(self.Thumbnaillist[6][1])].show()
        self['thumb' + str(self.Thumbnaillist[7][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/infobuttons/mountpoints.png'))
        self['thumb' + str(self.Thumbnaillist[7][1])].show()
        self['thumb' + str(self.Thumbnaillist[8][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/infobuttons/netperformance.png'))
        self['thumb' + str(self.Thumbnaillist[8][1])].show()

    def key_left(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.maxentry
        self.paintFrame()

    def key_right(self):
        self.index += 1
        if self.index > self.maxentry:
            self.index = 0
        self.paintFrame()

    def key_up(self):
        self.index -= self.thumbsX
        if self.index < 0:
            self.index = self.maxentry
        self.paintFrame()

    def key_down(self):
        self.index += self.thumbsX
        if self.index > self.maxentry:
            self.index = 0
        self.paintFrame()

    def KeyOk(self):
        self.keyNumberGlobal(self.index)

    def keyNumberGlobal(self, idx):
        sel = self['label' + str(self.index)].getText()
        if sel == _('Image Info'):
            self.session.open(screenabout)
        elif sel == _('General Info'):
            self.session.open(PurePrestigeginfo)
        elif sel == _('Free Space'):
            self.session.open(PurePrestigefreespace)
        elif sel == _('Mountpoints'):
            self.session.open(PurePrestigemountsinfo)
        elif sel == _('Process List'):
            self.session.open(PurePrestigeprocessinfo)
        elif sel == _('Kernel Modules'):
            self.session.open(PurePrestigekernelinfo)
        elif sel == _('Free Memory'):
            self.session.open(PurePrestigefreememoryinfo)
        else:
            self.startscript(sel)

    def startscript(self, sel):
        val = sel
        script = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/%s.sh' % val)
        dom = sel
        instr = val
        endstr = 'Press ok to exit'
        try:
            os.chmod(script, 755)
        except:
            self.setTitle(script)

        Console().ePopen('%s >%s') % (script, resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/currinfo.txt'))
        self.session.open(Console2.PurePrestigeConsole2, _('Reading: %s') % dom, [script], None, False, instr, endstr)
        return

    def callbackView(self, val=0):
        self.index = val
        if self.old_index != self.index:
            self.paintFrame()

    def Exit(self):
        del self.picload
        self.close(self.index + self.dirlistcount)

    def restartenigma(self):
        Console().ePopen('killall -9 enigma2')


class PurePrestigedevicesinfo(Screen):
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
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frame.png" position="0,0" size="920,600"/>\t\n       \n                <widget name="list" position="15,30" size="890,500" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\n           \n                <widget name="list" position="20,30" size="600,500" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\n                </screen>'

    def __init__(self, session):
        self.skin = PurePrestigedevicesinfo.skin
        Screen.__init__(self, session)
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        list = []
        self.list = list
        self['actions'] = ActionMap(['ColorActions', 'SetupActions'], {'ok': self.close,
         'cancel': self.close}, -2)
        self.executeinfo()
        self.onShow.append(self.getinfo)

    def executeinfo(self):
        script = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/devices.sh')
        try:
            os.chmod(script, 755)
        except:
            pass

        Console().ePopen('%s >%s') % (script, resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/devices.txt'))

    def getinfo(self):
        self.totallist = totalitems = []
        totalitems = getdevicesinfo()
        self.totallist = totalitems
        self.ListToMulticontent()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.totallist
        print('totallist', len(self.totallist))
        self['list'].l.setItemHeight(50)
        self['list'].l.setFont(0, gFont('Regular', 25))
        self.newdisk = False
        for i in range(0, len(self.events)):
            item = self.events[i]
            print(item)
            if len(self.events[i]) > 1:
                try:
                    item = self.events[i][0]
                except:
                    item = ''

                try:
                    total = self.events[i][1]
                except:
                    total = ''

                try:
                    used = self.events[i][2]
                except:
                    used = ''

                try:
                    free = self.events[i][3]
                except:
                    free = ''

                try:
                    shared = self.events[i][4]
                except:
                    shared = ''

                try:
                    buffers = self.events[i][5]
                except:
                    buffers = ''

                try:
                    system = self.events[i][6]
                except:
                    system = ''

                if len(self.events[i][0]) > 30:
                    if 'Disk' in item:
                        res = []
                        png = LoadPixmap(resolveFilename(SCOPE_PLUGINS, 'Extensions/LiveFootBall/images/slider.png'))
                        res.append(MultiContentEntryText(pos=(0, 10), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(15, 10), size=(890, 120), png=png))
                        theevents.append(res)
                        res = []
                        res.append(MultiContentEntryText(pos=(0, 10), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
                        res.append(MultiContentEntryText(pos=(20, 10), size=(850, 120), font=0, flags=RT_HALIGN_LEFT, text=item, color=c6color, color_sel=16777215))
                    else:
                        res.append(MultiContentEntryText(pos=(0, 10), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
                        res.append(MultiContentEntryText(pos=(20, 10), size=(850, 120), font=0, flags=RT_HALIGN_LEFT, text=item, color=c6color, color_sel=16777215))
                else:
                    res.append(MultiContentEntryText(pos=(0, 10), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(20, 10), size=(150, 120), font=0, flags=RT_HALIGN_LEFT, text=item, color=c6color, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(170, 10), size=(100, 120), font=0, flags=RT_HALIGN_LEFT, text=total, color=c2color, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(270, 10), size=(100, 120), font=0, flags=RT_HALIGN_LEFT, text=used, color=16777215, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(370, 10), size=(150, 120), font=0, flags=RT_HALIGN_LEFT, text=free, color=c3color, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(520, 10), size=(150, 120), font=0, flags=RT_HALIGN_LEFT, text=shared, color=c4color, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(670, 10), size=(100, 120), font=0, flags=RT_HALIGN_LEFT, text=buffers, color=c5color, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(770, 10), size=(130, 120), font=0, flags=RT_HALIGN_LEFT, text=system, color=c5color, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()


class PurePrestigekernelinfo(Screen):
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
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frame.png" position="0,0" size="920,600"/>\t\n       \n                <widget name="list" position="15,75" size="890,450" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\n           \n                <widget name="list" position="20,35" size="600,450" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\n                </screen>'

    def __init__(self, session):
        self.skin = PurePrestigekernelinfo.skin
        Screen.__init__(self, session)
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        list = []
        self.list = list
        self['actions'] = ActionMap(['ColorActions', 'SetupActions'], {'ok': self.close,
         'cancel': self.close}, -2)
        self.executeinfo()
        self.onShow.append(self.getinfo)

    def executeinfo(self):
        script = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Kernel_Modules.sh')
        try:
            os.chmod(script, 755)
        except:
            pass

        Console().ePopen('%s >%s') % (script, resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Kernel_Modules.txt'))

    def getinfo(self):
        self.totallist = totalitems = []
        totalitems = getkernelinfo()
        self.totallist = totalitems
        self.ListToMulticontent()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.totallist
        print('totallist', len(self.totallist))
        self['list'].l.setItemHeight(50)
        self['list'].l.setFont(0, gFont('Regular', 25))
        self.longitem = False
        for i in range(0, len(self.events)):
            item = self.events[i]
            print(item)
            if len(self.events[i]) > 0:
                item = self.events[i]
                res.append(MultiContentEntryText(pos=(0, 10), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(20, 10), size=(880, 120), font=0, flags=RT_HALIGN_LEFT, text=item, color=c6color, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()


class PurePrestigeprocessinfo(Screen):
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
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frame.png" position="0,0" size="920,600"/>\t\n       \n                <widget name="list" position="15,75" size="890,450" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\n           \n                <widget name="list" position="20,35" size="600,450" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\n                </screen>'

    def __init__(self, session):
        self.skin = PurePrestigeprocessinfo.skin
        Screen.__init__(self, session)
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        list = []
        self.list = list
        self['actions'] = ActionMap(['ColorActions', 'SetupActions'], {'ok': self.close,
         'cancel': self.close}, -2)
        self.executeinfo()
        self.onShow.append(self.getinfo)

    def executeinfo(self):
        script = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Process_list.sh')
        try:
            os.chmod(script, 755)
        except:
            pass

        Console().ePopen('%s >%s') % (script, resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Process_list.txt'))

    def getinfo(self):
        self.totallist = totalitems = []
        totalitems = getprocessinfo()
        self.totallist = totalitems
        self.ListToMulticontent()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.totallist
        print('totallist', len(self.totallist))
        self['list'].l.setItemHeight(50)
        self['list'].l.setFont(0, gFont('Regular', 25))
        self.longitem = False
        for i in range(0, len(self.events)):
            item = self.events[i]
            print(item)
            if len(self.events[i]) > 1:
                pid = self.events[i][0]
                user = self.events[i][1]
                VSZ = self.events[i][2]
                stat = self.events[i][3]
                command = self.events[i][4]
                res.append(MultiContentEntryText(pos=(0, 10), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(20, 10), size=(80, 120), font=0, flags=RT_HALIGN_LEFT, text=pid, color=c6color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(100, 10), size=(100, 120), font=0, flags=RT_HALIGN_LEFT, text=user, color=c2color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(200, 10), size=(90, 120), font=0, flags=RT_HALIGN_LEFT, text=VSZ, color=16777215, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(290, 10), size=(100, 120), font=0, flags=RT_HALIGN_LEFT, text=stat, color=c3color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(390, 10), size=(490, 120), font=0, flags=RT_HALIGN_LEFT, text=command, color=c4color, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()


class PurePrestigefreememoryinfo(Screen):
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
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frame.png" position="0,0" size="920,600"/>\t\n       \n                <widget name="list" position="15,75" size="890,450" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\n           \n                <widget name="list" position="20,35" size="600,450" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\n                </screen>'

    def __init__(self, session):
        self.skin = PurePrestigefreememoryinfo.skin
        Screen.__init__(self, session)
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        list = []
        self.list = list
        self['actions'] = ActionMap(['ColorActions', 'SetupActions'], {'ok': self.close,
         'cancel': self.close}, -2)
        self.executeinfo()
        self.onShow.append(self.getinfo)

    def executeinfo(self):
        script = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Free_Memory.sh')
        try:
            os.chmod(script, 755)
        except:
            pass

        Console().ePopen('%s >%s') % (script, resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Free_Memory.txt'))

    def getinfo(self):
        self.totallist = totalitems = []
        totalitems = getfreememoryinfo()
        self.totallist = totalitems
        self.ListToMulticontent()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.totallist
        print('totallist', len(self.totallist))
        self['list'].l.setItemHeight(50)
        self['list'].l.setFont(0, gFont('Regular', 25))
        self.longitem = False
        for i in range(0, len(self.events)):
            item = self.events[i]
            print(item)
            if len(self.events[i]) > 1:
                try:
                    item = self.events[i][0]
                except:
                    item = ''

                try:
                    total = self.events[i][1]
                except:
                    total = ''

                try:
                    used = self.events[i][2]
                except:
                    used = ''

                try:
                    free = self.events[i][3]
                except:
                    free = ''

                try:
                    shared = self.events[i][4]
                except:
                    shared = ''

                try:
                    buffers = self.events[i][5]
                except:
                    buffers = ''

                if i == 0:
                    item = ''
                    total = 'total'
                    used = 'used'
                    free = 'free'
                    shared = 'shared'
                    buffers = 'buffers'
                res.append(MultiContentEntryText(pos=(0, 10), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(20, 10), size=(150, 120), font=0, flags=RT_HALIGN_LEFT, text=item, color=c6color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(170, 10), size=(150, 120), font=0, flags=RT_HALIGN_LEFT, text=total, color=c2color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(320, 10), size=(150, 120), font=0, flags=RT_HALIGN_LEFT, text=used, color=16777215, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(470, 10), size=(150, 120), font=0, flags=RT_HALIGN_LEFT, text=free, color=c3color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(630, 10), size=(150, 120), font=0, flags=RT_HALIGN_LEFT, text=shared, color=c4color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(780, 10), size=(120, 120), font=0, flags=RT_HALIGN_LEFT, text=buffers, color=c4color, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()


class PurePrestigemountsinfo(Screen):
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
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frame.png" position="0,0" size="920,600"/>\t\n       \n                <widget name="list" position="15,75" size="890,450" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\n           \n                <widget name="list" position="20,35" size="600,450" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\n                </screen>'

    def __init__(self, session):
        self.skin = PurePrestigemountsinfo.skin
        Screen.__init__(self, session)
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        list = []
        self.list = list
        self['actions'] = ActionMap(['ColorActions', 'SetupActions'], {'ok': self.close,
         'cancel': self.close}, -2)
        self.executeinfo()
        self.onShow.append(self.getinfo)

    def executeinfo(self):
        script = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Mountpoints.sh')
        try:
            os.chmod(script, 755)
        except:
            pass

        Console().ePopen('%s >%s') % (script, resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Mountpoints.txt'))

    def getinfo(self):
        self.totallist = totalitems = []
        totalitems = getmountsinfo()
        self.totallist = totalitems
        self.ListToMulticontent()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.totallist
        print('totallist', len(self.totallist))
        self['list'].l.setItemHeight(50)
        self['list'].l.setFont(0, gFont('Regular', 25))
        self.longitem = False
        for i in range(0, len(self.events)):
            item = self.events[i]
            print(item)
            if len(self.events[i]) > 1:
                rootfs = self.events[i][0]
                on = self.events[i][1]
                slash = self.events[i][2]
                typem = self.events[i][3]
                rootfs2 = self.events[i][4]
                try:
                    rw = self.events[i][5]
                except:
                    rw = ''

                res.append(MultiContentEntryText(pos=(0, 10), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(20, 10), size=(200, 120), font=0, flags=RT_HALIGN_LEFT, text=rootfs, color=c6color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(220, 10), size=(200, 120), font=0, flags=RT_HALIGN_LEFT, text=slash, color=c2color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(420, 10), size=(150, 120), font=0, flags=RT_HALIGN_LEFT, text=rootfs2, color=16777215, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(570, 10), size=(330, 120), font=0, flags=RT_HALIGN_LEFT, text=rw, color=c3color, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()


class PurePrestigefreespace(Screen):
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
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frame.png" position="0,0" size="920,600"/>\t\n       \n                <widget name="list" position="15,75" size="890,450" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\n           \n                <widget name="list" position="20,35" size="600,450" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\n                </screen>'

    def __init__(self, session):
        self.skin = PurePrestigefreespace.skin
        Screen.__init__(self, session)
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        list = []
        self.list = list
        self['actions'] = ActionMap(['ColorActions', 'SetupActions'], {'ok': self.close,
         'cancel': self.close}, -2)
        self.executeinfo()
        self.onShow.append(self.getinfo)

    def executeinfo(self):
        script = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Free_Space.sh')
        try:
            os.chmod(script, 755)
        except:
            pass

        Console().ePopen('%s >%s') % (script, resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/Free_Space.txt'))

    def getinfo(self):
        self.totallist = totalitems = []
        totalitems = getfreespaceinfo()
        self.totallist = totalitems
        self.ListToMulticontent()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.totallist
        print('totallist', len(self.totallist))
        self['list'].l.setItemHeight(50)
        self['list'].l.setFont(0, gFont('Regular', 25))
        self.longitem = False
        for i in range(0, len(self.events)):
            item = self.events[i]
            print(item)
            if len(self.events[i]) > 1:
                item = self.events[i][0]
                size = self.events[i][1]
                used = self.events[i][2]
                available = self.events[i][3]
                use = self.events[i][4]
                try:
                    mounted = self.events[i][5]
                except:
                    mounted = ''

                if mounted == 'Mounted':
                    mounted = 'Mounted on'
                if self.longitem == False:
                    res.append(MultiContentEntryText(pos=(0, 10), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(20, 10), size=(200, 120), font=0, flags=RT_HALIGN_LEFT, text=item, color=c6color, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(220, 10), size=(100, 120), font=0, flags=RT_HALIGN_LEFT, text=size, color=c2color, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(320, 10), size=(100, 120), font=0, flags=RT_HALIGN_LEFT, text=used, color=16777215, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(420, 10), size=(150, 120), font=0, flags=RT_HALIGN_LEFT, text=available, color=c3color, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(570, 10), size=(100, 120), font=0, flags=RT_HALIGN_LEFT, text=use, color=c4color, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(670, 10), size=(200, 120), font=0, flags=RT_HALIGN_LEFT, text=mounted, color=c5color, color_sel=16777215))
                else:
                    res.append(MultiContentEntryText(pos=(0, 10), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(20, 10), size=(200, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=c1color, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(220, 10), size=(100, 120), font=0, flags=RT_HALIGN_LEFT, text=item, color=c2color, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(320, 10), size=(100, 120), font=0, flags=RT_HALIGN_LEFT, text=size, color=16777215, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(420, 10), size=(100, 120), font=0, flags=RT_HALIGN_LEFT, text=used, color=c3color, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(570, 10), size=(100, 120), font=0, flags=RT_HALIGN_LEFT, text=available, color=c4color, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(670, 10), size=(230, 120), font=0, flags=RT_HALIGN_LEFT, text=use, color=c5color, color_sel=16777215))
                    self.longitem = False
            else:
                self.longitem = True
                try:
                    item = self.events[i][0]
                    res.append(MultiContentEntryText(pos=(0, 10), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
                    res.append(MultiContentEntryText(pos=(20, 10), size=(500, 120), font=0, flags=RT_HALIGN_LEFT, text=item, color=c6color, color_sel=16777215))
                except:
                    pass

            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()


class PurePrestigeginfo(Screen):
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
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frame.png" position="0,0" size="920,600"/>\t\n       \n                <widget name="list" position="15,75" size="890,450" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\n           \n                <widget name="list" position="20,35" size="600,450" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\n                </screen>'

    def __init__(self, session):
        self.skin = PurePrestigeginfo.skin
        Screen.__init__(self, session)
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        list = []
        self.list = list
        self['actions'] = ActionMap(['ColorActions', 'SetupActions'], {'ok': self.close,
         'cancel': self.close}, -2)
        self.executeinfo()
        self.onShow.append(self.getinfo)

    def executeinfo(self):
        script = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/getinfo.sh')
        try:
            os.chmod(script, 755)
        except:
            pass

        Console().ePopen('%s >%s') % (script, resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/ginfo.txt'))

    def getinfo(self):
        self.list.append(['Image', compabout.getImageVersionString()])
        self.list.append(['Enigma', compabout.getEnigmaVersionString()])
        self.list.append(['Model', getiteminfo('hostname')])
        info = getiteminfo('drivers')
        info = info.replace('dreambox-dvb-modules', '')
        self.list.append(['dvb-modules', info])
        info = getiteminfo('kernel')
        a = info.split('(')
        if len(a) > 1:
            info = a[0]
        self.list.append(['linux version', info])
        self.list.append(['second stage', getiteminfo('2stage')])
        self.list.append(['up Time', getiteminfo('uptime')])
        info = getiteminfo('mac')
        b = info.split('HWaddr')
        if len(b) > 1:
            info = b[1]
        self.list.append(['mac address', info])
        info = getiteminfo('ip')
        c = info.split(' ')
        if len(c) > 1:
            info = c[1]
        info = info.replace('addr', '')
        self.list.append(['ip address', info])
        self.ListToMulticontent()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.list
        self['list'].l.setItemHeight(50)
        self['list'].l.setFont(0, gFont('Regular', 25))
        for i in range(0, len(self.events)):
            item = self.events[i]
            labelinfo = item[0]
            info = item[1]
            print(item)
            print(labelinfo)
            print(info)
            res.append(MultiContentEntryText(pos=(0, 10), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
            res.append(MultiContentEntryText(pos=(30, 10), size=(200, 120), font=0, flags=RT_HALIGN_LEFT, text=labelinfo, color=c1color, color_sel=16777215))
            res.append(MultiContentEntryText(pos=(230, 10), size=(660, 120), font=0, flags=RT_HALIGN_LEFT, text=info, color=c3color, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()
        self['list'].selectionEnabled(False)
