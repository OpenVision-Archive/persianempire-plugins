#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from enigma import ePicLoad, eTimer, getDesktop
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, pathExists, SCOPE_PLUGINS
from Components.Pixmap import Pixmap, MovingPixmap
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.StaticText import StaticText
from Components.FileList import FileList
from Components.AVSwitch import AVSwitch
from Components.Sources.List import List
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.ScrollLabel import ScrollLabel
from Components.config import config, ConfigSubsection, ConfigInteger, ConfigSelection, ConfigText, ConfigEnableDisable, KEY_LEFT, KEY_RIGHT, KEY_0, getConfigListEntry
from os import popen, system, path, listdir, remove
from Screens.About import About
import os
import sys
import crashreader
import languageone
import datetimechanger
import ScreenGrabber.ScreenGrabber
import Plugins.Extensions.PurePrestige.plugin
import Plugins.Extensions.PurePrestige.Stools.plugin
import Cronmanager.plugin
from Plugins.Extensions.PurePrestige.Stools.passresetter import *
from Components.Console import Console

def getScale():
    return AVSwitch().getFramebufferScale()


T_INDEX = 0
T_FRAME_POS = 1
T_PAGE = 2
T_NAME = 3
T_FULL = 4

class showPurePrestigemoretoolsscreen(Screen):

    def __init__(self, session):
        self.folder = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Stools/toolsbuttons/')
        self.fillplgfolders()
        piclist = self.fullpath
        path = self.folder
        lastindex = 0
        self.textcolor = config.PPrestige.textcolor.value
        self.color = config.PPrestige.bgcolor.value
        self.mtitle = 'PurePrestige Tools-2'
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
                print('label' + str(x[T_FRAME_POS]))

        self['label0'].setText('Langauge manager')
        self['label1'].setText('ScreenGrabber')
        self['label2'].setText('Swap manager')
        self['label3'].setText('Script Manager')
        self['label4'].setText('DateTime settings')
        self['label5'].setText('Password reset')
        self['label6'].setText('Crash Reader')
        self['label7'].setText('Crons manager')
        self['label8'].setText('Back')
        self.showPic()

    def showPic(self, picInfo = ''):
        self['thumb' + str(self.Thumbnaillist[0][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Stools/Moretools/moretoolsbuttons/language.png'))
        self['thumb' + str(self.Thumbnaillist[0][1])].show()
        self['thumb' + str(self.Thumbnaillist[1][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Stools/Moretools/moretoolsbuttons/grabber.png'))
        self['thumb' + str(self.Thumbnaillist[1][1])].show()
        self['thumb' + str(self.Thumbnaillist[2][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Stools/Moretools/moretoolsbuttons/swap.png'))
        self['thumb' + str(self.Thumbnaillist[2][1])].show()
        self['thumb' + str(self.Thumbnaillist[3][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Stools/Moretools/moretoolsbuttons/script.png'))
        self['thumb' + str(self.Thumbnaillist[3][1])].show()
        self['thumb' + str(self.Thumbnaillist[4][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Stools/Moretools/moretoolsbuttons/datechanger.png'))
        self['thumb' + str(self.Thumbnaillist[4][1])].show()
        self['thumb' + str(self.Thumbnaillist[5][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Stools/Moretools/moretoolsbuttons/passreset.png'))
        self['thumb' + str(self.Thumbnaillist[5][1])].show()
        self['thumb' + str(self.Thumbnaillist[6][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Stools/Moretools/moretoolsbuttons/crash.png'))
        self['thumb' + str(self.Thumbnaillist[6][1])].show()
        self['thumb' + str(self.Thumbnaillist[7][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Stools/Moretools/moretoolsbuttons/cronman.png'))
        self['thumb' + str(self.Thumbnaillist[7][1])].show()
        self['thumb' + str(self.Thumbnaillist[8][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Stools/Moretools/moretoolsbuttons/backward.png'))
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
        if self.maxentry < 0:
            return
        self.old_index = self.index
        if self.index == 0:
            self.session.open(languageone.PurePrestigelangsScreen)
        if self.index == 1:
            self.session.open(ScreenGrabber.ScreenGrabber.PurePrestigeScreenGrabberSetup)
        if self.index == 2:
            try:
                from Plugins.SystemPlugins.PEPanel.Swap import Swap
                self.session.open(Swap)
                return
            except:
                return
        if self.index == 3:
            try:
                from Plugins.SystemPlugins.PEPanel.Scripts import *
                self.session.open(Scripts)
                return
            except:
                return
        if self.index == 4:
            self.session.open(datetimechanger.PurePrestigeSetTimeChanger)
        if self.index == 5:
            self.session.open(passreset)
        if self.index == 6:
            self.session.open(crashreader.CrashReader)
        if self.index == 7:
            self.session.open(Cronmanager.plugin.PurePrestigecronsscreen)
        if self.index == 8:
            self.close()
            return

    def callbackView(self, val = 0):
        self.index = val
        if self.old_index != self.index:
            self.paintFrame()

    def Exit(self):
        del self.picload
        self.close(self.index + self.dirlistcount)

    def restartenigma(self):
        Console().ePopen('killall -9 enigma2')
