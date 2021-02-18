#!/usr/bin/python
# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Components.Console import Console as eConsole
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.config import ConfigSubsection, ConfigText, ConfigLocations, getConfigListEntry, configfile
from Components.config import config
from Components.ScrollLabel import ScrollLabel
from enigma import getDesktop, eTimer
from Tools.Directories import *
from time import gmtime, strftime, localtime, time
from datetime import date
from time import time
from os import path, stat, rename, remove, makedirs
from os import environ
import os
import gettext
import Consolef
import Consoleall
from Screens.Standby import TryQuitMainloop
from Components.Label import Label
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

plugin_path = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Stools/')

def localeInit():
    lang = language.getLanguage()
    environ['LANGUAGE'] = lang[:2]
    gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
    gettext.textdomain('enigma2')
    gettext.bindtextdomain('PPFlashBackup', '%s%s' % (resolveFilename(SCOPE_PLUGINS), plugin_path + 'PPFlashBackup/locale/'))


def _(txt):
    t = gettext.dgettext('PPFlashBackup', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)

def getBackupPath():
    backuppath = config.plugins.PPFlashBackup.backuplocation.value
    if backuppath.endswith('/'):
        return backuppath + 'backup'
    else:
        return backuppath + '/backup'


class makePurePrestigeFlashBackupTelnet(Screen):
    try:
        sz_w = getDesktop(0).size().width()
    except:
        sz_w = 720

    if sz_w == 1280:
        skin = '\n        <screen name="makePurePrestigeFlashBackupTelnet" position="center,center" size="1280,720" title="Backup is running" flags="wfNoBorder">\n        <widget name="text" position="80,80" size="1020,560" zPosition="10" font="Console;22" />\n        </screen>'
    elif sz_w == 1024:
        skin = '\n        <screen name="makePurePrestigeFlashBackupTelnet" position="center,center" size="1024,576" title="Backup is running">\n        <widget name="text" position="80,80" size="550,400" font="Console;14" />\n        </screen>'
    else:
        skin = '\n        <screen position="135,144" size="350,310" title="Backup is running" >\n        <widget name="text" position="0,0" size="550,400" font="Console;14" />\n        </screen>'

    def __init__(self, session, runBackup=False, sim2=1, console=True):
        Screen.__init__(self, session)
        self.session = session
        self.startTime = None
        self.sim2 = sim2
        self.console = console
        self.runBackup = runBackup
        self['text'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.cancel,
         'back': self.cancel,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown}, -1)
        self.finished_createFolder = None
        self.backuppath = getBackupPath()
        self.onLayoutFinish.append(self.layoutFinished)
        if self.runBackup:
            self.onShown.append(self.doBackup)
        return

    def layoutFinished(self):
        self.setWindowTitle()

    def setWindowTitle(self):
        self.setTitle(_('Backup  is running...'))

    def doBackup(self):
        if self.sim2 == 1:
            self.flaschCom = 'sh -x ' + plugin_path + 'PPFlashBackup/bin/build-nfi-image_sim2_pli.sh'
        else:
            self.flaschCom = 'sh -x ' + plugin_path + 'PPFlashBackup/bin/build-nfi-image_dmm_pli.sh'
        try:
            jff = plugin_path + 'PPFlashBackup/bin/mkfs.jffs2'
            bimage = plugin_path + 'PPFlashBackup/bin/buildimage'
            script = plugin_path + 'PPFlashBackup/bin/build-nfi-image_dmm.sh'
            os.chmod(script, 755)
            os.chmod(bimage, 755)
            os.chmod(jff, 755)
        except:
            pass

        self.flaschCom += ' ' + config.plugins.PPFlashBackup.backuplocation.value
        if config.plugins.PPFlashBackup.swap.value == 'auto':
            self.flaschCom += ' ' + config.plugins.PPFlashBackup.swapsize.value
        else:
            self.flaschCom += ' ' + config.plugins.PPFlashBackup.swap.value
        self.flaschCom += ' ' + config.plugins.PPFlashBackup.backuplocation.value
        self.flaschCom += ' ' + config.plugins.PPFlashBackup.log.value
        self.prompt(self.flaschCom)

    def prompt(self, com):
        configfile.save()
        self.startTime = time()
        try:
            if path.exists(self.backuppath) == False:
                makedirs(self.backuppath)
            instr = 'openpli-based image\nbased on script works by cokesux and bassie '
            if self.finished_createFolder:
                self.session.openWithCallback(self.finished_createFolder, Console, title=_('Backup  is running...'), cmdlist=['%s' % com], finishedCallback=self.backupFinished, closeOnSuccess=False)
            elif self.console == False:
                self.session.open(Consolef.Consolef, title=_('Backup  is running...'), cmdlist=['%s' % com], finishedCallback=self.backupFinished, closeOnSuccess=True)
            else:
                self.session.open(Consoleall.Consoleall, title=_('Backup  is running...'), cmdlist=['%s' % com], finishedCallback=self.backupFinished, closeOnSuccess=False)
        except OSError:
            if self.finished_createFolder:
                self.session.openWithCallback(self.finished_createFolder, MessageBox, _('Sorry your backup destination is not writeable.\nPlease choose an other one.'), MessageBox.TYPE_ERROR, timeout=10)
            else:
                self.session.openWithCallback(self.backupError, MessageBox, _('Sorry your backup destination is not writeable.\nPlease choose an other one.'), MessageBox.TYPE_ERROR, timeout=10)

    def exit(self, result):
        self.close()

    def backupFinished2(self, result):
        try:
            seconds = int(time() - self.startTime)
            minutes = 0
            backuplocation = config.plugins.PPFlashBackup.backuplocation.value + 'backup'
            while seconds > 60:
                seconds -= 60
                minutes += 1

            if minutes > 1:
                self.session.open(MessageBox, '\n%s%s:%d' % (_('TS FlashBackup successfully created in' + backuplocation + '.\nFlashBackup log created in /tmp/ as file FlashBackupLog.\nBackupduration (in minutes): '), minutes, seconds), MessageBox.TYPE_INFO)
                self.close()
            else:
                self.session.open(MessageBox, _('TS FlashBackup failed.\nFlashBackup Log created in /tmp/ as file FlashBackupLog.'), MessageBox.TYPE_ERROR)
                self.close()
        except:
            self.close()

    def backupFinished(self):
        seconds = int(time() - self.startTime)
        minutes = 0
        backuplocation = config.plugins.PPFlashBackup.backuplocation.value + 'backup'
        while seconds > 60:
            seconds -= 60
            minutes += 1

        if minutes > 1:
            self.session.open(MessageBox, '\n%s%s:%d' % (_('TS FlashBackup successfully created in' + backuplocation + '.\nFlashBackup log created in /tmp/ as file FlashBackupLog.\nBackupduration (in minutes): '), minutes, seconds), MessageBox.TYPE_INFO)
            self.close()
        else:
            self.session.open(MessageBox, _('TS FlashBackup failed.\nFlashBackup Log created in /tmp/ as file FlashBackupLog.'), MessageBox.TYPE_ERROR)
            self.close()

    def cancel(self):
        self.close()


class backuprunning(Screen):
    skin = '\n        \t\n                <screen  position="20,20" size="200,100" title=""  flags="wfNoBorder" >\n  \n\n                <widget name="info" position="20,20" zPosition="4" size="180,80" font="Regular;20" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n                </screen>'

    def __init__(self, session, com=None, starttime=None):
        self.skin = backuprunning.skin
        Screen.__init__(self, session)
        self.startTime = starttime
        self.com = com
        self['info'] = Label(_('Backup is running,please wait...'))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.close,
         'cancel': self.exit}, -2)
        self.onLayoutFinish.append(self.settitle)
        self.count = 1
        self.timer = eTimer()
        self.timer.callback.append(self.startbackup)
        self.timer.start(100, 1)

    def settitle(self):
        pass

    def exit(self, result):
        self.close(False)

    def startbackup(self):
        if self.count > 1:
            self.close(False)
            return
        self.count = self.count + 1
        cmd = self.com
        pipe = os.popen('{ ' + cmd + '; } 2>&1', 'r')
        text = pipe.read()
        sts = pipe.close()
        self.backupFinished()

    def restartenigma(self, result):
        epgpath = '/media/hdd/epg.dat'
        epgbakpath = '/media/hdd/epg.dat.bak'
        if os.path.exists(epgbakpath):
            os.remove(epgbakpath)
        if os.path.exists(epgpath):
            copyfile(epgpath, epgbakpath)
        self.session.open(TryQuitMainloop, 3)

    def backupFinished(self):
        seconds = int(time() - self.startTime)
        minutes = 0
        backuplocation = config.plugins.PPFlashBackup.backuplocation.value + 'backup'
        while seconds > 60:
            seconds -= 60
            minutes += 1

        if minutes > 1:
            self.session.openWithCallback(self.restartenigma, MessageBox, '\n%s%s:%d' % (_('TS FlashBackup successfully created in' + backuplocation + '.\nFlashBackup log created in /tmp/ as file FlashBackupLog.\nBackupduration (in minutes):\nenigama restarting now '), minutes, seconds), MessageBox.TYPE_INFO)
        else:
            self.session.openWithCallback(self.exit, MessageBox, _('TS FlashBackup failed.\nFlashBackup Log created in /tmp/ as file FlashBackupLog.'), MessageBox.TYPE_ERROR)
