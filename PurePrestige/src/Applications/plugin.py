#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from enigma import ePicLoad, eTimer, getDesktop
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, pathExists, SCOPE_PLUGINS, fileExists
from Screens.MessageBox import MessageBox
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
from Plugins.Extensions.PurePrestige.Console2 import *
from Components.Console import Console
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

def gethostname():
    path = '/etc/hostname'
    hostname = 'None'
    if os.path.exists(path):
        f = open(path, 'r')
        hostname = f.read()
        f.close()
    return 'None'

hostname = gethostname()

def getScale():
    return AVSwitch().getFramebufferScale()


T_INDEX = 0
T_FRAME_POS = 1
T_PAGE = 2
T_NAME = 3
T_FULL = 4

class showPurePrestigeappscreen(Screen):

    def __init__(self, session):
        self.folder = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Applications/appbuttons/')
        self.fillplgfolders()
        piclist = self.fullpath
        path = self.folder
        lastindex = 0
        self.textcolor = config.PPrestige.textcolor.value
        self.color = config.PPrestige.bgcolor.value
        self.mtitle = 'Applications'
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
        self.thumbsY = 4
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
            self.skin = '<screen position="20,center" flags="wfNoBorder" title="TSimage Panel"  size="' + str(size_w) + ',' + str(size_h) + '" > \t\t\t<eLabel position="0,0" zPosition="0" size="' + str(size_w) + ',' + str(size_h) + '" backgroundColor="' + self.color + '" /><widget name="frame" position="20,20" size="145,145" pixmap="~/pic_frame.png" zPosition="1" alphatest="on" />' + skincontent + '</screen>'

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

        self['label0'].setText('Persian Radio')
        self['label1'].setText('Persian Sports')
        self['label2'].setText('Live FootBall')
        self['label3'].setText('MyTube')
        self['label4'].setText('VLC')
        self['label5'].setText('Shoutcast')
        self['label6'].setText('Gmail Reader')
        self['label7'].setText('Google News')
        self['label8'].setText('Foreca Weather')
        self.showPic()

    def showPic(self, picInfo = ''):
        self['thumb' + str(self.Thumbnaillist[0][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Applications/appbuttons/pradio.png'))
        self['thumb' + str(self.Thumbnaillist[0][1])].show()
        self['thumb' + str(self.Thumbnaillist[1][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Applications/appbuttons/persiansoccer.png'))
        self['thumb' + str(self.Thumbnaillist[1][1])].show()
        self['thumb' + str(self.Thumbnaillist[2][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Applications/appbuttons/livefootball.png'))
        self['thumb' + str(self.Thumbnaillist[2][1])].show()
        self['thumb' + str(self.Thumbnaillist[3][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Applications/appbuttons/mytube.png'))
        self['thumb' + str(self.Thumbnaillist[3][1])].show()
        self['thumb' + str(self.Thumbnaillist[4][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Applications/appbuttons/vlc.png'))
        self['thumb' + str(self.Thumbnaillist[4][1])].show()
        self['thumb' + str(self.Thumbnaillist[5][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Applications/appbuttons/shoutcast.png'))
        self['thumb' + str(self.Thumbnaillist[5][1])].show()
        self['thumb' + str(self.Thumbnaillist[6][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Applications/appbuttons/gmail.png'))
        self['thumb' + str(self.Thumbnaillist[6][1])].show()
        self['thumb' + str(self.Thumbnaillist[7][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Applications/appbuttons/gnews.png'))
        self['thumb' + str(self.Thumbnaillist[7][1])].show()
        self['thumb' + str(self.Thumbnaillist[8][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Applications/appbuttons/weather.png'))
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
        print(self.index)
        if self.index == 0:
            pluginpath = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Applications/NetRadioPersian/plugin.pyo')
            self.pluginurl = 'http://mfaraj57.dreamoem.net/applications/enigma2-plugin-extensions-netradiopersian.ipk'
            self.dom = 'NetRadioPersian'
            if fileExists(pluginpath):
                from NetRadioPersian.plugin import persianMenuscrn
                self.session.open(persianMenuscrn)
                return
            self.session.openWithCallback(self.download, MessageBox, _('Application is not available,install now?'), MessageBox.TYPE_YESNO)
        if self.index == 2:
            pluginpath = resolveFilename(SCOPE_PLUGINS, 'Extensions/LiveFootBall/plugin.pyo')
            pluginpathpy = resolveFilename(SCOPE_PLUGINS, 'Extensions/LiveFootBall/plugin.py')
            self.pluginurl = 'http://mfaraj57.dreamoem.net/applications/enigma2-plugin-extensions-livefootball.ipk'
            self.dom = 'LiveFootBall'
            if fileExists(pluginpath) or fileExists(pluginpathpy):
                from Plugins.Extensions.LiveFootBall.plugin import showLiveFootBallscreen
                self.session.open(showLiveFootBallscreen)
                return
            self.session.openWithCallback(self.download, MessageBox, _('Application is not available,install now?'), MessageBox.TYPE_YESNO)
        if self.index == 1:
            pluginpath = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Applications/PersianLiveSoccer/plugin.pyo')
            self.pluginurl = 'http://mfaraj57.dreamoem.net/applications/enigma2-plugin-extensions-persianlivesoccer.ipk'
            self.dom = 'PersianLiveSoccer'
            if fileExists(pluginpath):
                from PersianLiveSoccer.plugin import psoccerbootlogo
                self.session.open(psoccerbootlogo)
                return
            self.session.openWithCallback(self.download, MessageBox, _('Application is not available,install now?'), MessageBox.TYPE_YESNO)
        if self.index == 3:
            pluginpath = resolveFilename(SCOPE_PLUGINS, 'Extensions/MyTube/plugin.pyo')
            pluginpathpy = resolveFilename(SCOPE_PLUGINS, 'Extensions/MyTube/plugin.py')
            self.pluginurl = 'http://mfaraj57.dreamoem.net/applications/python-gdata_1.2.4-r0_mips32el.ipk http://mfaraj57.dreamoem.net/applications/enigma2-plugin-extensions-mytube.ipk'
            self.dom = 'MyTube'
            if fileExists(pluginpath) or fileExists(pluginpathpy):
                import Plugins.Extensions.MyTube.plugin
                reload(Plugins.Extensions.MyTube.plugin)
                Plugins.Extensions.MyTube.plugin.MyTubeMain(self.session)
            else:
                self.session.openWithCallback(self.download, MessageBox, _('Application is not available,install now?'), MessageBox.TYPE_YESNO)
        if self.index == 4:
            pluginpath = resolveFilename(SCOPE_PLUGINS, 'Extensions/VlcPlayer/plugin.pyo')
            pluginpathpy = resolveFilename(SCOPE_PLUGINS, 'Extensions/VlcPlayer/plugin.py')
            self.pluginurl = 'http://mfaraj57.dreamoem.net/applications/enigma2-plugin-extensions-vlcplayer.ipk'
            self.dom = 'VlcPlayer'
            if fileExists(pluginpath) or fileExists(pluginpathpy):
                import Plugins.Extensions.VlcPlayer.plugin
                reload(Plugins.Extensions.VlcPlayer.plugin)
                Plugins.Extensions.VlcPlayer.plugin.main(self.session)
            else:
                self.session.openWithCallback(self.download, MessageBox, _('Application is not available,install now?'), MessageBox.TYPE_YESNO)
        if self.index == 5:
            pluginpath = resolveFilename(SCOPE_PLUGINS, 'Extensions/SHOUTcast/plugin.pyo')
            pluginpathpy = resolveFilename(SCOPE_PLUGINS, 'Extensions/SHOUTcast/plugin.py')
            self.pluginurl = 'http://mfaraj57.dreamoem.net/applications/enigma2-plugin-extensions-shoutcast.ipk'
            self.dom = 'SHOUTcast'
            if fileExists(pluginpath) or fileExists(pluginpathpy):
                import Plugins.Extensions.SHOUTcast.plugin
                reload(Plugins.Extensions.SHOUTcast.plugin)
                Plugins.Extensions.SHOUTcast.plugin.main(self.session)
            else:
                self.session.openWithCallback(self.download, MessageBox, _('Application is not available,install now?'), MessageBox.TYPE_YESNO)
        if self.index == 6:
            pluginpath = resolveFilename(SCOPE_PLUGINS, 'Extensions/GmailReader/plugin.pyo')
            pluginpathpy = resolveFilename(SCOPE_PLUGINS, 'Extensions/GmailReader/plugin.py')
            self.pluginurl = 'http://mfaraj57.dreamoem.net/applications/enigma2-plugin-extensions-gmailreader.ipk'
            self.dom = 'GmailReader'
            if fileExists(pluginpath) or fileExists(pluginpathpy):
                import Plugins.Extensions.GmailReader.plugin
                reload(Plugins.Extensions.GmailReader.plugin)
                Plugins.Extensions.GmailReader.plugin.main(self.session)
            else:
                self.session.openWithCallback(self.download, MessageBox, _('Application is not available,install now?'), MessageBox.TYPE_YESNO)
        if self.index == 7:
            pluginpath = resolveFilename(SCOPE_PLUGINS, 'Extensions/GoogleNews/plugin.pyo')
            pluginpathpy = resolveFilename(SCOPE_PLUGINS, 'Extensions/GoogleNews/plugin.py')
            self.pluginurl = 'http://mfaraj57.dreamoem.net/applications/enigma2-plugin-extensions-googlenews.ipk'
            self.dom = 'GmailReader'
            if fileExists(pluginpath) or fileExists(pluginpathpy):
                import Plugins.Extensions.GoogleNews.plugin
                reload(Plugins.Extensions.GoogleNews.plugin)
                Plugins.Extensions.GoogleNews.plugin.main(self.session)
            else:
                self.session.openWithCallback(self.download, MessageBox, _('Application is not available,install now?'), MessageBox.TYPE_YESNO)
        if self.index == 8:
            pluginpath = resolveFilename(SCOPE_PLUGINS, 'Extensions/Foreca/plugin.pyo')
            pluginpathpy = resolveFilename(SCOPE_PLUGINS, 'Extensions/Foreca/plugin.py')
            self.pluginurl = 'http://mfaraj57.dreamoem.net/applications/python-html_2.6.7-ml8.3_mips32el.ipk http://mfaraj57.dreamoem.net/applications/enigma2-plugin-extensions-foreca.ipk'
            self.dom = 'Foreca'
            if fileExists(pluginpath) or fileExists(pluginpathpy):
                from Plugins.Extensions.Foreca.plugin import ForecaPreview
                self.session.open(ForecaPreview)
                return
            self.session.openWithCallback(self.download, MessageBox, _('Application is not available,install now?'), MessageBox.TYPE_YESNO)

    def downloadgdata(self, result):
        if result:
            dom = 'gdata'
            com = 'http://mfaraj57.dreamoem.net/applications/python-gdata_1.2.4-r0_mips32el.ipk'
            instr = 'Please wait while plugin is being downloaded...'
            endstr = 'installing now mytube ..please wait'
            self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.downloadmytube, True, instr, endstr)

    def downloadmytube(self):
        dom = self.dom
        com = self.pluginurl
        instr = 'Please wait while plugin is being downloaded..'
        endstr = 'Press OK for exit '
        self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], None, False, instr, endstr)
        return

    def download(self, result):
        if result:
            dom = self.dom
            com = self.pluginurl
            instr = 'Please wait while plugin is being downloaded...\n  Restarting enigma2 is required after successful installation'
            endstr = 'Press OK for exit recommonded to start enigma before running the application '
            self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], None, False, instr, endstr)
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
