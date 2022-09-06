# -*- coding: utf-8 -*-
from Screens.Standby import TryQuitMainloop
from Components.Label import Label
from Components.MenuList import MenuList
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.AVSwitch import AVSwitch
from Components.config import config
from Tools.Directories import fileExists, pathExists, copyfile, resolveFilename, SCOPE_PLUGINS
from ServiceReference import ServiceReference
from enigma import getDesktop, ePicLoad
from os import popen, system, path, listdir, remove
from Components.Sources.StaticText import StaticText
from random import randint
from Components.ActionMap import ActionMap
from Components.Scanner import openFile, openList
from .picplayer import grabberPic_Thumb
from mimetypes import guess_type
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import config, ConfigDirectory, ConfigSubsection, ConfigSubList, ConfigEnableDisable, ConfigNumber, ConfigText, ConfigSelection, ConfigYesNo, ConfigPassword, getConfigListEntry, configfile


class PurePrestigeFilesScreen(Screen):
    skin = '\n                        <screen name="PurePrestigeFilesScreen" position="center,center" size="640,520" title="Screenshot Files"  flags="wfNoBorder" >\n                        <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\t\n\t\n\t\t\t<ePixmap position="15,65" size="610,5" pixmap="~/images/slider.png" alphaTest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\n                          <widget name="ButtonBluetext" position="75,25" size="160,40" verticalAlignment="center" horizontalAlignment="left" zPosition="10" font="Regular;22" transparent="1" />\n\t\t\t  <widget name="ButtonBlue" pixmap="~/images/button_blue.png" position="55,35" zPosition="10" size="100,100" transparent="1" alphaTest="on" />\n                          <widget name="ButtonYellowtext" position="285,25" size="200,40" verticalAlignment="center" horizontalAlignment="left" zPosition="10" font="Regular;22" transparent="1" />\n\t\t\t  <widget name="ButtonYellow" pixmap="~/images/button_yellow.png" position="265,35" zPosition="10" size="100,100" transparent="1" alphaTest="on" />\n                          <widget name="info" position="25,415" zPosition="4" size="400,30" font="Regular;20" foregroundColor="yellow" transparent="1" horizontalAlignment="left" verticalAlignment="center" />\n                          <widget name="menu" position="30,75" size="580,425" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t                  \n        \t</screen>\n\t\t'

    def __init__(self, session):
        self.skin = PurePrestigeFilesScreen.skin
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        Screen.__init__(self, session)
        list = []
        self['menu'] = MenuList(list)
        self['ButtonBlue'] = Pixmap()
        self['ButtonBluetext'] = Label(_('Preview'))
        self['ButtonYellow'] = Pixmap()
        self['ButtonYellowtext'] = Label(_('Delete'))
        self['info'] = Label()
        if config.plugins.PPrestige.storedir.value == 'tmp':
            self.folder = '/tmp/'
        else:
            self.folder = '/media/hdd/'
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'yellow': self.removefile,
         'blue': self.onFileAction,
         'ok': self.onFileAction,
         'cancel': self.close}, -2)
        self.fillplgfolders()

    def removefile(self):
        self['info'].setText('')
        try:
            fname = self['menu'].getCurrent()
            filename = self.folder + fname
            remove(filename)
            self.fillplgfolders()
        except:
            self['info'].setText('unable to delete file')

    def onFileAction(self):
        self['info'].setText('')
        fname = self['menu'].getCurrent()
        try:
            self.session.open(grabberPic_Thumb, self.fullpath, 0, self.folder)
        except TypeError as e:
            self['info'].setText('unable to preview file')

    def fillplgfolders(self):
        self['info'].setText('')
        plgfolders = []
        fullpath = []
        for x in listdir(self.folder):
            if path.isfile(self.folder + x):
                if x.endswith('.jpg'):
                    plgfolders.append(x)
                    fullpath.append(x)

        self['menu'].setList(plgfolders)
        self.fullpath = fullpath


class PurePrestigeScreenGrabberSetup(Screen, ConfigListScreen):
    skin = '\n                        <screen name="PurePrestigeScreenGrabberSetup" position="center,center" size="640,520" title="ScreebGrabber setup"  flags="wfNoBorder" >\n                        <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\t\n\t\t \n\t\t\t<ePixmap position="15,45" size="610,5" pixmap="~/images/slider.png" alphaTest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\t<ePixmap pixmap="~/images/button_red.png" position="20,15" zPosition="0" size="140,40" transparent="1" alphaTest="on" />\n\t\t\t<ePixmap pixmap="~/images/button_green.png" position="160,15" zPosition="0" size="140,40" transparent="1" alphaTest="on" />\n\t\t\t<ePixmap pixmap="~/images/button_yellow.png" position="300,15" zPosition="0" size="140,40" transparent="1" alphaTest="on" />\n\t\t\t\n\t\t\t<widget render="Label" source="key_red" position="40,5" size="140,40" zPosition="5" verticalAlignment="center" horizontalAlignment="left" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget render="Label" source="key_green" position="180,5" size="140,40" zPosition="5" verticalAlignment="center" horizontalAlignment="left" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget render="Label" source="key_yellow" position="320,5" size="140,40" zPosition="5" verticalAlignment="center" horizontalAlignment="left" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                        <widget name="config" position="20,50" size="600,320" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t        <widget name="info" position="0,370" zPosition="4" size="580,30" font="Regular;20" foregroundColor="yellow" transparent="1" horizontalAlignment="center" verticalAlignment="center" />\n                </screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Save'))
        self['key_yellow'] = StaticText(_('Files'))
        self['info'] = Label('')
        self.list = []
        self.list.append(getConfigListEntry(_('ScreenShot:'), config.plugins.PPrestige.items))
        self.list.append(getConfigListEntry(_('Storing Folder:'), config.plugins.PPrestige.storedir))
        self.list.append(getConfigListEntry(_('Remote screenshot button:'), config.plugins.PPrestige.scut))
        self.list.append(getConfigListEntry(_('Picture size:'), config.plugins.PPrestige.newsize))
        self.list.append(getConfigListEntry(_('screenshot format/quality:'), config.plugins.PPrestige.format))
        self.list.append(getConfigListEntry(_('Fixed Aspect ratio:'), config.plugins.PPrestige.fixedaspectratio))
        self.list.append(getConfigListEntry(_('Fixed Aspect ratio 4:3:'), config.plugins.PPrestige.always43))
        self.list.append(getConfigListEntry(_('Bicubic picture resize:'), config.plugins.PPrestige.bicubic))
        self.onitem = config.plugins.PPrestige.items.value
        self.scut = config.plugins.PPrestige.scut.value
        ConfigListScreen.__init__(self, self.list, session)
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {'yellow': self.showfiles,
         'green': self.keySave,
         'cancel': self.keyClose}, -2)

    def showfiles(self):
        if self.checkfolder() == True:
            self.session.open(PurePrestigeFilesScreen)
        else:
            self.session.open(MessageBox, text=_('Storing directory is not available'), type=MessageBox.TYPE_INFO, timeout=3, close_on_any_key=True)

    def checkfolder(self):
        strfolder = str(self['config'].list[1][1].value)
        print(strfolder)
        if strfolder == 'hdd':
            strfolder = '/media/hdd'
        elif strfolder == 'tmp':
            strfolder = '/tmp'
        print(strfolder)
        if path.exists(strfolder):
            return True
        else:
            return False

    def keySave(self):
        if self.checkfolder() == True:
            for x in self['config'].list:
                x[1].save()

            configfile.save()
            if not self.onitem == config.plugins.PPrestige.items.value or not self.scut == config.plugins.PPrestige.scut.value:
                self.session.openWithCallback(self.restartenigma, MessageBox, _('Restart enigma2 to load new settings?'), MessageBox.TYPE_YESNO)
            else:
                self.close(True)
        else:
            self.session.open(MessageBox, text=_('Storing directory is not available'), type=MessageBox.TYPE_INFO, timeout=3, close_on_any_key=True)
            return

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

    def keyClose(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close(False)


class PurePrestigeScreenGrabberView(Screen):

    def __init__(self, session):
        nowService = session.nav.getCurrentlyPlayingServiceReference()
        self.nowService = nowService
        self.srvName = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
        session.nav.stopService()
        cmd = ''
        tcmd = ''
        if config.plugins.PPrestige.items.value == '-v':
            items = '-v'
        elif config.plugins.PPrestige.items.value == '-o':
            items = '-o'
        else:
            items = ''
        newsize = config.plugins.PPrestige.newsize.value.replace('Disabled', '')
        format = config.plugins.PPrestige.format.value
        fixedaspectratio = config.plugins.PPrestige.fixedaspectratio.value.replace('Disabled', '')
        always43 = config.plugins.PPrestige.always43.value.replace('Disabled', '')
        bicubic = config.plugins.PPrestige.bicubic.value.replace('Disabled', '')
        tcmd = items + ' ' + newsize + ' ' + format + ' ' + fixedaspectratio + ' ' + always43 + ' ' + bicubic
        print(tcmd)
        self.pictureformat = ''
        if format == '-p':
            self.pictureformat = '/tmp/ScreenGrabber.png'
        else:
            self.pictureformat = '/tmp/ScreenGrabber.jpg'
        r = popen('grab ' + tcmd + ' ' + self.pictureformat).readlines()
        w = getDesktop(0).size().width()
        h = getDesktop(0).size().height()
        PreviewString = '<screen backgroundColor="#00080808" flags="wfNoBorder" position="0,0" size="' + str(w) + ',' + str(h) + '" title="Preview">\n'
        PreviewString = PreviewString + ' <widget name="Picture" position="0,0" size="' + str(w) + ',' + str(h) + '" zPosition="5" alphaTest="on" />\n'
        PreviewString = PreviewString + ' <eLabel font="Regular;18" backgroundColor="#00640808" horizontalAlignment="left" verticalAlignment="center" position="10,80" size="300,25" text="Please wait....." zPosition="1"/>\n'
        PreviewString = PreviewString + ' <eLabel font="Regular;18" backgroundColor="#00080808" horizontalAlignment="left" verticalAlignment="center" position="10,50" size="620,25" text="OK=Save        Exit=Play TV        Green=Setup        Yellow=Files" zPosition="9"/>\n'
        PreviewString = PreviewString + '</screen>'
        prvScreen = PreviewString
        self.skin = prvScreen
        Screen.__init__(self, session)
        self.session = session
        self.whatPic = self.pictureformat
        self.EXscale = AVSwitch().getFramebufferScale()
        self.EXpicload = ePicLoad()
        self['Picture'] = Pixmap()
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.SavePic,
         'back': self.dexit,
         'green': self.showsetup,
         'yellow': self.showfiles}, -1)
        self.EXpicload.PictureData.get().append(self.DecodeAction)
        self.onLayoutFinish.append(self.Show_Picture)

    def showsetup(self):
        self.session.open(PurePrestigeScreenGrabberSetup)
        self.dexit()

    def showfiles(self):
        self.session.open(PurePrestigeFilesScreen)
        self.dexit()

    def dexit(self):
        self.session.nav.playService(self.nowService)
        self.close()

    def Show_Picture(self):
        if fileExists(self.whatPic):
            self.EXpicload.setPara([self['Picture'].instance.size().width(),
             self['Picture'].instance.size().height(),
             self.EXscale[0],
             self.EXscale[1],
             0,
             1,
             '#00080808'])
            self.EXpicload.startDecode(self.whatPic)

    def DecodeAction(self, pictureInfo=''):
        if fileExists(self.whatPic):
            ptr = self.EXpicload.getData()
            self['Picture'].instance.setPixmap(ptr)

    def SavePic(self):
        import datetime
        now = datetime.datetime.now()
        day = str(now.day)
        month = str(now.month)
        year = str(now.year)
        hour = str(now.hour)
        second = str(now.second)
        datestr = day + month + year + '-' + hour + second
        if fileExists(self.whatPic):
            srvName = ServiceReference(self.session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
            srvName = srvName.replace('\xc2\x86', '').replace('\xc2\x87', '')
            srvName = srvName.replace(' ', '_')
            if config.plugins.PPrestige.storedir.value == 'tmp':
                self.folder = '/tmp/'
            else:
                self.folder = '/media/hdd/'
            try:
                if pathExists(self.folder):
                    if self.pictureformat.endswith('jpg'):
                        filename = self.folder + self.srvName + '-' + datestr + '.jpg'
                    else:
                        filename = self.folder + self.srvName + '-' + datestr + '.png'
                    command = 'cp ' + self.pictureformat + ' ' + filename
                    mtext = 'saving picture to...\n' + filename
                    copyfile(self.pictureformat, filename)
                    self.session.open(MessageBox, text=_(filename), type=MessageBox.TYPE_INFO, timeout=3, close_on_any_key=True)
                else:
                    self.session.open(MessageBox, text=_('Location not available!'), type=MessageBox.TYPE_ERROR, timeout=5, close_on_any_key=True)
            except:
                self.session.open(MessageBox, text=_('Failed saving file!'), type=MessageBox.TYPE_ERROR, timeout=5, close_on_any_key=True)

        self.dexit()
