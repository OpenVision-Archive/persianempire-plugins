#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from Screens.Console import Console
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.Harddisk import harddiskmanager
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigText, ConfigLocations, ConfigYesNo, ConfigSelection, configfile
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.PluginComponent import plugins
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Components.FileList import MultiFileSelectList
from Tools.Directories import pathExists, fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_PLUGIN, SCOPE_CURRENT_SKIN, SCOPE_METADIR
from Tools.LoadPixmap import LoadPixmap
from enigma import eTimer, quitMainloop, RT_HALIGN_LEFT, RT_VALIGN_CENTER, eListboxPythonMultiContent, eListbox, gFont, getDesktop, ePicLoad, eRCInput, getPrevAsciiCode
from os import path, unlink, stat, mkdir, popen, makedirs, listdir, access, rename, remove, W_OK, R_OK, F_OK
from time import time, gmtime, strftime, localtime
from datetime import date

config.plugins.configurationbackup = ConfigSubsection()
config.plugins.configurationbackup.backuplocation = ConfigText(default='/media/hdd/', visible_width=50, fixed_size=False)
config.plugins.configurationbackup.backupdirs = ConfigLocations(default=['/etc/enigma2/',
 '/etc/network/interfaces',
 '/etc/wpa_supplicant.conf',
 '/etc/wpa_supplicant.ath0.conf',
 '/etc/wpa_supplicant.wlan0.conf',
 '/etc/resolv.conf',
 '/etc/default_gw',
 '/etc/hostname'])
config.plugins.softwaremanager = ConfigSubsection()
config.plugins.softwaremanager.overwriteConfigFiles = ConfigSelection([('Y', _('Yes, always')), ('N', _('No, never')), ('ask', _('Always ask'))], 'Y')


def getBackupPath():
    backuppath = '/media/hdd'
    try:
        backuppath = config.plugins.configurationbackup.backuplocation.value
        if backuppath.endswith('/'):
            return backuppath + 'backup'
        return backuppath + '/backup'
    except:
        return backuppath + '/backup'


def getBackupFilename():
    return 'enigma2settingsbackup.tar.gz'


class PurePrestigeBackupScreen(Screen, ConfigListScreen):
    skin = '\n\t\t<screen position="135,144" size="350,310" title="Backup is running" >\n\t\t<widget name="config" position="10,10" size="330,250" transparent="1" scrollbarMode="showOnDemand" />\n\t\t</screen>'

    def __init__(self, session, runBackup=False):
        Screen.__init__(self, session)
        self.session = session
        self.runBackup = runBackup
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.close,
         'back': self.close,
         'cancel': self.close}, -1)
        self.finished_cb = None
        self.backuppath = getBackupPath()
        self.backupfile = getBackupFilename()
        self.fullbackupfilename = self.backuppath + '/' + self.backupfile
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self.onLayoutFinish.append(self.layoutFinished)
        if self.runBackup:
            self.onShown.append(self.doBackup)
        return

    def layoutFinished(self):
        self.setWindowTitle()

    def setWindowTitle(self):
        self.setTitle(_('Backup is running...'))

    def doBackup(self):
        configfile.save()
        try:
            if path.exists(self.backuppath) == False:
                makedirs(self.backuppath)
            self.backupdirs = ' '.join(config.plugins.configurationbackup.backupdirs.value)
            if path.exists(self.fullbackupfilename):
                dt = str(date.fromtimestamp(stat(self.fullbackupfilename).st_ctime))
                self.newfilename = self.backuppath + '/' + dt + '-' + self.backupfile
                if path.exists(self.newfilename):
                    remove(self.newfilename)
                rename(self.fullbackupfilename, self.newfilename)
            if self.finished_cb:
                self.session.openWithCallback(self.finished_cb, Console, title=_('Backup is running...'), cmdlist=['tar -czvf ' + self.fullbackupfilename + ' ' + self.backupdirs], finishedCallback=self.backupFinishedCB, closeOnSuccess=True)
            else:
                self.session.open(Console, title=_('Backup is running...'), cmdlist=['tar -czvf ' + self.fullbackupfilename + ' ' + self.backupdirs], finishedCallback=self.backupFinishedCB, closeOnSuccess=True)
        except OSError:
            if self.finished_cb:
                self.session.openWithCallback(self.finished_cb, MessageBox, _('Sorry your backup destination is not writeable.\nPlease choose an other one.'), MessageBox.TYPE_INFO, timeout=10)
            else:
                self.session.openWithCallback(self.backupErrorCB, MessageBox, _('Sorry your backup destination is not writeable.\nPlease choose an other one.'), MessageBox.TYPE_INFO, timeout=10)

    def backupFinishedCB(self, retval=None):
        self.close(True)

    def backupErrorCB(self, retval=None):
        self.close(False)

    def runAsync(self, finished_cb):
        self.finished_cb = finished_cb
        self.doBackup()


class PurePrestigeBackupSelection(Screen):
    skin = '\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520" transparent="1"/>\t\n                <widget name="tspace" position="0,480" zPosition="4" size="640,40" font="Regular;20" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n                <ePixmap position="15,64" size="610,5" pixmap="~/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\t\n                        <ePixmap pixmap="~/ddbuttons/red.png" position="15,15" size="140,40" alphatest="on" />\n\t\t        <ePixmap pixmap="~/ddbuttons/green.png" position="160,15" size="140,40" alphatest="on" />\n\t\t\t<ePixmap pixmap="~/ddbuttons/yellow.png" position="300,15" size="140,40" alphatest="on" />\n\t\t\t<widget source="key_red" render="Label" position="15,20" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget source="key_green" render="Label" position="160,20" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t\t<widget source="key_yellow" render="Label" position="300,20" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t\t<widget name="checkList" position="15,80" size="610,380" transparent="1" scrollbarMode="showOnDemand" zPosition="2" />\n\t                <ePixmap position="15,470" size="610,5" pixmap="~/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n        \t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Save'))
        self['key_yellow'] = StaticText()
        self['tspace'] = Label('Select files or folders for backup')
        self.selectedFiles = config.plugins.configurationbackup.backupdirs.value
        defaultDir = '/'
        inhibitDirs = ['/bin',
         '/boot',
         '/dev',
         '/autofs',
         '/lib',
         '/proc',
         '/sbin',
         '/sys',
         '/hdd',
         '/tmp',
         '/mnt',
         '/media']
        self.filelist = MultiFileSelectList(self.selectedFiles, defaultDir, inhibitDirs=inhibitDirs)
        self['checkList'] = self.filelist
        self['actions'] = ActionMap(['DirectionActions', 'OkCancelActions', 'ShortcutActions'], {'cancel': self.exit,
         'red': self.exit,
         'yellow': self.changeSelectionState,
         'green': self.saveSelection,
         'ok': self.okClicked,
         'left': self.left,
         'right': self.right,
         'down': self.down,
         'up': self.up}, -1)
        if self.selectionChanged not in self['checkList'].onSelectionChanged:
            self['checkList'].onSelectionChanged.append(self.selectionChanged)
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        idx = 0
        self['checkList'].moveToIndex(idx)
        self.setWindowTitle()
        self.selectionChanged()

    def setWindowTitle(self):
        self.setTitle(_('Select files/folders to backup'))

    def selectionChanged(self):
        current = self['checkList'].getCurrent()[0]
        if current[2] is True:
            self['key_yellow'].setText(_('Deselect'))
        else:
            self['key_yellow'].setText(_('Select'))

    def up(self):
        self['checkList'].up()

    def down(self):
        self['checkList'].down()

    def left(self):
        self['checkList'].pageUp()

    def right(self):
        self['checkList'].pageDown()

    def changeSelectionState(self):
        self['checkList'].changeSelectionState()
        self.selectedFiles = self['checkList'].getSelectedList()

    def saveSelection(self):
        self.selectedFiles = self['checkList'].getSelectedList()
        config.plugins.configurationbackup.backupdirs.value = self.selectedFiles
        config.plugins.configurationbackup.backupdirs.save()
        config.plugins.configurationbackup.save()
        config.save()
        self.close(None)
        return

    def exit(self):
        self.close(None)
        return

    def okClicked(self):
        if self.filelist.canDescent():
            self.filelist.descent()


class PurePrestigeRestoreMenu(Screen):
    skin = '\n                        <screen name="devicentery" position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                        <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\t\n\t\t\t<ePixmap pixmap="~/nbuttons/green.png" position="140,25" size="140,40" alphatest="on" />\n\t\t\t<ePixmap pixmap="~/nbuttons/yellow.png" position="280,25" size="140,40" alphatest="on" />\n\t\t\n\t\t\t<widget source="key_green" render="Label" position="140,15" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t\t<widget source="key_yellow" render="Label" position="280,15" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t\t<widget name="filelist" position="15,60" size="610,320" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        self.skin = PurePrestigeRestoreMenu.skin
        self['key_green'] = StaticText(_('Restore'))
        self['key_yellow'] = StaticText(_('Delete'))
        self.sel = []
        self.val = []
        self.entry = False
        self.exe = False
        self.path = ''
        self['actions'] = NumberActionMap(['SetupActions'], {'ok': self.KeyOk,
         'cancel': self.keyCancel}, -1)
        self['shortcuts'] = ActionMap(['ShortcutActions'], {'green': self.KeyOk,
         'yellow': self.deleteFile})
        self.flist = []
        self['filelist'] = MenuList(self.flist)
        self.fill_list()
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setWindowTitle()

    def setWindowTitle(self):
        self.setTitle(_('PurePrestige-Restore backups'))

    def fill_list(self):
        self.flist = []
        self.path = getBackupPath()
        if path.exists(self.path) == False:
            makedirs(self.path)
        for file in listdir(self.path):
            if file.endswith('.tar.gz'):
                self.flist.append(file)
                self.entry = True

        self['filelist'].l.setList(self.flist)

    def KeyOk(self):
        if self.exe == False and self.entry == True:
            self.sel = self['filelist'].getCurrent()
            if self.sel:
                self.val = self.path + '/' + self.sel
                self.session.openWithCallback(self.startRestore, MessageBox, _('Are you sure you want to restore\nfollowing backup:\n') + self.sel + _('\nSystem will restart after the restore!'))

    def keyCancel(self):
        self.close()

    def startRestore(self, ret=False):
        if ret == True:
            self.exe = True
            self.session.open(Console, title=_('Restore running'), cmdlist=['tar -xzvf ' + self.path + '/' + self.sel + ' -C /', 'killall -9 enigma2'])

    def deleteFile(self):
        if self.exe == False and self.entry == True:
            self.sel = self['filelist'].getCurrent()
            if self.sel:
                self.val = self.path + '/' + self.sel
                self.session.openWithCallback(self.startDelete, MessageBox, _('Are you sure you want to delete\nfollowing backup:\n') + self.sel)

    def startDelete(self, ret=False):
        if ret == True:
            self.exe = True
            print('removing:', self.val)
            if path.exists(self.val) == True:
                remove(self.val)
            self.exe = False
            self.fill_list()


class PurePrestigeRestoreScreen(Screen, ConfigListScreen):
    skin = '\n\t\t<screen position="135,144" size="350,310" title="Restore is running..." >\n\t\t<widget name="config" position="10,10" size="330,250" transparent="1" scrollbarMode="showOnDemand" />\n\t\t</screen>'

    def __init__(self, session, runRestore=False):
        Screen.__init__(self, session)
        self.session = session
        self.runRestore = runRestore
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.close,
         'back': self.close,
         'cancel': self.close}, -1)
        self.finished_cb = None
        self.backuppath = getBackupPath()
        self.backupfile = getBackupFilename()
        self.fullbackupfilename = self.backuppath + '/' + self.backupfile
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self.onLayoutFinish.append(self.layoutFinished)
        if self.runRestore:
            self.onShown.append(self.doRestore)
        return

    def layoutFinished(self):
        self.setWindowTitle()

    def setWindowTitle(self):
        self.setTitle(_('Restore is running...'))

    def doRestore(self):
        if path.exists('/proc/stb/vmpeg/0/dst_width'):
            restorecmdlist = ['tar -xzvf ' + self.fullbackupfilename + ' -C /',
             'echo 0 > /proc/stb/vmpeg/0/dst_height',
             'echo 0 > /proc/stb/vmpeg/0/dst_left',
             'echo 0 > /proc/stb/vmpeg/0/dst_top',
             'echo 0 > /proc/stb/vmpeg/0/dst_width',
             'killall -9 enigma2']
        else:
            restorecmdlist = ['tar -xzvf ' + self.fullbackupfilename + ' -C /', 'killall -9 enigma2']
        if self.finished_cb:
            self.session.openWithCallback(self.finished_cb, Console, title=_('Restore is running...'), cmdlist=restorecmdlist)
        else:
            self.session.open(Console, title=_('Restore is running...'), cmdlist=restorecmdlist)

    def backupFinishedCB(self, retval=None):
        self.close(True)

    def backupErrorCB(self, retval=None):
        self.close(False)

    def runAsync(self, finished_cb):
        self.finished_cb = finished_cb
        self.doRestore()


class PurePrestigeBackupSettingsScrean(Screen):
    skin = '\n                        <screen name="devicentery" position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                        <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\t\n\t\t\n                <widget name="list" position="15,30" size="610,510" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t        \n        </screen>'

    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        self.skin = PurePrestigeBackupSettingsScrean.skin
        self.list = []
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        self['list'].onSelectionChanged.append(self.selectionChanged)
        self.text = ''
        self.backupdirs = ' '.join(config.plugins.configurationbackup.backupdirs.value)
        self.list.append(_('Backup system settings'))
        self.list.append(_('Restore system settings'))
        self.list.append(_('Restore from file'))
        self.list.append(_('Choose backup location'))
        self.list.append(_('Choose backup files'))
        self['actions'] = ActionMap(['SetupActions'], {'ok': self.go,
         'cancel': self.close}, -1)
        self.onLayoutFinish.append(self.layoutFinished)
        self.backuppath = getBackupPath()
        self.backupfile = getBackupFilename()
        self.fullbackupfilename = self.backuppath + '/' + self.backupfile
        self.ListToMulticontent()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.list
        self['list'].l.setItemHeight(38)
        self['list'].l.setFont(0, gFont('Regular', 26))
        for i in range(0, len(self.events)):
            res.append(MultiContentEntryText(pos=(0, 1), size=(2, 34), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
            res.append(MultiContentEntryText(pos=(50, 1), size=(540, 34), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=self.events[i], color=16777215, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()

    def selectionChanged(self):
        try:
            currentEntry = self['list'].getSelectionIndex()
            if currentEntry == 3:
                backuplocation = 'Current location:' + config.plugins.configurationbackup.backuplocation.value
                self.setTitle(_(backuplocation))
            else:
                self.setTitle(_('PurePrestige-Settings backup&restore'))
        except:
            pass

    def layoutFinished(self):
        idx = 0
        self['list'].index = idx

    def setWindowTitle(self):
        self.setTitle(_('PurePrestige-Settings backup-restore'))

    def go(self):
        currentEntry = self['list'].getSelectionIndex()
        if currentEntry == 3:
            parts = [(r.description, r.mountpoint, self.session) for r in harddiskmanager.getMountedPartitions(onlyhotplug=False)]
            for x in parts:
                if not access(x[1], F_OK | R_OK | W_OK) or x[1] == '/':
                    parts.remove(x)

            if len(parts):
                self.session.openWithCallback(self.backuplocation_choosen, ChoiceBox, title=_('Please select medium to use as backup location'), list=parts)
        elif currentEntry == 4:
            self.session.openWithCallback(self.backupfiles_choosen, PurePrestigeBackupSelection)
        elif currentEntry == 2:
            self.session.open(PurePrestigeRestoreMenu)
        elif currentEntry == 0:
            self.session.openWithCallback(self.backupDone, PurePrestigeBackupScreen, runBackup=True)
        elif currentEntry == 1:
            if path.exists(self.fullbackupfilename):
                self.session.openWithCallback(self.startRestore, MessageBox, _('Are you sure you want to restore your Enigma2 backup?\nEnigma2 will restart after the restore'))
            else:
                self.session.open(MessageBox, _('Sorry no backups found!'), MessageBox.TYPE_INFO, timeout=10)

    def backupfiles_choosen(self, ret):
        self.backupdirs = ' '.join(config.plugins.configurationbackup.backupdirs.value)
        config.plugins.configurationbackup.backupdirs.save()
        config.plugins.configurationbackup.save()
        config.save()

    def backuplocation_choosen(self, option):
        oldpath = config.plugins.configurationbackup.backuplocation.getValue()
        if option is not None:
            config.plugins.configurationbackup.backuplocation.value = str(option[1])
        config.plugins.configurationbackup.backuplocation.save()
        config.plugins.configurationbackup.save()
        config.save()
        newpath = config.plugins.configurationbackup.backuplocation.getValue()
        if newpath != oldpath:
            self.createBackupfolders()
        self.selectionChanged()
        return

    def createBackupfolders(self):
        print('Creating backup folder if not already there...')
        self.backuppath = getBackupPath()
        try:
            if path.exists(self.backuppath) == False:
                makedirs(self.backuppath)
        except OSError:
            self.session.open(MessageBox, _('Sorry, your backup destination is not writeable.\n\nPlease choose another one.'), MessageBox.TYPE_INFO, timeout=10)

    def backupDone(self, retval=None):
        if retval is True:
            self.session.open(MessageBox, _('Backup done.'), MessageBox.TYPE_INFO, timeout=10)
        else:
            self.session.open(MessageBox, _('Backup failed.'), MessageBox.TYPE_INFO, timeout=10)

    def startRestore(self, ret=False):
        if ret == True:
            self.exe = True
            self.session.open(PurePrestigeRestoreScreen, runRestore=True)
