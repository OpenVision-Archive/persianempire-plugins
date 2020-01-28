from enigma import ePicLoad, eTimer, getDesktop
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, pathExists, SCOPE_MEDIA, copyfile, fileExists, SCOPE_PLUGINS
from xml.dom import Node, minidom
from Screens.MessageBox import MessageBox
from Components.Button import Button
from Components.Label import Label
from Components.Pixmap import Pixmap, MovingPixmap
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.StaticText import StaticText
from Components.AVSwitch import AVSwitch
from Components.Sources.List import List
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.ScrollLabel import ScrollLabel
from Components.config import config, ConfigSubsection, ConfigInteger, ConfigSelection, ConfigText, ConfigEnableDisable, KEY_LEFT, KEY_RIGHT, KEY_0, getConfigListEntry
from os import popen, system, path, listdir, remove
import os
import sys
import Console2
from Screens.Standby import TryQuitMainloop
from Components.About import about
from Components.config import config, ConfigDirectory, ConfigSubsection, ConfigSubList, ConfigEnableDisable, ConfigNumber, ConfigText, ConfigSelection, ConfigYesNo, ConfigPassword, getConfigListEntry, configfile
import PurePrestigeAddOnsManager.plugin
import Stools.MenuUninstaller
import Stools.feeds
import Applications.plugin
from Sysinfo import showPurePrestigeinfoscreenstandard
from Stools.plugin import showPurePrestigetoolsscreen
from Applications.plugin import showPurePrestigeappscreen
from twisted.web.client import downloadPage
import urllib
from GlobalActions import globalActionMap
from keymapparser import readKeymap, removeKeymap
from Screens.InfoBarGenerics import InfoBarPlugins
from Components.Console import Console

def getScale():
    return AVSwitch().getFramebufferScale()


config.plugins.showPurePrestige = ConfigSubsection()
config.PPrestige = ConfigSubsection()
config.plugins.showPurePrestige.scut = ConfigSelection(default='disabled', choices=[('disabled', _('Not assigned')), ('green', _('green'))])
config.plugins.PPrestige = ConfigSubsection()
config.plugins.PPrestige.items = ConfigSelection(default='Disabled', choices=[('All', _('Grab All')),
 ('-v', _('Video only')),
 ('-o', _('OSD only')),
 ('Disabled', _('Off'))])
config.plugins.PPrestige.storedir = ConfigSelection(default='tmp', choices=[('tmp', _('/tmp')), ('hdd', _('/media/hdd'))])
config.plugins.PPrestige.scut = ConfigSelection(default='text', choices=[('text', _('Text')),
 ('help', _('Help')),
 ('info', _('Info')),
 ('video', _('Video')),
 ('mute', _('Mute')),
 ('radio', _('Radio'))])
config.plugins.PPrestige.newsize = ConfigSelection(default='-r800', choices=[('-r1920', _('1920*1080')),
 ('-r800', _('800*450')),
 ('-r600', _('600*337')),
 ('Disabled', _('Skin resolution'))])
config.plugins.PPrestige.format = ConfigSelection(default='-j80', choices=[('-j100', _('jpg100')),
 ('-j80', _('jpg80')),
 ('-j60', _('jpg60')),
 ('-j40', _('jpg40')),
 ('-j20', _('jpg20')),
 ('-p', _('PNG'))])
config.plugins.PPrestige.fixedaspectratio = ConfigSelection(default='Disabled', choices=[('-n', _('Enabled')), ('Disabled', _('Off'))])
config.plugins.PPrestige.always43 = ConfigSelection(default='Disabled', choices=[('-l', _('Enabled')), ('Disabled', _('Off'))])
config.plugins.PPrestige.bicubic = ConfigSelection(default='Disabled', choices=[('-b', _('Enabled')), ('Disabled', _('Off'))])
config.PPrestige.framesize = ConfigInteger(default=30, limits=(5, 99))
config.PPrestige.slidetime = ConfigInteger(default=10, limits=(1, 60))
config.PPrestige.resize = ConfigSelection(default='1', choices=[('0', _('simple')), ('1', _('better'))])
config.PPrestige.cache = ConfigEnableDisable(default=True)
config.PPrestige.lastDir = ConfigText(default=resolveFilename(SCOPE_MEDIA))
config.PPrestige.infoline = ConfigEnableDisable(default=True)
config.PPrestige.loop = ConfigEnableDisable(default=True)
config.PPrestige.bgcolor = ConfigSelection(default='#00000000', choices=[('#00000000', _('black')),
 ('#009eb9ff', _('blue')),
 ('#00ff5a51', _('red')),
 ('#00ffe875', _('yellow')),
 ('#0038FF48', _('green'))])
config.PPrestige.textcolor = ConfigSelection(default='#00ff5a51', choices=[('#6495ED', _('CornflowerBlue')),
 ('#009eb9ff', _('blue')),
 ('#00ff5a51', _('red')),
 ('#00ffe875', _('yellow')),
 ('#0038FF48', _('green'))])
EMbaseInfoBarPlugins__init__ = None
EMStartOnlyOneTime = False
EMsession = None
InfoBar_instance = None
currversion = '1.0'
plugin_path = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/')
T_INDEX = 0
T_FRAME_POS = 1
T_PAGE = 2
T_NAME = 3
T_FULL = 4
HDSkn = False
sz_w = getDesktop(0).size().width()
if sz_w > 800:
    HDSkn = True
else:
    HDSkn = False

def f2(seq):
    checked = []
    for e in seq:
        if e not in checked:
            checked.append(e)

    return checked


class showPurePrestigescreen(Screen):

    def __init__(self, session):
        self.folder = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/panelbuttons/')
        self.fillplgfolders()
        piclist = self.fullpath
        path = self.folder
        lastindex = 0
        self.session = session
        self.textcolor = config.PPrestige.textcolor.value
        self.color = config.PPrestige.bgcolor.value
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
            skincontent += '<widget source="label' + str(x) + '" render="Label" position="' + str(absX - 25) + ',' + str(absY + self.picY - textsize + 5) + '" size="' + str(self.picX + 15) + ',' + str(textsize) + '" font="Regular;20" zPosition="2" transparent="1" noWrap="1" halign="' + 'center' + '"  valign="' + 'center' + '"  foregroundColor="' + self.textcolor + '" />'
            skincontent += '<widget name="thumb' + str(x) + '" position="' + str(absX + 5) + ',' + str(absY + 5) + '" size="' + str(self.picX - 30) + ',' + str(self.picY - 20) + '" zPosition="2" transparent="1" alphatest="on" />'

        if dwidth == 1280:
            self.skin = '<screen position="center,77" title="Pure Prestige ' + str(currversion) + '"  size="' + str(size_w) + ',' + str(size_h) + '" > \t\t\t<eLabel position="0,0" zPosition="0" size="' + str(size_w) + ',' + str(size_h) + '" backgroundColor="' + self.color + '" /><widget name="frame" position="20,20" size="145,145" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/pic_frame.png" zPosition="1" alphatest="on" />' + skincontent + '</screen>'
        else:
            self.skin = '<screen position="20,center" flags="wfNoBorder" title="Pure Prestige ' + str(currversion) + '"  size="' + str(size_w) + ',' + str(size_h) + '" > \t\t\t<eLabel position="0,0" zPosition="0" size="' + str(size_w) + ',' + str(size_h) + '" backgroundColor="' + self.color + '" /><widget name="frame" position="20,20" size="145,145" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/pic_frame.png" zPosition="1" alphatest="on" />' + skincontent + '</screen>'
        Screen.__init__(self, session)
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

        self['label0'].setText('Download')
        self['label1'].setText('UnInstaller')
        self['label2'].setText('Tools')
        self['label3'].setText('Applications')
        self['label4'].setText('File Explorer')
        self['label5'].setText('Device Manager')
        self['label6'].setText('RSS Reader')
        self['label7'].setText('Information')
        self['label8'].setText('About')
        self.showPic()

    def showPic(self, picInfo = ''):
        self['thumb' + str(self.Thumbnaillist[0][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/panelbuttons/download.png'))
        self['thumb' + str(self.Thumbnaillist[0][1])].show()
        self['thumb' + str(self.Thumbnaillist[1][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/panelbuttons/uninstaller.png'))
        self['thumb' + str(self.Thumbnaillist[1][1])].show()
        self['thumb' + str(self.Thumbnaillist[2][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/panelbuttons/tools.png'))
        self['thumb' + str(self.Thumbnaillist[2][1])].show()
        self['thumb' + str(self.Thumbnaillist[3][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/panelbuttons/applications.png'))
        self['thumb' + str(self.Thumbnaillist[3][1])].show()
        self['thumb' + str(self.Thumbnaillist[4][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/panelbuttons/filesbrowser.png'))
        self['thumb' + str(self.Thumbnaillist[4][1])].show()
        self['thumb' + str(self.Thumbnaillist[5][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/panelbuttons/device.png'))
        self['thumb' + str(self.Thumbnaillist[5][1])].show()
        self['thumb' + str(self.Thumbnaillist[6][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/panelbuttons/rss.png'))
        self['thumb' + str(self.Thumbnaillist[6][1])].show()
        self['thumb' + str(self.Thumbnaillist[7][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/panelbuttons/info.png'))
        self['thumb' + str(self.Thumbnaillist[7][1])].show()
        self['thumb' + str(self.Thumbnaillist[8][1])].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/panelbuttons/about.png'))
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
        if self.index == 1:
            self.session.open(Stools.MenuUninstaller.PurePrestigeMenuscrn)
        elif self.index == 0:
            try:
                self.openuserxml()
                self.session.open(PurePrestigeAddOnsManager.plugin.PurePrestigeServersScreen, self.serversnames, self.serversurls)
            except:
                pass

        elif self.index == 2:
            self.session.open(showPurePrestigetoolsscreen)
        elif self.index == 3:
            self.session.open(showPurePrestigeappscreen)
        elif self.index == 4:
            try:
                from Plugins.Extensions.DreamExplorer.plugin import *
                main(self.session)
                return
            except:
                return
        elif self.index == 5:
            try:
                from Plugins.SystemPlugins.PEPanel.HddSetup import HddSetup
                self.session.open(HddSetup)
                return
            except:
                return

        elif self.index == 6:
            self.session.open(Stools.feeds.PurePrestigeFeedScreenList)
        elif self.index == 7:
            self.session.open(showPurePrestigeinfoscreenstandard)
        elif self.index == 8:
            self.session.open(PurePrestigeAboutScreen)

    def callbackView(self, val = 0):
        self.index = val
        if self.old_index != self.index:
            self.paintFrame()

    def Exit(self):
        del self.picload
        self.close(self.index + self.dirlistcount)

    def restartenigma(self):
        epgpath = '/media/hdd/epg.dat'
        epgbakpath = '/media/hdd/epg.dat.bak'
        if path.exists(epgbakpath):
            remove(epgbakpath)
        if path.exists(epgpath):
            copyfile(epgpath, epgbakpath)
        self.session.open(TryQuitMainloop, 3)

    def openuserxml(self):
        self.serversnames = []
        self.serversurls = []
        try:
            self.serversnames.append('Open Vision Server')
            self.serversurls.append('https://openvision.tech/pureprestige/mips32el/pureprestige.xml')
            self.serversnames.append('DreamOEM Server')
            self.serversurls.append('http://mfaraj57.dreamoem.net/sim201-server_addons.xml')
            return
            if fileExists('/etc/ts_useraddons.xml'):
                pass
            else:
                return
            myfile = file('/etc/ts_useraddons.xml')
            xmlparse = minidom.parse(myfile)
            self.xmlparse = xmlparse
            print 'mahm'
            if xmlparse:
                for servers in self.xmlparse.getElementsByTagName('servers'):
                    for server in servers.getElementsByTagName('server'):
                        serverxmlurl = str(server.getElementsByTagName('url')[0].childNodes[0].data)
                        servername = str(server.getAttribute('name').encode('utf8'))
                        self.serversnames.append(servername)
                        self.serversurls.append(serverxmlurl)

                print servername
                print serverxmlurl
                self.serversnames = f2(self.serversnames)
                self.serversurls = f2(self.serversurls)
                return
        except:
            return


class checkupdateScreen(Screen):
    skin = '\n\n       \t<screen name="checkupdateScreen" position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\n\t\t<widget name="text" position="15,15" size="610,440" font="Regular;22" transparent="1" zPosition="2" />\n\n                \n\t        <ePixmap name="red"  position="195,450" zPosition="2" size="150,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/red.png" transparent="1" alphatest="on" />\n\t        <ePixmap name="yellow" position="321,450" zPosition="2" size="150,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" transparent="1" alphatest="on" /> \n        \t\n\n        \t\n        \t<widget name="key_red" position="182,457" size="150,45" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> \n                <widget name="key_yellow" position="312,457" size="150,45" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />\n        \n                </screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        info = ''
        self['key_red'] = Button(_('Exit'))
        self['key_yellow'] = Button(_('update'))
        self['text'] = Label(info)
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions', 'ColorActions'], {'ok': self.close,
         'cancel': self.close,
         'red': self.close,
         'yellow': self.runupdate}, -1)
        try:
            fp = urllib.urlopen('https://openvision.tech/pureprestige/mips32el/update.txt')
            count = 0
            self.labeltext = ''
            s1 = fp.readline()
            s2 = fp.readline()
            s3 = fp.readline()
            s1 = s1.strip()
            s2 = s2.strip()
            s3 = s3.strip()
            self.link = s2
            self.version = s1
            self.info = s3
            fp.close()
            cstr = s1 + ' ' + s2
            if s1 == currversion:
                self['text'].setText('Pure Prestige version: ' + currversion + '\n\n No updates available')
                self.update = False
            else:
                updatestr = 'Pure Prestige version: ' + currversion + '\n\nNew update ' + s1 + ' is available  \n updates:' + self.info + '\n\n press yellow button to start updating'
                self.update = True
                self['text'].setText(updatestr)
        except:
            self.update = False
            self['text'].setText('unable to check for updates-No internet connection or server down-please check later')

    def showsetup(self):
        self.session.open(ShowPurePrestigeSetup)

    def showabout(self):
        self.session.open(PurePrestigeAboutScreen)

    def runupdate(self):
        if self.update == False:
            return
        com = self.link
        dom = 'Updating plugin to ' + self.version
        instr = 'Please wait while ipkg is being downloaded...\n restart enigma is required after successful installation'
        endstr = 'Press OK to exit'
        self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.finishupdate, False, instr, endstr)

    def restartenigma(self, result):
        if result:
            epgpath = '/media/hdd/epg.dat'
            epgbakpath = '/media/hdd/epg.dat.bak'
            if path.exists(epgbakpath):
                remove(epgbakpath)
            if path.exists(epgpath):
                copyfile(epgpath, epgbakpath)
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close(True)

    def finishupdate(self):
        pass


class ShowPurePrestigeSetup(Screen, ConfigListScreen):
    skin = '\n       \t<screen name="ShowPurePrestigeSetup" position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\n\t\t\n\t        <ePixmap name="red"  position="195,450" zPosition="2" size="150,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/red.png" transparent="1" alphatest="on" />\n\t        <ePixmap name="green" position="321,450" zPosition="2" size="150,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" /> \n        \t\n\n        \t\n        \t<widget name="key_red" position="182,457" size="150,45" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> \n                <widget name="key_green" position="312,457" size="150,45" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />\n        \t\t\t\n                        <widget name="config" position="15,50" size="610,320" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t        <widget name="info" position="0,370" zPosition="4" size="400,30" font="Regular;20" foregroundColor="yellow" transparent="1" halign="left" valign="center" />\n                </screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['key_red'] = Button(_('Cancel'))
        self['key_green'] = Button(_('Save'))
        self['info'] = Label('')
        self.list = []
        self.onitem = config.plugins.showPurePrestige.scut.value
        self.mitem = config.plugins.PPrestige.items.value
        self.scut = config.plugins.PPrestige.scut.value
        self.list.append(getConfigListEntry(_('Pure Prestige shortcut button:'), config.plugins.showPurePrestige.scut))
        self.list.append(getConfigListEntry(_('ScreenShot:'), config.plugins.PPrestige.items))
        self.list.append(getConfigListEntry(_('ScreenShots Storing Folder:'), config.plugins.PPrestige.storedir))
        self.list.append(getConfigListEntry(_('Screenshot shortcut button:'), config.plugins.PPrestige.scut))
        ConfigListScreen.__init__(self, self.list, session)
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {'green': self.keySave,
         'cancel': self.keyClose,
         'ok': self.keySave}, -2)

    def showfiles(self):
        self.session.open(FilesScreen)

    def keySave(self):
        for x in self['config'].list:
            x[1].save()

        configfile.save()
        if not self.onitem == config.plugins.showPurePrestige.scut.value or not self.mitem == config.plugins.PPrestige.items.value or not self.scut == config.plugins.PPrestige.scut.value:
            self.session.openWithCallback(self.restartenigma, MessageBox, _('Restart enigma2 to load new settings?'), MessageBox.TYPE_YESNO)
        else:
            self.close(True)

    def keyClose(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close(False)

    def restartenigma(self, result):
        if result:
            epgpath = '/media/hdd/epg.dat'
            epgbakpath = '/media/hdd/epg.dat.bak'
            if path.exists(epgbakpath):
                remove(epgbakpath)
            if path.exists(epgpath):
                copyfile(epgpath, epgbakpath)
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close(True)


class PurePrestigebootlogo(Screen):
    global HD_Res
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    HD_Res = False
    if HD_Res == True:
        skin = '\n        \t\n                <screen name="PurePrestigebootlogo" position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="920,600" transparent="1"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/teamhd.png" position="15,15" size="890,570"/>\t\n                \n                 </screen>'
    else:
        skin = '\n      \t<screen name="PurePrestigebootlogo" position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\n                \n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/team.png" position="45,50" size="550,420"/>\t\n \n\t\n                </screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['SetupActions'], {'ok': self.disappear,
         'cancel': self.disappear}, -1)
        self.timer = eTimer()
        self.timer.callback.append(self.disappear)
        self.timer.start(2000, True)

    def disappear(self):
        if OVLock() == False:
            self.close()
            return
        self.session.openWithCallback(self.close, showPurePrestigescreen)

def OVLock():
    try:
        from ov import gettitle
        ovtitle = gettitle()
        return ovtitle
    except:
        return False

class PurePrestigeAboutScreen(Screen):
    global HD_Res
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    HD_Res = False
    if HD_Res == True:
        skin = '\n        \t\n                <screen name="PurePrestigeAboutScreen" position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frame.png" position="0,0" size="920,600" transparent="1"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/teamhd.png" position="15,15" size="890,570"/>\t\n                \n                 </screen>'
    else:
        skin = '\n      \t<screen name="PurePrestigeAboutScreen" position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\n                \n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/team.png" position="45,50" size="550,420"/>\t\n \n\t\n                </screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['SetupActions'], {'ok': self.close,
         'cancel': self.close}, -1)


def main(session, **kwargs):
    path = plugin_path + 'ts_useraddons.xml'
    userPath = '/etc/ts_useraddons.xml'
    try:
        if fileExists(userPath):
            path = userPath
        else:
            copyfile(path, userPath)
    except:
        pass

    session.open(PurePrestigebootlogo)


def menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('Pure Prestige'),
          main,
          'PurePrestige_mainmenu',
          44)]
    return []


def Plugins(**kwargs):
    list = []
    list.append(PluginDescriptor(icon='PurePrestige.png', name='Pure Prestige', description='Pure Prestige Panel', where=PluginDescriptor.WHERE_MENU, fnc=menu))
    list.append(PluginDescriptor(icon='PurePrestige.png', name='Pure Prestige', description='Pure Prestige Panel', where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main))
    list.append(PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=PurePrestigeAutostart))
    return list


class DreamCCAuto():

    def __init__(self):
        self.readCurrent()

    def readCurrent(self):
        current = None
        try:
            clist = open('/etc/clist.list', 'r')
        except:
            return

        if clist is not None:
            for line in clist:
                current = line

            clist.close()
        scriptliste = []
        path = '/usr/script/cam/'
        for root, dirs, files in os.walk(path):
            for name in files:
                scriptliste.append(name)

        for lines in scriptliste:
            dat = path + lines
            datei = open(dat, 'r')
            for line in datei:
                if line[0:3] == 'OSD':
                    nam = line[5:len(line) - 2]
                    if current == nam:
                        if fileExists('/etc/init.d/dccamd'):
                            Console().ePopen('mv /etc/init.d/dccamd /etc/init.d/dccamdOrig &')
                        Console().ePopen('ln -sf /usr/bin /var/bin')
                        Console().ePopen('ln -sf /usr/keys /var/keys')
                        Console().ePopen('ln -sf /usr/scce /var/scce')
                        Console().ePopen('ln -sf /usr/script /var/script')
                        Console().ePopen('sleep 2')
                        Console().ePopen('%s cam_startup &' % dat)

            datei.close()

        return


def autostartsoftcam(reason, session = None, **kwargs):
    """called with reason=1 to during shutdown, with reason=0 at startup?"""
    global DreamCC_auto
    print '[Softcam] Started'
    print 'restarting enigma dreambox '
    if reason == 0:
        try:
            if fileExists('/etc/init.d/dccamd'):
                Console().ePopen('mv /etc/init.d/dccamd /etc/init.d/dccamdOrig &')
            DreamCC_auto = DreamCCAuto()
        except:
            pass


def InfoBarPlugins__init__(self):
    global EMStartOnlyOneTime
    global InfoBar_instance
    if not EMStartOnlyOneTime:
        EMStartOnlyOneTime = True
        InfoBar_instance = self
        self['PurePrestigeActions'] = ActionMap(['PurePrestigeActions'], {'PurePrestige': self.green}, -1)
    else:
        InfoBarPlugins.__init__ = InfoBarPlugins.__init__
        InfoBarPlugins.green = None
    EMbaseInfoBarPlugins__init__(self)
    return


def showPurePrestige(self):
    path = plugin_path + 'ts_useraddons.xml'
    userPath = '/etc/ts_useraddons.xml'
    try:
        if fileExists(userPath):
            path = userPath
        else:
            copyfile(path, userPath)
    except:
        pass

    self.session.open(PurePrestigebootlogo)


def PurePrestigeAutostart(reason, **kwargs):
    epgpath = '/media/hdd/epg.dat'
    epgbakpath = '/media/hdd/epg.dat.bak'
    if path.exists(epgbakpath):
        copyfile(epgbakpath, epgpath)
        remove(epgbakpath)
    if reason == 0:
        try:
            if config.plugins.PPrestige.items.value == 'Disabled':
                pass
            else:
                print 'sessionstart'
                pScreenGrabber.gotSession(kwargs['session'])
        except:
            pass


class classScreenGrabber():

    def __init__(self):
        self.dialog = None
        return

    def gotSession(self, session):
        global globalActionMap
        try:
            rcbutton = config.plugins.PPrestige.scut.value
        except:
            rcbutton = 'text'

        ScreenGrabber_keymap = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Stools/Moretools/ScreenGrabber/keymaps/' + rcbutton + '_keymap.xml')
        self.session = session
        readKeymap(ScreenGrabber_keymap)
        globalActionMap.actions['ShowScreenGrabber'] = self.ShowHide

    def ShowHide(self):
        self.session.open(Stools.Moretools.ScreenGrabber.ScreenGrabber.PurePrestigeScreenGrabberView)


pScreenGrabber = classScreenGrabber()
