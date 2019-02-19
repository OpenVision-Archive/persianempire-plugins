from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Input import Input
from Components.Sources.StaticText import StaticText
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from Components.Button import Button
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.Slider import Slider
from Components.Ipkg import IpkgComponent
from Components.Harddisk import harddiskmanager
from Components.config import getConfigListEntry, ConfigSubsection, ConfigText, ConfigLocations, ConfigSelection, ConfigBoolean, ConfigYesNo
from Components.config import config
from Components.ConfigList import ConfigListScreen
from Components.Console import Console
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.SelectionList import SelectionList
from Components.PluginComponent import plugins
from Components.Language import language
from Components.AVSwitch import AVSwitch
from Tools.Directories import pathExists, fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_PLUGIN, SCOPE_CURRENT_SKIN, SCOPE_METADIR, SCOPE_MEDIA, SCOPE_LANGUAGE
from Tools.LoadPixmap import LoadPixmap
from enigma import eTimer, quitMainloop, RT_HALIGN_LEFT, RT_VALIGN_CENTER, eListboxPythonMultiContent, eListbox, gFont, getDesktop
from cPickle import dump, load
from os import path as os_path, system as os_system, unlink, stat, mkdir, popen, makedirs, listdir, access, rename, remove, W_OK, R_OK, F_OK
from time import time, gmtime, strftime, localtime
from stat import ST_MTIME
from datetime import date
from os import environ
import gettext
import os
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from BackupLocation import PurePrestigeFlashBackupBackupLocation
from BackupStartopenTelnet import makePurePrestigeFlashBackupTelnet

config.plugins.PPFlashBackup = ConfigSubsection()
config.plugins.PPFlashBackup.backuplocation = ConfigText(default='/media/hdd/', visible_width=50, fixed_size=False)
config.plugins.PPFlashBackup.log = ConfigText(default='2> /tmp/FlashBackupLog >&1')
config.plugins.PPFlashBackup.debug = ConfigText(default='debugon')
config.plugins.PPFlashBackup.swap = ConfigSelection([('auto', 'auto'),
 ('128', '128 MB'),
 ('256', '256 MB'),
 ('512', '512 MB'),
 ('0', 'off')], default='auto')
config.plugins.PPFlashBackup.swapsize = ConfigText(default='128')
config.plugins.PPFlashBackup.disclaimer = ConfigBoolean(default=True)
config.plugins.PPFlashBackup.update = ConfigYesNo(default=False)
mounted_string = 'Nothing mounted at '

def getBackupPath():
    backuppath = config.plugins.PPFlashBackup.backuplocation.value
    if backuppath.endswith('/'):
        return backuppath + 'backup'
    else:
        return backuppath + '/backup'


def localeInit():
    lang = language.getLanguage()
    environ['LANGUAGE'] = lang[:2]
    gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
    gettext.textdomain('enigma2')
    gettext.bindtextdomain('PPFlashBackup', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/PurePrestige/Stools/PPFlashBackup/locale/'))


def _(txt):
    t = gettext.dgettext('PPFlashBackup', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)

def write_cache(cache_file, cache_data):
    if not os_path.isdir(os_path.dirname(cache_file)):
        try:
            mkdir(os_path.dirname(cache_file))
        except OSError:
            print os_path.dirname(cache_file), 'is a file'

    fd = open(cache_file, 'w')
    dump(cache_data, fd, -1)
    fd.close()


def valid_cache(cache_file, cache_ttl):
    try:
        mtime = stat(cache_file)[ST_MTIME]
    except:
        return 0

    curr_time = time()
    if curr_time - mtime > cache_ttl:
        return 0
    else:
        return 1


def load_cache(cache_file):
    fd = open(cache_file)
    cache_data = load(fd)
    fd.close()
    return cache_data


class TSDreamboxtypesScreen(Screen):
    skin = '\n\t\t<screen position="center,center" size="640,520" title="PPFlashBackup-dreambox type"  >\n              \n\t\t <widget name="info" position="0,360" zPosition="4" size="640,160" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n                <widget name="list" position="15,30" size="610,320" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t        \n        </screen>'

    def __init__(self, session):
        self.skin = TSDreamboxtypesScreen.skin
        Screen.__init__(self, session)
        self.serversnames = []
        self.serversnames.append('SIM2-dreambox')
        self.serversnames.append('Dream multimedia-dreambox')
        self['info'] = Label('Select dreambox type,only reflash the backup to the selected type')
        self.list = []
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['actions'] = ActionMap(['SetupActions'], {'ok': self.okClicked,
         'cancel': self.close}, -2)
        self.ListToMulticontent()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.serversnames
        self['list'].l.setItemHeight(90)
        self['list'].l.setFont(0, gFont('Regular', 25))
        for i in range(0, len(self.events)):
            res.append(MultiContentEntryText(pos=(0, 40), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
            res.append(MultiContentEntryText(pos=(60, 40), size=(530, 120), font=0, flags=RT_HALIGN_LEFT, text=self.events[i], color=16777215, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()

    def okClicked(self):
        selectedserverurl = ''
        try:
            selection = self['list'].getCurrent()
            cindex = self['list'].getSelectionIndex()
            sim2 = 1
            if cindex == 0:
                self.session.open(PurePrestigeFlashBackup, sim2)
            elif cindex == 1:
                sim2 = 0
                self.session.open(PurePrestigeFlashBackup, sim2)
        except:
            pass


class PurePrestigeFlashBackup(Screen):
    try:
        sz_w = getDesktop(0).size().width()
    except:
        sz_w = 720

    if sz_w == 1280:
        skin = '\n        <screen name="PurePrestigeFlashBackup" position="center,center" size="1280,720" title="Pure Prestige FlashBackup" flags="wfNoBorder">\n            <widget source="Title" render="Label" position="80,80" size="350,30" zPosition="3" font="Regular;26" transparent="1"/>\n            <widget source="targettext" render="Label" position="80,470" size="360,25" font="Regular;22" transparent="1" zPosition="1" foregroundColor="#ffffff" />\n            <widget source="swaptext" render="Label" position="80,550" size="350,25" font="Regular;22" transparent="1" zPosition="1" foregroundColor="#ffffff" />\n            <widget name="target" position="80,500" size="540,22" valign="left" font="Regular;22" transparent="1" />\n            <widget name="swapsize" position="420,550" size="540,22" valign="left" font="Regular;22" transparent="1" />\n            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Stools/PPFlashBackup/images/button_red.png" position="80,600" size="15,16" alphatest="on" />\n            <widget source="key_red" render="Label" position="100,596" zPosition="1" size="140,25" font="Regular;22" halign="left" transparent="1" />\n            <widget source="session.VideoPicture" render="Pig"  position="80,120" size="380,215" zPosition="3" backgroundColor="#ff000000"/>\n            <widget source="menu" render="Listbox" position="550,120" size="610,200" zPosition="3" scrollbarMode="showNever">\n                <convert type="TemplatedMultiContent">\n                    {"template": [\n                            MultiContentEntryText(pos = (10, 10), size = (608, 30), flags = RT_HALIGN_LEFT, text = 1), # index 0 is the MenuText,\n                        ],\n                    "fonts": [gFont("Regular", 26)],\n                    "itemHeight": 50\n                    }\n            </convert>\n        </widget>\n        <widget source="menu" render="Listbox"     position="80,350" size="1070,250" zPosition="3" scrollbarMode="showNever" selectionDisabled="1" transparent="1">\n            <convert type="TemplatedMultiContent">\n                {"template": [\n                        MultiContentEntryText(pos = (0, 0), size = (1070, 250), flags = RT_HALIGN_CENTER|RT_VALIGN_TOP|RT_WRAP, text = 2), # index 0 is the MenuText,\n                    ],\n                "fonts": [gFont("Regular", 19)],\n                "itemHeight": 250\n                }\n            </convert>\n        </widget>\n        </screen>'
    else:
        skin = '        \n        <screen name="PurePrestigeFlashBackup" position="center,center" size="610,420" title="Pure Prestige FlashBackup" >\n            \n            <widget source="targettext" render="Label" position="15,350" size="540,25" font="Regular;22" transparent="1" zPosition="1" foregroundColor="#ffffff" />\n            <widget source="swaptext" render="Label" position="15,390" size="350,28" font="Regular;22" transparent="1" zPosition="1" foregroundColor="#ffffff" />\n            <widget name="target" position="15,370" size="580,50" valign="left" font="Regular;22" />\n            <widget name="swapsize" position="305,390" size="540,25" valign="left" font="Regular;22" transparent="1" />\n            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Stools/PPFlashBackup/images/button_red.png" zPosition="1" position="0,0" size="140,40" alphatest="on" />\n            <widget source="key_red" render="Label" position="0,0" zPosition="2" size="135,40" halign="center" valign="center" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-1,-1" /> \n            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/border_menu_350.png" position="5,50" zPosition="1" size="350,300" transparent="1" alphatest="on" />\n            <widget source="menu" render="Listbox" position="15,60" size="330,290" scrollbarMode="showOnDemand">\n                <convert type="TemplatedMultiContent">\n                    {"template": [\n                            MultiContentEntryText(pos = (2, 2), size = (330, 24), flags = RT_HALIGN_LEFT, text = 1), # index 0 is the MenuText,\n                        ],\n                    "fonts": [gFont("Regular", 22)],\n                    "itemHeight": 25\n                    }\n                </convert>\n            </widget>\n            <widget source="menu" render="Listbox" position="360,10" size="240,390" scrollbarMode="showNever" selectionDisabled="1">\n                <convert type="TemplatedMultiContent">\n                    {"template": [\n                            MultiContentEntryText(pos = (2, 2), size = (240, 390), flags = RT_HALIGN_CENTER|RT_VALIGN_CENTER|RT_WRAP, text = 2), # index 2 is the Description,\n                        ],\n                    "fonts": [gFont("Regular", 22)],\n                    "itemHeight": 390\n                    }\n                </convert>\n            </widget>\n        </screen>'

    def __init__(self, session, sim2 = 1):
        Screen.__init__(self, session)
        self.skin = PurePrestigeFlashBackup.skin
        self.menu = 0
        self.sim2 = sim2
        self.list = []
        self.oktext = _('\nPress OK on your remote control to continue.')
        self.text = ''
        if self.menu == 0:
            self.list.append(('backup',
             _('Start Backup'),
             _('\nStarts backup from yours Flash-Image.') + self.oktext,
             None))
            self.list.append(('console',
             _('Start Backup with console'),
             _('\nStarts backup with console from yours Flash-Image.') + self.oktext,
             None))
            self.list.append(('backuplocation',
             _('Choose backup location'),
             _('\nSelect your backup device.') + self.oktext,
             None))
            self.list.append(('settings',
             _('Settings'),
             _('\nAdjustments for Swap and Enigma 2 update.') + self.oktext,
             None))
        self['menu'] = List(self.list)
        self['key_red'] = StaticText(_('Close'))
        self['status'] = StaticText('')
        self['targettext'] = StaticText(_('Selected Backuplocation:'))
        self['target'] = Label(config.plugins.PPFlashBackup.backuplocation.value)
        self['swaptext'] = StaticText(_('Current Swapsize (0 is off): '))
        self['swapsize'] = Label(config.plugins.PPFlashBackup.swap.value + ' MB')
        self['shortcuts'] = ActionMap(['ShortcutActions', 'WizardActions', 'InfobarEPGActions'], {'ok': self.go,
         'back': self.cancel,
         'red': self.cancel}, -1)
        self.onLayoutFinish.append(self.layoutFinished)
        self.onShown.append(self.setWindowTitle)
        return

    def layoutFinished(self):
        idx = 0
        self['menu'].index = idx

    def setWindowTitle(self):
        self.setTitle(_('Pure Prestige FlashBackup'))

    def callMyMsg(self, result):
        path = config.plugins.PPFlashBackup.backuplocation.value
        if self.checkmountBackupPath(path) == False:
            return
        if result:
            if fileExists('/etc/init.d/flashexpander.sh'):
                self.session.open(MessageBox, _('FlashExpander is used,no FlashBackup possible.'), MessageBox.TYPE_INFO)
                self.cancel()
            else:
                runBackup = True
                self.session.open(makePurePrestigeFlashBackupTelnet, runBackup, self.sim2, console=False)

    def callMyMsg2(self, result):
        path = config.plugins.PPFlashBackup.backuplocation.value
        if self.checkmountBackupPath(path) == False:
            return
        if result:
            if fileExists('/etc/init.d/flashexpander.sh'):
                self.session.open(MessageBox, _('FlashExpander is used,no FlashBackup possible.'), MessageBox.TYPE_INFO)
                self.cancel()
            else:
                runBackup = True
                self.session.open(makePurePrestigeFlashBackupTelnet, runBackup, self.sim2, console=True)

    def checkmountBackupPath(self, path):
        if path is None:
            self.session.open(MessageBox, _('nothing entered'), MessageBox.TYPE_ERROR)
            return False
        else:
            sp = []
            sp = path.split('/')
            print sp
            if len(sp) > 1:
                if sp[1] != 'media':
                    self.session.open(MessageBox, mounted_string % path, MessageBox.TYPE_ERROR)
                    return False
            mounted = False
            self.swappable = False
            sp2 = []
            f = open('/proc/mounts', 'r')
            m = f.readline()
            while m and not mounted:
                if m.find('/%s/%s' % (sp[1], sp[2])) is not -1:
                    mounted = True
                    print m
                    sp2 = m.split(' ')
                    print sp2
                    if sp2[2].startswith('ext') or sp2[2].endswith('fat'):
                        print '[stFlash] swappable'
                        self.swappable = True
                m = f.readline()

            f.close()
            if not mounted:
                self.session.open(MessageBox, mounted_string + str(path), MessageBox.TYPE_ERROR)
                return False
            if os.path.exists(config.plugins.PPFlashBackup.backuplocation.value):
                try:
                    os.chmod(config.plugins.PPFlashBackup.backuplocation.value, 511)
                except:
                    pass

            return True
            return

    def go(self):
        current = self['menu'].getCurrent()
        if current:
            currentEntry = current[0]
        if self.menu == 0:
            if currentEntry == 'settings':
                self.session.openWithCallback(self.updateSwap, PurePrestigeFlashBackupSetting)
            if currentEntry == 'backup':
                if self.sim2 == 1:
                    self.session.openWithCallback(self.callMyMsg, MessageBox, _('You selected to backup flash image for sim2 dreambox,continue?'), MessageBox.TYPE_YESNO)
                else:
                    self.session.openWithCallback(self.callMyMsg, MessageBox, _('You selected to backup flash image for original dream multimedia dreambox,continue?'), MessageBox.TYPE_YESNO)
            if currentEntry == 'console':
                if self.sim2 == 1:
                    self.session.openWithCallback(self.callMyMsg2, MessageBox, _('You selected to backup flash image for sim2 dreambox,continue?'), MessageBox.TYPE_YESNO)
                else:
                    self.session.openWithCallback(self.callMyMsg2, MessageBox, _('You selected to backup flash image for original dream multimedia dreambox,continue?'), MessageBox.TYPE_YESNO)
            elif currentEntry == 'backuplocation':
                self.session.openWithCallback(self.backuplocation_choosen, PurePrestigeFlashBackupBackupLocation)

    def updateSwap(self, retval):
        self['swapsize'].setText(''.join(config.plugins.PPFlashBackup.swap.value + ' MB'))

    def backuplocation_choosen(self, option):
        self.updateTarget()
        if option is not None:
            config.plugins.PPFlashBackup.backuplocation.value = str(option[1])
        config.plugins.PPFlashBackup.backuplocation.save()
        config.plugins.PPFlashBackup.save()
        config.save()
        self.createBackupfolders()
        return

    def createBackupfolders(self):
        self.backuppath = getBackupPath()
        try:
            if os_path.exists(self.backuppath) == False:
                makedirs(self.backuppath)
        except OSError:
            self.session.openWithCallback(self.goagaintobackuplocation, MessageBox, _('Sorry, your backup destination is not writeable.\n\nPlease choose another one.'), MessageBox.TYPE_ERROR)

    def goagaintobackuplocation(self, retval):
        self.session.openWithCallback(self.backuplocation_choosen, PurePrestigeFlashBackupBackupLocation)

    def updateTarget(self):
        self['target'].setText(''.join(config.plugins.PPFlashBackup.backuplocation.value))

    def backupDone(self, retval = None):
        if retval is False:
            self.session.open(MessageBox, _('Pure Prestige FlashBackup failed.'), MessageBox.TYPE_ERROR, timeout=10)
        elif config.plugins.PPFlashBackup.update.value == True:
            self.session.open(PurePrestigeFlashBackupUpdateCheck)
        else:
            self.cancel()

    def cancel(self):
        self.close(None)
        return

    def runUpgrade(self, result):
        if result:
            self.session.open(PurePrestigeFlashBackupUpdateCheck)


class PurePrestigeFlashBackupUpdateCheck(Screen):
    try:
        sz_w = getDesktop(0).size().width()
    except:
        sz_w = 720

    if sz_w == 1280:
        skin = '\n        <screen name="PPFlashBackupUpdateCheck" position="center,center" size="1280,720" title="Software update">\n        <widget source="Title" render="Label" position="80,80" size="450,30" zPosition="3" font="Regular;22" transparent="1"/>\n        <widget source="session.VideoPicture" render="Pig"  position="80,120" size="380,215" zPosition="3" backgroundColor="#ff000000"/>\n        <widget source="package" render="Label" position="550,130" size="660,28" font="Regular;24" backgroundColor="#25062748" transparent="1"/>\n        <widget source="status" render="Label" position="550,170" size="660,56" font="Regular;24" backgroundColor="#25062748" transparent="1"/>\n        <widget name="slider" position="550,290" size="660,20" borderWidth="1" transparent="1"/>\n        <widget name="activityslider" position="43,670" size="1194,6" transparent="1"/>\n        </screen>'
    elif sz_w == 1024:
        skin = '\n        <screen name="PPFlashBackupUpdateCheck" position="center,center" size="1024,576" title="Software update">\n        <widget name="activityslider" position="0,0" size="550,5"/>\n        <widget name="slider" position="0,150" size="550,30"/>\n        <widget source="package" render="Label" position="10,30" size="540,20" font="Regular;18" halign="center" valign="center" backgroundColor="#25062748" transparent="1"/>\n        <widget source="status" render="Label" position="10,60" size="540,45" font="Regular;20" halign="center" valign="center" backgroundColor="#25062748" transparent="1"/>\n        </screen>'
    else:
        skin = '\n        <screen name="PPFlashBackupUpdateCheck" position="center,center" size="550,300" title="Software update" >\n        <widget name="activityslider" position="0,0" size="550,5"/>\n        <widget name="slider" position="0,150" size="550,30"/>\n        <widget source="package" render="Label" position="10,30" size="540,20" font="Regular;18" halign="center" valign="center" backgroundColor="#25062748" transparent="1"/>\n        <widget source="status" render="Label" position="10,60" size="540,45" font="Regular;20" halign="center" valign="center" backgroundColor="#25062748" transparent="1"/>\n        </screen>'

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self.sliderPackages = {'dreambox-dvb-modules': 1,
         'enigma2': 2,
         'tuxbox-image-info': 3}
        self.slider = Slider(0, 4)
        self['slider'] = self.slider
        self.activityslider = Slider(0, 100)
        self['activityslider'] = self.activityslider
        self.status = StaticText(_('Upgrading Dreambox... Please wait'))
        self['status'] = self.status
        self.package = StaticText()
        self['package'] = self.package
        self.oktext = _('Press OK on your remote control to continue.')
        self.packages = 0
        self.error = 0
        self.processed_packages = []
        self.activity = 0
        self.activityTimer = eTimer()
        self.activityTimer.callback.append(self.doActivityTimer)
        self.activityTimer.start(100, False)
        self.ipkg = IpkgComponent()
        self.ipkg.addCallback(self.ipkgCallback)
        self.updating = True
        self.package.setText(_('Package list update'))
        self.ipkg.startCmd(IpkgComponent.CMD_UPDATE)
        self['actions'] = ActionMap(['WizardActions'], {'ok': self.exit,
         'back': self.exit}, -1)

    def doActivityTimer(self):
        self.activity += 1
        if self.activity == 100:
            self.activity = 0
        self.activityslider.setValue(self.activity)

    def ipkgCallback(self, event, param):
        if event == IpkgComponent.EVENT_DOWNLOAD:
            self.status.setText(_('Downloading'))
        elif event == IpkgComponent.EVENT_UPGRADE:
            if self.sliderPackages.has_key(param):
                self.slider.setValue(self.sliderPackages[param])
            self.package.setText(param)
            self.status.setText(_('Upgrading'))
            if param not in self.processed_packages:
                self.processed_packages.append(param)
                self.packages += 1
        elif event == IpkgComponent.EVENT_INSTALL:
            self.package.setText(param)
            self.status.setText(_('Installing'))
            if param not in self.processed_packages:
                self.processed_packages.append(param)
                self.packages += 1
        elif event == IpkgComponent.EVENT_REMOVE:
            self.package.setText(param)
            self.status.setText(_('Removing'))
            if param not in self.processed_packages:
                self.processed_packages.append(param)
                self.packages += 1
        elif event == IpkgComponent.EVENT_CONFIGURING:
            self.package.setText(param)
            self.status.setText(_('Configuring'))
        elif event == IpkgComponent.EVENT_MODIFIED:
            if config.plugins.SoftwareManager.overwriteConfigFiles.value in ('N', 'Y'):
                self.ipkg.write(True and config.plugins.SoftwareManager.overwriteConfigFiles.value)
            else:
                self.session.openWithCallback(self.modificationCallback, MessageBox, _('A configuration file (%s) was modified since Installation.\nDo you want to keep your version?') % param)
        elif event == IpkgComponent.EVENT_ERROR:
            self.error += 1
        elif event == IpkgComponent.EVENT_DONE:
            if self.updating:
                self.updating = False
                self.ipkg.startCmd(IpkgComponent.CMD_UPGRADE, args={'test_only': False})
            elif self.error == 0:
                self.slider.setValue(4)
                self.activityTimer.stop()
                self.activityslider.setValue(0)
                self.package.setText('')
                self.status.setText(_('Done - Installed or upgraded %d packages') % self.packages + '\n\n' + self.oktext)
            else:
                self.activityTimer.stop()
                self.activityslider.setValue(0)
                error = _('your dreambox might be unusable now. Please consult the manual for further assistance before rebooting your dreambox.')
                if self.packages == 0:
                    error = _('No packages were upgraded yet. So you can check your network and try again.')
                if self.updating:
                    error = _("Your dreambox isn't connected to the internet properly. Please check it and try again.")
                self.status.setText(_('Error') + ' - ' + error)

    def modificationCallback(self, res):
        self.ipkg.write(res and 'N' or 'Y')

    def exit(self):
        if not self.ipkg.isRunning():
            if self.packages != 0 and self.error == 0:
                self.session.openWithCallback(self.exitAnswer, MessageBox, _('Upgrade finished.') + ' ' + _('Do you want to reboot your Dreambox?'))
            else:
                self.close()

    def exitAnswer(self, result):
        if result is not None and result:
            quitMainloop(2)
        self.close()
        return

    def cancel(self):
        self.close(None)
        return


class PurePrestigeFlashBackupSetting(Screen, ConfigListScreen):
    try:
        sz_w = getDesktop(0).size().width()
    except:
        sz_w = 720

    if sz_w == 1280:
        skin = '\n        <screen name="PPFlashBackupSetting" position="center,center" size="1280,720" title="Pure Prestige FlashBackup Settings" flags="wfNoBorder">\n            <widget source="Title" render="Label" position="80,80" size="550,30" zPosition="3" font="Regular;26" transparent="1"/>\n            <widget source="session.VideoPicture" render="Pig"  position="80,120" size="380,215" zPosition="3" backgroundColor="#ff000000"/>\n            <widget name="config" position="550,150" size="610,150" zPosition="3" scrollbarMode="showOnDemand" transparent="1" />\n            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Stools/PPFlashBackup/images/div-h.png" position="550,220" zPosition="1" size="610,4" />\n            <widget source="helptext" render="Label" position="550,250" zPosition="1" size="610,200" font="Regular;22" halign="left" transparent="1" />\n            <widget name="red" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Stools/PPFlashBackup/images/button_red.png" position="80,600" size="15,16" alphatest="on" />\n            <widget name="green" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Stools/PPFlashBackup/images/button_green.png" position="290,600" size="15,16" alphatest="on" />\n            <widget source="key_red" render="Label" position="100,596" zPosition="1" size="140,25" font="Regular;22" halign="left" transparent="1" />\n            <widget source="key_green" render="Label" position="310,596" zPosition="1" size="140,25" font="Regular;22" halign="left" transparent="1" />\n        </screen>'
    elif sz_w == 1024:
        skin = '\n        <screen name="PPFlashBackupSetting" position="center,center" size="1024,576" title="Pure Prestige FlashBackup Settings" flags="wfNoBorder">\n            <widget source="Title" render="Label" position="80,80" size="550,30" zPosition="3" font="Regular;26" transparent="1"/>\n            <widget source="session.VideoPicture" render="Pig"  position="80,120" size="380,215" zPosition="3" backgroundColor="#ff000000"/>\n            <widget name="config" position="470,150" size="474,150" zPosition="3" scrollbarMode="showOnDemand" transparent="1" />\n            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Stools/PPFlashBackup/images/div-h.png" position="470,220" zPosition="1" size="474,4" />\n            <widget source="helptext" render="Label" position="470,250" zPosition="1" size="474,200" font="Regular;20" halign="left" transparent="1" />\n            <widget name="red" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Stools/PPFlashBackup/images/button_red.png" position="80,500" size="15,16" alphatest="on" />\n            <widget name="green" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Stools/PPFlashBackup/images/button_green.png" position="290,500" size="15,16" alphatest="on" />\n            <widget source="key_red" render="Label" position="100,496" zPosition="1" size="140,25" font="Regular;22" halign="left" transparent="1" />\n            <widget source="key_green" render="Label" position="310,496" zPosition="1" size="140,25" font="Regular;22" halign="left" transparent="1" />\n        </screen>'
    else:
        skin = '         \n        <screen name="PPFlashBackupSetting" position="center,center" size="610,410" title="Pure Prestige FlashBackup Settings" >\n            <widget name="config" position="5,70" size="600,50" scrollbarMode="showOnDemand" />\n            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Stools/PPFlashBackup/images/div-h.png" position="5,130" zPosition="1" size="600,4" />\n            <widget source="helptext" render="Label" position="5,140" zPosition="1" size="600,100" font="Regular;22" halign="left" transparent="1" />\n            <widget name="red" position="0,5" zPosition="1" size="135,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Stools/PPFlashBackup/images/button_red.png" transparent="1" alphatest="on" />\n            <widget source="key_red" render="Label" position="0,5" zPosition="2" size="135,40" halign="center" valign="center" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-1,-1" />   \n            <widget name="green" position="135,5" zPosition="1" size="135,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Stools/PPFlashBackup/images/button_green.png" transparent="1" alphatest="on" />\n            <widget source="key_green" render="Label" position="135,5" zPosition="2" size="135,40" halign="center" valign="center" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n        </screen>'

    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self.list = []
        self.list.append(getConfigListEntry(_('Swapsize: '), config.plugins.PPFlashBackup.swap))
        self.list.append(getConfigListEntry(_('Check for Enigma 2 Update after Backup: '), config.plugins.PPFlashBackup.update))
        ConfigListScreen.__init__(self, self.list)
        self['green'] = Pixmap()
        self['red'] = Pixmap()
        self['key_red'] = StaticText(_('Close'))
        self['key_green'] = StaticText(_('Save'))
        self['helptext'] = StaticText(_('It is sometimes necessary to disable the Swap function if the backup is done on a network mount!\nAttention: A working Swap must be active on the box.'))
        self['shortcuts'] = ActionMap(['ShortcutActions', 'WizardActions', 'InfobarEPGActions'], {'ok': self.save,
         'back': self.cancel,
         'green': self.save,
         'red': self.cancel}, -1)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('Pure Prestige FlashBackup Settings'))

    def save(self):
        for x in self['config'].list:
            x[1].save()

        self.close(None)
        return

    def cancel(self):
        self.close(None)
        return


def main(session, **kwargs):
    session.open(TSDreamboxtypesScreen)


def startSetup(menuid):
    if menuid != 'setup':
        return []
    return [(_('PurePrestige FlashBackup'),
      main,
      'PPFlashBackup',
      50)]


def Plugins(path, **kwargs):
    global plugin_path
    plugin_path = path
    list = [PluginDescriptor(name=_('Pure Prestige FlashBackup'), description=_('Flashimage-Backup on storage device'), where=PluginDescriptor.WHERE_PLUGINMENU, icon='PPFlashBackup.png', fnc=main), PluginDescriptor(name=_('Pure Prestige FlashBackup'), description=_('Flashimage-Backup on storage device'), where=PluginDescriptor.WHERE_MENU, fnc=startSetup), PluginDescriptor(name=_('Pure Prestige FlashBackup'), description=_('Flashimage-Backup on storage device'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon='g3icon_PPFlashBackup.png', fnc=main)]
    return list
