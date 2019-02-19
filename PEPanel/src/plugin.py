from Screens.About import About
from Screens.ChannelSelection import *
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.NetworkSetup import NetworkAdapterSelection, NameserverSetup
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Screens.PluginBrowser import *
from Screens.Ipkg import Ipkg
from Screens.ServiceInfo import ServiceInfo
from Screens.Screen import Screen
from Screens.Setup import SetupSummary, Setup
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import HelpableActionMap, ActionMap, NumberActionMap
from Components.Button import Button
from Components.config import config, getConfigListEntry, configfile, ConfigSelection, ConfigSubsection, ConfigText, ConfigLocations, ConfigNothing, ConfigOnOff, ConfigInteger, NoSave, ConfigYesNo, ConfigNumber, ConfigIP, ConfigSlider, ConfigClock, ConfigBoolean
from Components.ScrollLabel import ScrollLabel
from Components.Console import Console as ComConsole
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Harddisk import harddiskmanager
from Components.Input import Input
from Components.Ipkg import IpkgComponent
from Plugins.Extensions.PersianPalace import *
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Network import iNetwork
from Components.Pixmap import Pixmap, MultiPixmap
from Components.PluginComponent import plugins
from Components.PluginList import *
from Components.ProgressBar import ProgressBar
from Components.SelectionList import SelectionList
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import pathExists, fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_PLUGIN, SCOPE_CURRENT_SKIN, SCOPE_METADIR
from Tools.HardwareInfo import HardwareInfo
from Tools.LoadPixmap import LoadPixmap
from Tools.NumericalTextInput import NumericalTextInput
from ServiceReference import ServiceReference
from enigma import eConsoleAppContainer, eTimer, quitMainloop, RT_HALIGN_LEFT, RT_VALIGN_CENTER, eListboxPythonMultiContent, eListbox, gFont, getDesktop, ePicLoad, iServiceInformation
from enigma import ePoint, eSize, eTimer, eEnv, eRCInput, getPrevAsciiCode
from random import randint
from skin import loadSkin
from cPickle import dump, load
from os import system, listdir, symlink, unlink, readlink, path as os_path, stat, mkdir, popen, makedirs, access, rename, remove, W_OK, R_OK, F_OK, chmod, walk, getcwd, chdir, statvfs
from random import Random
from stat import ST_MTIME
from time import *
import string
import sys
from BackupRestore import BackupSelection, RestoreMenu, BackupScreen, RestoreScreen, getBackupPath, getBackupFilename
from bitrate import Bitrate
from HddSetup import HddSetup
from Scripts import Scripts
from About import AboutTeam
from DaemonsList import DaemonsList
from Swap import Swap
from Addons import AddonsFileBrowser
from __init__ import _, loadPluginSkin

config.plugins.pepanel = ConfigSubsection()
config.plugins.pepanel.configurationbackup = ConfigSubsection()
config.plugins.pepanel.configurationbackup.backuplocation = ConfigText(default='/media/hdd/', visible_width=50, fixed_size=False)
config.plugins.pepanel.configurationbackup.backupdirs = ConfigLocations(default=[eEnv.resolve('${sysconfdir}/enigma2/'),
 '/etc/tuxbox/config/',
 '/etc/network/interfaces',
 '/etc/wpa_supplicant.conf',
 '/etc/resolv.conf',
 '/etc/default_gw',
 '/etc/hostname'])
config.plugins.sundtekcontrolcenter = ConfigSubsection()
config.plugins.sundtekcontrolcenter.dvbtransmission = ConfigSelection(default='0', choices=[('0', _('DVB-S/S2')), ('1', _('DVB-C')), ('2', _('DVB-T'))])
config.plugins.sundtekcontrolcenter.autostart = ConfigYesNo(default=False)
config.plugins.sundtekcontrolcenter.usbnet = ConfigSubsection()
config.plugins.sundtekcontrolcenter.usbnet.selection = ConfigSelection(default='0', choices=[('0', _('via USB')), ('1', _('via Network'))])
config.plugins.sundtekcontrolcenter.usbnet.networkip = ConfigText(default='0.0.0.0', visible_width=50, fixed_size=False)
modelist = {'0': _('None'),
 '1': _('Nova WinTV')}
config.plugins.USBTunerSetup = ConfigSubsection()
config.plugins.USBTunerSetup.mode1 = ConfigSelection(choices=modelist, default='0')
config.plugins.dvbntptime = ConfigSubsection()
config.plugins.dvbntptime.ntpautocheck = ConfigYesNo(default=False)
config.plugins.dvbntptime.tdtautocheck = ConfigYesNo(default=False)
config.plugins.dvbntptime.enablemainmenu = ConfigYesNo(default=False)
config.plugins.dvbntptime.showntpmessage = ConfigYesNo(default=False)
showmessage = _('Show NTP message on startup') + ': '
ntpautostart = _('NTP-Server autostart') + ': '
tdtautostart = _('DVB Time check autostart') + ': '
transponderupdate = _('Enigma 2 Timeupdate') + ': '
iface = None

class PEMainMenu(Screen):

    def __init__(self, session, args = 0):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self['key_red'] = StaticText(_('Close'))
        self['key_green'] = StaticText(_('System Infos'))
        self['key_yellow'] = StaticText(_('System Tools'))
        self.title = _('PE Panel')
        try:
            self['title'] = StaticText(self.title)
        except:
            print 'self["title"] was not found in skin'
        self['actions'] = ActionMap(['ColorActions', 'SetupActions'], {'red': self.redPressed,
         'green': self.greenPressed,
         'yellow': self.yellowPressed,
         'ok': self.okPressed,
         'cancel': self.close}, -1)
        self.dlg = None
        self.state = {}
        self.list = []
        self.output_line = ''
        self['list'] = List(self.list)
        self.onLayoutFinish.append(self.createMENUlist)

    def createMENUlist(self):
        self.mylist = []
        divpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/div-h.png'))
        if fileExists(resolveFilename(SCOPE_PLUGINS, '/usr/lib/enigma2/python/Plugins/Extensions/PECamManager/plugin.pyo')):
            self.mylist.append((_('Cam Manager'),
             'CamSelectMenu',
             _('manage your favourite cam'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/camcenter.png')),
             divpng))
        self.mylist.append((_('System Info'),
         'SystemInfoMenu',
         _('Infos about your PE'),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/systeminfo.png')),
         divpng))
        self.mylist.append((_('System Tools'),
         'SystemToolsMenu',
         _('manage your PE'),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/systemtools.png')),
         divpng))
        self.mylist.append((_('Backup Tools'),
         'BackupToolsMenu',
         _('backup or restore your settings'),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/backuptools.png')),
         divpng))
        self.mylist.append((_('Softwaremanager'),
         'manInstallerMenu',
         _('Online, Offline Installer for IPK and several Archives'),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/manualinstaller.png')),
         divpng))
        self.mylist.append((_('Plugins'),
         'PluginBrowser',
         _('open enigma2 Plugin Menu'),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/addons.png')),
         None))
        self['list'].setList(self.mylist)

    def okPressed(self):
        cur = self['list'].getCurrent()
        if cur:
            name = cur[0]
            menu = cur[1]
            if menu == 'CamSelectMenu':
                if fileExists(resolveFilename(SCOPE_PLUGINS, '/usr/lib/enigma2/python/Plugins/Extensions/PECamManager/plugin.pyo')):
                    try:
                        from Plugins.Extensions.PECamManager import *
                    except ImportError:
                        self.session.open(MessageBox, _('The PE Cam Manager Plugin is not installed!\nPlease install it.'), type=MessageBox.TYPE_INFO, timeout=10)
                    else:
                        self.session.open(plugin.PECamManager)
            elif menu == 'PluginBrowser':
                self.session.open(PluginBrowser)
            elif menu == 'BackupToolsMenu':
                self.session.open(PESubMenu, 0)
            elif menu == 'manInstallerMenu':
                self.session.openWithCallback(self.updateList, PESubMenu, 1)
            elif menu == 'ImageToolsMenu':
                self.session.open(PESubMenu, 2)
            elif menu == 'SystemToolsMenu':
                self.session.open(PESubMenu, 3)
            elif menu == 'SystemInfoMenu':
                self.session.open(PESubMenu, 4)
            else:
                message = '[PEPanel] no menu linked to ' + name
                self.session.open(MessageBox, message, MessageBox.TYPE_INFO, timeout=5)

    def setWindowTitle(self, title = None):
        if not title:
            title = self.title
        self.setTitle(title)
        self['title'] = StaticText(title)

    def updateList(self):
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))

    def redPressed(self):
        self.close(0)

    def greenPressed(self):
        self.session.open(PESubMenu, 4)

    def yellowPressed(self):
         self.session.open(PESubMenu, 3)

    def cancel(self):
        self.close()


class PESubMenu(Screen):

    def __init__(self, session, menuid, args = 0):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self.menu = menuid
        self.title = _('Submenu')
        try:
            self['title'] = StaticText(self.title)
        except:
            print 'self["title"] was not found in skin'
        self.list = []
        self.text = ''
        self.backupdirs = ' '.join(config.plugins.pepanel.configurationbackup.backupdirs.value)
        if self.menu == 0:
            menuid = 0
            self.list.append(('system-backup',
             _('Backup system settings'),
             _('Backup your STB settings.'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/savesettings.png')),
             None,
             menuid))
            self.list.append(('system-restore',
             _('Restore system settings'),
             _('Restore your STB settings.'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/restoresettings.png')),
             None,
             menuid))
            self.list.append(('advancedrestore',
             _('Advanced restore'),
             _('Restore your backups by date.'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/restoreadvanced.png')),
             None,
             menuid))
            self.list.append(('backuplocation',
             _('Choose backup location'),
             _('Select your backup device. '),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/backuplocation.png')),
             None,
             menuid))
            self.list.append(('backupfiles',
             _('Choose backup files'),
             _('Select files for backup. '),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/backupfiles.png')),
             None,
             menuid))
            self.title = _('Backup Tools')
        elif self.menu == 1:
            menuid = 1
            self.list.append(('targz',
             _('Addon Installer Filebrowser'),
             _('Install IPK, tar.gz, tgz, tar.bz2, zip and rar Packages'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/addoninstaller.png')),
             None,
             menuid))
            self.list.append(('ipkg2',
             _('Install IPK from all Storage Media'),
             _('Install IPK from Root Directory or /tmp'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/ipkg.png')),
             None,
             menuid))
            self.list.append(('allpacketmanager',
             _('Show all available Packages'),
             _('Install, Update or Remove all available Packages from Feed'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/ipkgall.png')),
             None,
             menuid))
            if fileExists(resolveFilename(SCOPE_PLUGINS, '/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/plugin.pyo')):
                self.list.append(('ipkgcams',
                 _('Show CAM'),
                 _('Install, Update or Remove all available CAMs from Feed'),
                 LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/ipkgcam.png')),
                 None,
                 menuid))
            self.list.append(('ipkgpicons',
             _('Show Picons'),
             _('Install, Update or Remove all available Picons from Feed'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/ipkgpicon.png')),
             None,
             menuid))
            self.list.append(('ipkgsettings',
             _('Show Settings'),
             _('Install, Update or Remove all available Settings from Feed'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/ipkgsettings.png')),
             None,
             menuid))
            self.list.append(('ipkgsystemplugins',
             _('Show Systemplugins'),
             _('Install, Update or Remove all available Systemplugins from Feed'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/ipkgsystemplugins.png')),
             None,
             menuid))
            self.list.append(('ipkgextensions',
             _('Show Extensions'),
             _('Install, Update or Remove all available Extensions from Feed'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/ipkgpicon.png')),
             None,
             menuid))
            self.list.append(('ipkgdrivers',
             _('Show Drivers'),
             _('Install, Update or Remove all available Drivers from Feed'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/ipkgpdrivers.png')),
             None,
             menuid))
            self.list.append(('ipkgskins',
             _('Show Skins'),
             _('Install, Update or Remove all available Skins from Feed'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/ipkgskins.png')),
             None,
             menuid))
            self.list.append(('ipkgothers',
             _('Show Other Packages'),
             _('Install, Update or Remove all available Other from Feed'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/ipkgpothers.png')),
             None,
             menuid))
        elif self.menu == 3:
            menuid = 3
            if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/Videomode/plugin.pyo')):
                self.list.append(('AVSettings',
                 _('A/V Settings'),
                 _('Show Videomodeconfiguration'),
                 LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/avsettings.png')),
                 None,
                 menuid))
            if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/DreamExplorer/plugin.pyo')):
                self.list.append(('FileManager',
                 _('File Manager'),
                 _('open Filemanager'),
                 LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/filemanager_sub.png')),
                 None,
                 menuid))
            if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/NetworkBrowser/NetworkBrowser.pyo')):
                self.list.append(('NetworkBrowser',
                 _('Network Browser'),
                 _('open NetworkBrowswer'),
                 LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/networkbrowser_sub.png')),
                 None,
                 menuid))
            if fileExists('/usr/lib/enigma2/python/Screens/NetworkSetup.pyo'):
                self.list.append(('NetworkIfc',
                 _('Network Interfaces'),
                 _('See your Network Interfaces'),
                 LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/networkifc.png')),
                 None,
                 menuid))
            if fileExists('/usr/lib/enigma2/python/Screens/NetworkSetup.pyo'):
                self.list.append(('NetworkDNS',
                 _('Network Nameserver'),
                 _('See your DNS-Server'),
                 LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/networkdns.png')),
                 None,
                 menuid))
            if fileExists('/usr/lib/enigma2/python/Screens/NetworkSetup.pyo'):
                self.list.append(('NetworkMounts',
                 _('Network Mounts'),
                 _('See your Network mounts'),
                 LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/networkmounts.png')),
                 None,
                 menuid))
            if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/CrossEPG/plugin.pyo')):
                self.list.append(('CrossEPG',
                 _('CrossEPG'),
                 _('Enhanced EPG-Import Services'),
                 LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/epg.png')),
                 None,
                 menuid))
            self.list.append(('passwd',
             _('Set Root Password'),
             _('set root password of your stb'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/passwd.png')),
             None,
             menuid))
            self.list.append(('kernel',
             _('Kernel Modules'),
             _('Show Active Kernel Modules'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/kernel.png')),
             None,
             menuid))
            if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/NfsServer/plugin.pyo')):
                self.list.append(('nfsserver',
                 _('NFS-Server Panel'),
                 _('enable/disable and configure NFS-Server'),
                 LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/nfsserver.png')),
                 None,
                 menuid))
            if fileExists('/usr/sbin/openvpn'):
                self.list.append(('openvpn',
                 _('OpenVPN-Server Panel'),
                 _('Configure your OpenVPN-Server'),
                 LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/openvpnserver.png')),
                 None,
                 menuid))
            self.list.append(('daemons',
             _('Daemons'),
             _('enable/disable Systemservices'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/services.png')),
             None,
             menuid))
            self.list.append(('scripts',
             _('User scripts'),
             _('Execute Scripts from /usr/script'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/scripts.png')),
             None,
             menuid))
            self.list.append(('cronjobs',
             _('Cronjobs'),
             _('Manage STB Cronjobs'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/cronjob.png')),
             None,
             menuid))
            self.list.append(('sundtekcontrolcenter',
             _('Sundtek USB DVB-Panel'),
             _('Control your USB DVB-T/C/S2-Stick'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/sundtekucontrolcenter.png')),
             None,
             menuid))
            self.list.append(('hauppagewintvstick',
             _('Hauppage USB DVB-T Panel'),
             _('Control your WinTV Nova Stick'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/hauppagewintvnova.png')),
             None,
             menuid))
            self.list.append(('disksetup',
             _('Device Manager'),
             _('Control your local Storage'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/disks.png')),
             None,
             menuid))
            self.list.append(('ipkuninstaller',
             _('IPK Uninstaller'),
             _('remove seletected package from stb'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/ipkgremove.png')),
             None,
             menuid))
            if os_path.exists('/dev/sda') == True:
                self.list.append(('e2crashlog',
                 _('Purge Enigma2 Crashlogs'),
                 _('selective wipe of enigma2 crashlogs'),
                 LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/crashlog.png')),
                 None,
                 menuid))
            self.list.append(('swap',
             _('Swapfile'),
             _('create and manage your Swapfile'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/swapfile.png')),
             None,
             menuid))
            self.list.append(('ntptime',
             _('Set NTP Time'),
             _('refresh time for enigma2 from ntp server'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/ntptime.png')),
             None,
             menuid))
            if os_path.exists('/dev/sda') == True:
                self.list.append(('hddinfo',
                 _('Hard Disk Infopanel'),
                 _('Control your HDD Parameter'),
                 LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/hddstandby.png')),
                 None,
                 menuid))
            self.title = _('System Tools')
        elif self.menu == 4:
            menuid = 4
            self.list.append(('sysinfo',
             _('Infopanel'),
             _('Complete overview of system parameters'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/sysinfo.png')),
             None,
             menuid))
            self.list.append(('who',
             _('Show Consolesessions'),
             _('show all active user sessions'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/sessions.png')),
             None,
             menuid))
            self.list.append(('sockets',
             _('Show Networkconnections'),
             _('show all connected sockets from ip-stack'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/sockets.png')),
             None,
             menuid))
            self.list.append(('networkconfig',
             _('Show Networkdetails'),
             _('shows assigned ip-adresses, routingtable and nameserver'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/nwcfg.png')),
             None,
             menuid))
            self.setWindowTitle(_('System Infos'))
            self.list.append(('aboutimage',
             _('Image Infos'),
             _('Show Image Infos'),
             LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/about.png')),
             None,
             menuid))
            self.title = _('System Infos')
        self['list'] = List(self.list)
        self['key_red'] = StaticText(_('Close'))
        self['shortcuts'] = ActionMap(['ShortcutActions', 'WizardActions', 'InfobarEPGActions'], {'ok': self.go,
         'back': self.close,
         'red': self.close}, -1)
        self.onLayoutFinish.append(self.layoutFinished)
        self.backuppath = getBackupPath()
        self.backupfile = getBackupFilename()
        self.fullbackupfilename = self.backuppath + '/' + self.backupfile

    def setWindowTitle(self, title = None):
        if not title:
            title = self.title
        try:
            self['title'] = StaticText(title)
        except:
            print 'self["title"] was not found in skin'

    def layoutFinished(self):
        idx = 0
        self['list'].index = idx

    def go(self):
        current = self['list'].getCurrent()
        if current:
            currentEntry = current[0]
            if currentEntry == 'backuplocation':
                parts = [ (r.description, r.mountpoint, self.session) for r in harddiskmanager.getMountedPartitions(onlyhotplug=False) ]
                for x in parts:
                    if not access(x[1], F_OK | R_OK | W_OK) or x[1] == '/':
                        parts.remove(x)
                for x in parts:
                    if x[1].startswith('/autofs/'):
                        parts.remove(x)
                if len(parts):
                    self.session.openWithCallback(self.backuplocation_choosen, ChoiceBox, title=_('Please select medium to use as backup location'), list=parts)
            elif currentEntry == 'backupfiles':
                self.session.openWithCallback(self.backupfiles_choosen, BackupSelection)
            elif currentEntry == 'advancedrestore':
                self.session.open(RestoreMenu, self.skin_path)
            elif currentEntry == 'system-backup':
                self.session.openWithCallback(self.backupDone, BackupScreen, runBackup=True)
            elif currentEntry == 'system-restore':
                if os_path.exists(self.fullbackupfilename):
                    self.session.openWithCallback(self.startRestore, MessageBox, _('Are you sure you want to restore your Enigma2 backup?\nEnigma2 will restart after the restore'))
                else:
                    self.session.open(MessageBox, _('Sorry no backups found!'), MessageBox.TYPE_INFO, timeout=10)
            elif currentEntry == 'tar.gz':
                self.session.openWithCallback(self.updateList, Console, title=_('.tar.gz installer'), cmdlist=['for i in /tmp/*.tar.gz; do echo Installing $i; tar -xzf $i -C /; done'])
            elif currentEntry == 'targz':
                self.checkPanel()
            elif currentEntry == 'ipkg2':
                try:
                    from Plugins.Extensions.MediaScanner.plugin import main
                    main(self.session)
                except:
                    self.session.open(MessageBox, _('Sorry MediaScanner is not installed!'), MessageBox.TYPE_INFO, timeout=10)
            elif currentEntry == 'allpacketmanager':
                if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/SoftwareManager/plugin.pyo')):
                    try:
                        from Plugins.SystemPlugins.SoftwareManager.plugin import PacketManager
                        self.session.open(PacketManager, self.skin_path)
                    except ImportError:
                        self.session.open(MessageBox, _('The SoftwareManager Plugin is not installed!\nPlease install it.'), type=MessageBox.TYPE_INFO, timeout=10)
            elif currentEntry == 'ipkgcams':
                plugin_prefix = ('enigma2-plugin-softcam', 'enigma2-softcam', 'softcam', 'persianpalace-cam', 'cam')
                cache_prefix = 'packetmanager-cams.cache'
                title_prefix = _('Install, Upgrade or Delete CAMs')
                self.session.open(PEPacketManager, self.skin_path, plugin_prefix, cache_prefix, title_prefix)
            elif currentEntry == 'ipkgpicons':
                plugin_prefix = ('enigma2-plugin-picon', 'enigma2-picon', 'picon')
                cache_prefix = 'packetmanager-picons.cache'
                title_prefix = _('Install, Upgrade or Delete Picons')
                self.session.open(PEPacketManager, self.skin_path, plugin_prefix, cache_prefix, title_prefix)
            elif currentEntry == 'ipkgsettings':
                plugin_prefix = ('enigma2-plugin-setting', 'enigma2-setting', 'setting')
                cache_prefix = 'packetmanager-settings.cache'
                title_prefix = _('Install, Upgrade or Delete Settings')
                self.session.open(PEPacketManager, self.skin_path, plugin_prefix, cache_prefix, title_prefix)
            elif currentEntry == 'ipkgsystemplugins':
                plugin_prefix = ('enigma2-plugin-systemplugins', 'systemplugin')
                cache_prefix = 'packetmanager-systemplugins.cache'
                title_prefix = _('Install, Upgrade or Delete Systemplugins')
                self.session.open(PEPacketManager, self.skin_path, plugin_prefix, cache_prefix, title_prefix)
            elif currentEntry == 'ipkgextensions':
                plugin_prefix = ('enigma2-plugin-extensions', 'extension')
                cache_prefix = 'packetmanager-extensions.cache'
                title_prefix = _('Install, Upgrade or Delete Extensions')
                self.session.open(PEPacketManager, self.skin_path, plugin_prefix, cache_prefix, title_prefix)
            elif currentEntry == 'ipkgdrivers':
                plugin_prefix = ('enigma2-plugin-driver', 'firmware', 'kernel-module-', '-dvb-modules-', 'kernel-firmware-', 'driver', 'modules', 'v4l', 'dvb')
                cache_prefix = 'packetmanager-drivers.cache'
                title_prefix = _('Install, Upgrade or Delete Drivers')
                self.session.open(PEPacketManager, self.skin_path, plugin_prefix, cache_prefix, title_prefix)
            elif currentEntry == 'ipkgskins':
                plugin_prefix = ('enigma2-plugin-skin', 'enigma2-skin', 'skin')
                cache_prefix = 'packetmanager-skins.cache'
                title_prefix = _('Install, Upgrade or Delete Skins')
                self.session.open(PEPacketManager, self.skin_path, plugin_prefix, cache_prefix, title_prefix)
            elif currentEntry == 'ipkgothers':
                plugin_prefix = ('enigma2-plugin-other', 'enigma2-plugin-security', 'enigma2-plugin-upnp', 'enigma2-plugin-pli')
                cache_prefix = 'packetmanager-others.cache'
                title_prefix = _('Install, Upgrade or Delete Other Packages')
                self.session.open(PEPacketManager, self.skin_path, plugin_prefix, cache_prefix, title_prefix)
            elif currentEntry == 'ipkgxt':
                plugin_prefix = ('enigma2-pe-', 'pe-', '-pe-')
                cache_prefix = 'packetmanager-pe.cache'
                title_prefix = _('Install, Remove PE Packages')
                tlist = []				
            elif currentEntry == 'update-image':
                if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/SoftwareManager/plugin.pyo')):
                    try:
                        from Plugins.SystemPlugins.SoftwareManager import plugin
                    except ImportError:
                        self.session.open(MessageBox, _('The SoftwareManager Plugin is not installed!\nPlease install it.'), type=MessageBox.TYPE_INFO, timeout=10)
                    else:
                        self.session.openWithCallback(self.runUpgrade, MessageBox, _('Do you want to update your STB?') + '\n' + _('\nAfter pressing OK, please wait!'))
            elif currentEntry == 'install-image':
                self.session.open(MessageBox, _('Menu ') + currentEntry + _(' not implemented yet\n\nPlease choose another one.'), MessageBox.TYPE_INFO, timeout=5)
            elif currentEntry == 'AVSettings':
                if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/Videomode/plugin.pyo')):
                    try:
                        from Plugins.SystemPlugins.Videomode.plugin import videoSetupMain
                    except ImportError:
                        self.session.open(MessageBox, _('The Videomode Plugin is not installed!\nPlease install it.'), type=MessageBox.TYPE_INFO, timeout=10)
                    else:
                        videoSetupMain(self.session)
            elif currentEntry == 'FileManager':
                if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/DreamExplorer/plugin.pyo')):
                    try:
                        from Plugins.Extensions.DreamExplorer.plugin import *
                    except ImportError:
                        self.session.open(MessageBox, _('The FileManager is not installed!\nPlease install it.'), type=MessageBox.TYPE_INFO, timeout=10)
                    else:
                        self.session.open(DreamExplorerII)
            elif currentEntry == 'NetworkBrowser':
                if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/NetworkBrowser/NetworkBrowser.pyo')):
                    try:
                        from Plugins.SystemPlugins.NetworkBrowser.NetworkBrowser import NetworkBrowser
                    except ImportError:
                        self.session.open(MessageBox, _('The NetworkBrowser is not installed!\nPlease install it.'), type=MessageBox.TYPE_INFO, timeout=10)
                    else:
                        self.session.open(NetworkBrowser, iface, plugin_path)
            elif currentEntry == 'CrossEPG':
                if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/CrossEPG/plugin.pyo')):
                    try:
                        from Plugins.SystemPlugins.CrossEPG.crossepg_main import crossepg_main
                    except ImportError:
                        self.session.open(MessageBox, _('The CrossEPG Plugin is not installed!\nPlease install it.'), type=MessageBox.TYPE_INFO, timeout=10)
                    else:
                        crossepg_main.setup(self.session)
            elif currentEntry == 'NetworkIfc':
                if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/NetworkBrowser/NetworkBrowser.pyo')):
                    self.session.open(NetworkAdapterSelection)
            elif currentEntry == 'NetworkDNS':
                if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/NetworkBrowser/NetworkBrowser.pyo')):
                    self.session.open(NameserverSetup)
            elif currentEntry == 'NetworkBrowse':
                if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/NetworkBrowser/NetworkBrowser.pyo')):
                    try:
                        from Plugins.SystemPlugins.NetworkBrowser.plugin import NetworkBrowserMain
                    except ImportError:
                        self.session.open(MessageBox, _('The Networkbrowser Plugin is not installed!\nPlease install it.'), type=MessageBox.TYPE_INFO, timeout=10)
                    else:
                        NetworkBrowserMain(self.session)
            elif currentEntry == 'NetworkMounts':
                if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/NetworkBrowser/NetworkBrowser.pyo')):
                    try:
                        from Plugins.SystemPlugins.NetworkBrowser.plugin import MountManagerMain
                    except ImportError:
                        self.session.open(MessageBox, _('The Networkbrowser Plugin is not installed!\nPlease install it.'), type=MessageBox.TYPE_INFO, timeout=10)
                    else:
                        MountManagerMain(self.session)
            elif currentEntry == 'kernel':
                self.session.open(PEKernelModShow)
            elif currentEntry == 'nfsserver':
                if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/NfsServer/plugin.pyo')):
                    try:
                        from Plugins.Extensions.NfsServer.plugin import *
                    except ImportError:
                        self.session.open(MessageBox, _('The NFSServer Plugin is not installed!\nPlease install it.'), type=MessageBox.TYPE_INFO, timeout=10)
                    else:
                        self.session.open(NFSServerSetup)
            elif currentEntry == 'openvpn':
                self.session.open(PEOpenvpn)
            elif currentEntry == 'passwd':
                self.session.open(PasswdScreen)
            elif currentEntry == 'services':
                self.session.open(PEStatusListMenu, 22)
            elif currentEntry == 'daemons':
                self.session.open(DaemonsList)
            elif currentEntry == 'scripts':
                self.session.open(Scripts)
            elif currentEntry == 'cronjobs':
                self.session.open(PECronMang)
            elif currentEntry == 'sundtekusbdvb':
                self.session.open(PEStatusListMenu, 28)
            elif currentEntry == 'sundtekcontrolcenter':
                self.session.open(SundtekControlCenter)
            elif currentEntry == 'hauppagewintvstick':
                self.session.open(USBTunerSetupScreen)
            elif currentEntry == 'disksetup':
                self.session.open(HddSetup)
            elif currentEntry == 'ipkuninstaller':
                self.session.open(PEStatusListMenu, 24)
            elif currentEntry == 'skinremove':
                self.session.open(PEStatusListMenu, 25)
            elif currentEntry == 'e2crashlog':
                self.session.open(PEStatusListMenu, 26)
            elif currentEntry == 'ntfspart':
                self.session.open(PEStatusListMenu, 27)
            elif currentEntry == 'sambaservice':
                self.session.open(PESamba)
            elif currentEntry == 'telnetservice':
                self.session.open(PETelnet)
            elif currentEntry == 'ftpservice':
                self.session.open(PEFtp)
            elif currentEntry == 'swapfile':
                self.session.open(PEStatusListMenu, 21)
            elif currentEntry == 'swap':
                self.session.open(Swap)
            elif currentEntry == 'ntptime':
                self.session.open(PEDVBNTPTime)
            elif currentEntry == 'sysinfo':
                self.session.open(PEInfo)
            elif currentEntry == 'hddstandby':
                self.session.open(Console, title=_('Harddisk Standbymode'), cmdlist=['hdparm -y /dev/sda'])
            elif currentEntry == 'hddinfo':
                self.session.open(PEHdd)
            elif currentEntry == 'sysinfo':
                self.session.open(PEInfo)
            elif currentEntry == 'ecm':
                self.session.open(Console, title=_('Show ecm.info'), cmdlist=['for i in /tmp/ecm*info;do echo $i;echo ------------------------------------------------; cat $i; echo ================================================; done'])
            elif currentEntry == 'ecminfo':
                self.session.open(ECMBluePanel)
            elif currentEntry == 'ps-xa':
                self.session.open(PEProcInfo)
            elif currentEntry == 'e2settings':
                self.session.open(PEEnsetInfo)
            elif currentEntry == 'dmesg':
                self.session.open(dmesgInfo)
            elif currentEntry == 'mount':
                self.session.open(Console, title=_('Show mounted filesystems'), cmdlist=['mount'])
            elif currentEntry == 'networkconfig':
                self.session.open(Console, title=_('Show networkconfiguration and routingtable'), cmdlist=['ip addr; iwconfig; echo ------------------------------------------------; route -n; echo ================================================; cat /etc/resolv.conf'])
            elif currentEntry == 'ntfspartition':
                self.session.open(Console, title=_('Show ntfs partitions'), cmdlist=['fdisk -l | grep NTFS; echo ------------------------------------------------; ls -lR /dev/disk/by-uuid'])
            elif currentEntry == 'hddtemp':
                if os_path.exists('/dev/sda') == True:
                    msg = self.session.openWithCallback(self.hdparm, MessageBox, _("Harddiskmanufacturer, Type and it's Temperature :") + '\n\n' + self.ScanHDD() + '\n\n' + _('Are you sure to set hdd in standby mode?'), MessageBox.TYPE_YESNO)
                    msg.setTitle(_('HDD Temperature'))
                else:
                    self.session.open(MessageBox, _('No internal Harddisk detected!!!! \n\nPlease install an internal Harddisk first to be in a position to check harddisk temperature.'), MessageBox.TYPE_INFO, timeout=5)
            elif currentEntry == 'who':
                self.session.open(Console, title=_('Active Usersessions :'), cmdlist=['who'])
            elif currentEntry == 'uptime':
                msg = self.session.open(MessageBox, _('Current Time, Operating Time and Load Average :') + '\n\n' + self.ShowUptime(), MessageBox.TYPE_INFO)
                msg.setTitle(_('Uptime'))
            elif currentEntry == 'sockets':
                self.session.open(Console, title=_('Show network stats'), cmdlist=['netstat -t -u'])
            elif currentEntry == 'memory':
                msg = self.session.open(MessageBox, _('Current Memory Usage :') + '\n\n' + self.ShowMemoryUsage(), MessageBox.TYPE_INFO)
                msg.setTitle(_('Memory Usage'))
            elif currentEntry == 'df-h':
                self.session.open(Console, title=_('Show free diskspace'), cmdlist=['df -h'])
            elif currentEntry == 'about':
                self.session.open(About)
            elif currentEntry == 'aboutimage':
                self.session.open(AboutTeam)
            else:
                self.session.open(MessageBox, _('Menu not implemented yet!!!! \n\nfeel free to code this menu now ;)'), MessageBox.TYPE_INFO, timeout=5)

    def askReboot(self):
        self.session.openWithCallback(self.reboot, MessageBox, _('Install/update finished.') + ' ' + _('Do you want to reboot your STB?'), MessageBox.TYPE_YESNO)

    def reboot(self, result):
        if result:
            quitMainloop(3)

    def backupfiles_choosen(self, ret):
        self.backupdirs = ' '.join(config.plugins.pepanel.configurationbackup.backupdirs.value)

    def backuplocation_choosen(self, option):
        if option is not None:
            config.plugins.pepanel.configurationbackup.backuplocation.value = str(option[1])
        config.plugins.pepanel.configurationbackup.backuplocation.save()
        config.plugins.pepanel.configurationbackup.save()
        config.save()
        self.createBackupfolders()

    def createBackupfolders(self):
        self.backuppath = getBackupPath()
        try:
            if os_path.exists(self.backuppath) == False:
                makedirs(self.backuppath)
        except OSError:
            self.session.open(MessageBox, _('Sorry, your backup destination is not writeable.\n\nPlease choose another one.'), MessageBox.TYPE_INFO, timeout=10)

    def backupDone(self, retval = None):
        if retval is True:
            self.session.open(MessageBox, _('Backup done.'), MessageBox.TYPE_INFO, timeout=10)
        else:
            self.session.open(MessageBox, _('Backup failed.'), MessageBox.TYPE_INFO, timeout=10)

    def startRestore(self, ret = False):
        if ret == True:
            self.exe = True
            self.session.open(RestoreScreen, runRestore=True)

    def updateList(self):
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))

    def ScanHDD(self):
        try:
            ret = ''
            out_line = popen('hddtemp -q /dev/sda').readline()
            ret = ret + out_line
            return ret
            out_line.close()
        except:
            return _('No Harddisk or Harddisk with S.M.A.R.T capabilites detected')

    def ShowUptime(self):
        try:
            ret = ''
            out_line = popen('uptime').readline()
            ret = ret + _('At') + out_line + '\n'
            return ret
            out_line.close()
        except:
            return _('Could not grep Uptime Information from busybox')

    def ShowAllSockets(self):
        try:
            ret = ''
            out_lines = []
            out_lines = popen('netstat -t -u').readlines()
            for lidx in range(len(out_lines) - 1):
                ret = ret + out_lines[lidx] + '\n'
            return ret
            out_lines.close()
        except:
            return _('Could not grep socket information from busybox')

    def ShowMemoryUsage(self):
        try:
            ret = ''
            out_lines = []
            out_lines = popen('free').readlines()
            for lidx in range(len(out_lines) - 1):
                ret = ret + out_lines[lidx] + '\n'

            return ret
            out_lines.close()
        except:
            return _('Could not grep Memory Usage information from busybox')

    def hdparm(self, result):
        if result is None or result is False:
            print 'no hdd standby confirmed'
        else:
            ret = ''
            out_line = popen('hdparm -y /dev/sda').readline()
            ret = ret + out_line
            return ret
            out_line.close()

    def checkPanel(self):
        check = 0
        pkgs = listdir('/tmp')
        for fil in pkgs:
            if fil.find('.tgz') != -1 or fil.find('.tar.gz') != -1:
                check = 1

        if check == 1:
            self.session.open(AddonsFileBrowser)
        else:
            self.session.open(AddonsFileBrowser)

    def runUpgrade(self, result):
        if result:
            try:
                from Plugins.SystemPlugins.SoftwareManager.plugin import UpdatePlugin
                self.session.open(UpdatePlugin, self.skin_path)
            except ImportError:
                self.session.open(MessageBox, _('The SoftwareManager Plugin is not installed!\nPlease install it.'), type=MessageBox.TYPE_INFO, timeout=10)


class PEStatusListMenu(Screen):

    def __init__(self, session, menuid, args = 0):
        Screen.__init__(self, session)
        self.menu = menuid
        self.skin_path = plugin_path
        self['key_red'] = Label()
        self['key_green'] = Label()
        self['key_yellow'] = Label()
        self['key_blue'] = Label()
        self['pic_red'] = Pixmap()
        self['pic_green'] = Pixmap()
        self['pic_yellow'] = Pixmap()
        self['pic_blue'] = Pixmap()
        self.title = _('PE Status List Menu')
        try:
            self['title'] = StaticText(self.title)
        except:
            print 'self["title"] was not found in skin'
        if self.menu == 21:
            self['key_red'].setText(_('Stop Swap'))
            self['key_green'].setText(_('Start Swap'))
            self['key_yellow'].hide()
            self['key_blue'].hide()
            self['pic_yellow'].hide()
            self['pic_blue'].hide()
            self.setWindowTitle(_('SwapFile Menu'))
            self.onShown.append(self.buildSwapList)
        elif self.menu == 22:
            self['key_red'].setText(_('Stop'))
            self['key_green'].setText(_('Start'))
            self['key_yellow'].setText(_('Restart'))
            self['key_blue'].hide()
            self['pic_blue'].hide()
            self.setWindowTitle(_('Services Menu'))
            self.onShown.append(self.buildServicesList)
        elif self.menu == 24:
            self['key_red'].setText(_('Uninstall'))
            self['key_green'].setText(_('Force uninst.'))
            self['key_yellow'].hide()
            self['key_blue'].hide()
            self['pic_yellow'].hide()
            self['pic_blue'].hide()
            self.title = _('IPK Uninstaller')
            self.onShown.append(self.buildIPKinstalledList)
            self.onClose.append(self.delIPKDB)
        elif self.menu == 25:
            self['key_red'].setText(_('Remove Skin'))
            self['key_green'].hide()
            self['key_yellow'].hide()
            self['key_blue'].hide()
            self['pic_green'].hide()
            self['pic_yellow'].hide()
            self['pic_blue'].hide()
            self.setWindowTitle(_('Skinremove Menu'))
            self.onShown.append(self.buildSkinList)
        elif self.menu == 26:
            self['key_red'].setText(_('Remove selected'))
            self['key_green'].setText(_('Remove all'))
            self['key_yellow'].setText(_('Remove older 7 Days'))
            self['key_blue'].hide()
            self['pic_blue'].hide()
            self.title = _('Crashlog Remover')
            self.onShown.append(self.buildCrashlogList)
        elif self.menu == 27:
            self['key_red'].hide()
            self['key_green'].hide()
            self['key_yellow'].hide()
            self['key_blue'].hide()
            self['pic_blue'].hide()
            self.setWindowTitle(_('NTFS Partition Menu'))
            self.onShown.append(self.buildDeviceList)
        elif self.menu == 28:
            self['key_red'].setText(_('Start'))
            self['key_green'].hide()
            self['pic_green'].hide()
            self['key_yellow'].hide()
            self['pic_yellow'].hide()
            self['key_blue'].hide()
            self['pic_blue'].hide()
            self.setWindowTitle(_('Sundtek USB DVB Menu'))
            self.onShown.append(self.buildSundtekUSBDVBList)
        else:
            self['key_red'].setText(_('not in use'))
            self['key_green'].setText(_('not in use'))
            self['key_yellow'].setText(_('not in use'))
            self['key_blue'].setText(_('not in use'))
            self.setWindowTitle(_('Status List Menu'))
        self['actions'] = ActionMap(['ColorActions', 'SetupActions'], {'red': self.redPressed,
         'green': self.greenPressed,
         'yellow': self.yellowPressed,
         'blue': self.bluePressed,
         'ok': self.okPressed,
         'cancel': self.close}, -1)
        self.list = []
        self.output_line = ''
        self['list'] = List(self.list)

    def setWindowTitle(self, title = None):
        if not title:
            title = self.title
        try:
            self['title'] = StaticText(title)
        except:
            print 'self["title"] was not found in skin'

    def redPressed(self):
        cur = self['list'].getCurrent()
        if cur and len(cur) > 2:
            if self.menu == 21:
                self.askForBuild(cur, 'stop')
            elif self.menu == 22:
                self.askForBuild(cur, 'stop')
            elif self.menu == 24:
                self.askForBuild(cur, 'stop')
            elif self.menu == 25:
                self.askForBuild(cur, 'stop')
            elif self.menu == 26:
                self.askForBuild(cur, 'stop')
            elif self.menu == 28:
                self.askForBuild(cur, 'stop')
            else:
                print '[PEStatusListMenu] red'

    def greenPressed(self):
        cur = self['list'].getCurrent()
        if cur and len(cur) > 2:
            if self.menu == 21:
                self.askForBuild(cur)
            elif self.menu == 22:
                self.askForBuild(cur, 'start')
            elif self.menu == 24:
                self.askForBuild(cur, 'start')
            elif self.menu == 26:
                self.askForBuild(cur, 'start')
            else:
                print '[PEStatusListMenu] green'

    def yellowPressed(self):
        cur = self['list'].getCurrent()
        if cur and len(cur) > 2:
            if self.menu == 22:
                self.askForBuild(cur, 'restart')
            elif self.menu == 26:
                self.askForBuild(cur, 'restart')
            else:
                print '[PEStatusListMenu] yellow'

    def bluePressed(self):
        cur = self['list'].getCurrent()
        if cur and len(cur) > 2:
            print '[PEStatusListMenu] blue'

    def okPressed(self):
        cur = self['list'].getCurrent()
        if cur and len(cur) > 2:
            if self.menu == 21:
                self.askForBuild(cur)
            else:
                print '[PEStatusListMenu] ok'

    def buildServicesList(self):
        try:
            list = []
            exclude = ['bootup',
             'devpts.sh',
             'halt',
             'rc',
             'rcS',
             'reboot',
             'rmnologin',
             'sendsigs',
             'single',
             'sysfs.sh',
             'umountfs']
            for root, dirnames, filenames in walk('/etc/init.d'):
                filenames.sort()
                for item in filenames:
                    if item not in exclude:
                        fullname = '/etc/init.d/' + item
                        list.append((item,
                         fullname,
                         None,
                         None))

            self['list'].setList(list)
        except:
            print 'Could not grab any services script from /etc/init.d/'

    def buildIPKinstalledList(self):
        try:
            list = []
            cmd = 'opkg list_installed > /tmp/ipkdb'
            system(cmd)
            ret = ''
            out_lines = []
            out_lines = open('/tmp/ipkdb').readlines()
            for filename in out_lines:
                ret = out_lines
                list.append((filename,
                 ret,
                 None,
                 None))

            self['list'].setList(list)
            out_lines.close()
        except:
            print 'Could not grab any installed IPK from OPKG Database'

    def buildSkinList(self):
        try:
            list = []
            chdir('/usr/share/enigma2')
            for root, dirnames, filenames in walk('.'):
                for filename in filenames:
                    if filename.endswith('skin.xml'):
                        if not root == '.':
                            root = root.replace('./', '')
                            fullname = '/usr/share/enigma2/' + root
                            list.append((root,
                             fullname,
                             None,
                             None))

            self['list'].setList(list)
        except:
            print 'Could not grab any additionally installed Skin from Skinbase'

    def buildCrashlogList(self):
        try:
            list = []
            curtime = time()
            path = '/media/hdd/'
            for infile in listdir('/media/hdd'):
                if infile.startswith('enigma2_crash') and infile.endswith('.log'):
                    list.append((infile,
                     None,
                     None,
                     None))

            self['list'].setList(list)
        except:
            print 'Could not grab any enigma2 crashlogs from /media/hdd/'

    def build2DeviceList(self, arg = None):
        self.listReady = False
        list = []
        for dev in self.getDeviceList():
            list.append(dev)

        self['list'].setList(list)

    def buildDeviceList(self):
        devices = []
        for dev in listdir('/dev'):
            dev = dev[:3]
            if dev.startswith('sdb1'):
                devices.append(dev)
            self['list'].setList(devices)

    def buildSundtekUSBDVBList(self):
        try:
            list = []
            for root, dirnames, filenames in walk('/usr/script'):
                filenames.sort()
                for item in filenames:
                    if item.startswith('DVB_') and item.endswith('.sh'):
                        fullname = '/usr/script/' + item
                        list.append((item,
                         fullname,
                         None,
                         None))

            self['list'].setList(list)
        except:
            print 'Could not grab any Sundtek USB DVB Scripts from /usr/script/'

    def buildSwapList(self):
        list = []
        cur_swap = self.checkSwap()
        for loc in swaplocations:
            if os_path.exists(loc) == True:
                for size in swapsizes:
                    text = str(size) + _('MB swapfile on ') + loc
                    if cur_swap[0] == loc and int(cur_swap[1]) == int(size):
                        list.append((text,
                         loc,
                         str(size),
                         LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/green_ok.png'))))
                    else:
                        list.append((text,
                         loc,
                         str(size),
                         None))

        self['list'].setList(list)

    def askForBuild(self, result, action = None):
        if self.menu == 21:
            try:
                self.swaptext = result[0]
                self.swaptarget = result[1]
                self.swapsize = result[2]
                if action == 'stop':
                    self.session.openWithCallback(self.stopSwap, MessageBox, _('Are you sure to delete swapfile ?'), MessageBox.TYPE_YESNO)
                else:
                    self.session.openWithCallback(self.buildSwapfile, MessageBox, _('Are you sure to %s ?') % self.swaptext, MessageBox.TYPE_YESNO)
            except:
                print '[PEPanel] nothing to do exit buildswap menu'

        elif self.menu == 22:
            try:
                bin = result[1]
                if action == 'start':
                    self.session.open(Console, title=_('Start Service'), cmdlist=[bin + ' start'])
                elif action == 'stop':
                    self.session.open(Console, title=_('Stop Service'), cmdlist=[bin + ' stop'])
                elif action == 'restart':
                    self.session.open(Console, title=_('Restart Service'), cmdlist=[bin + ' restart'])
            except:
                print '[PEPanel] nothing to do exit services menu'

        elif self.menu == 24:
            try:
                self.package = result[0]
                if action == 'start':
                    self.session.openWithCallback(self.ipkuninstallforce, MessageBox, _('Are you sure to force uninstall of selected package: \n') + self.package, MessageBox.TYPE_YESNO)
                elif action == 'stop':
                    self.session.openWithCallback(self.ipkuninstall, MessageBox, _('Are you sure to uninstall selected package: \n') + self.package, MessageBox.TYPE_YESNO)
            except:
                print '[PEPanel] nothing to do. exit ipk uninstaller menu'

        elif self.menu == 25:
            try:
                skin = result[1]
                if action == 'stop':
                    self.session.open(Console, title=_('Skinremoval'), cmdlist=['echo Removing Skin; rm -rf ' + skin])
            except:
                print '[PEPanel] nothing to do exit services menu'

        elif self.menu == 26:
            try:
                crashlog = result[0]
                if action == 'start':
                    ret = int(system('rm -f /media/hdd/enigma2_crash_*.log'))
                    if ret == 0:
                        self.session.open(MessageBox, _('Deleted all Enigma2 Crashlogs.'), MessageBox.TYPE_INFO)
                    else:
                        self.session.open(MessageBox, _('Could not delete all Enigma2 Crashlogs.'), MessageBox.TYPE_ERROR)
                elif action == 'stop':
                    ret = int(system('rm -f /media/hdd/' + crashlog))
                    if ret == 0:
                        self.session.open(MessageBox, _('Deleted Enigma2 Crashlog: \n\n' + crashlog), MessageBox.TYPE_INFO)
                    else:
                        self.session.open(MessageBox, _('Could not delete Enigma2 Crashlog: \n\n' + crashlog), MessageBox.TYPE_ERROR)
                elif action == 'restart':
                    path = '/media/hdd/'
                    msg = ''
                    ret = ''
                    curtime = time()
                    for infile in listdir('/media/hdd'):
                        if infile.startswith('enigma2_crash') and infile.endswith('.log'):
                            difftime = curtime - os_path.getmtime('/media/hdd/' + infile)
                            if difftime >= 604800:
                                ret = int(system('rm -f /media/hdd/' + infile))
                                msg += infile + '\n'

                    if ret == 0:
                        self.session.open(MessageBox, _('Deleted Crashlogs older 7 Days: \n\n' + msg), MessageBox.TYPE_INFO)
                    else:
                        self.session.open(MessageBox, _('Could not delete any Crashlogs older 7 Days. \n\n' + msg), MessageBox.TYPE_ERROR)
            except:
                print '[PEPanel] nothing to delete. exit e2crashlogremove menu'

        elif self.menu == 28:
            try:
                bin = result[1]
                if action == 'stop':
                    self.session.open(Console, title=_('Sundtek USB DVB Servicecontrol'), cmdlist=[bin])
            except:
                print '[PEPanel] nothing to do exit services menu'

        else:
            print '[PEPanel] wrong menuid'

    def checkSwap(self):
        try:
            for line in open(swapstarter):
                if line.lstrip().lower().startswith('swapon'):
                    swapfile = line.lstrip('swapon ').rstrip('\n')
                    try:
                        swapfilelocation = swapfile.rstrip('/swapfile')
                        swapfilesize = os_path.getsize(swapfile) / 1024 / 1024
                        return (swapfilelocation, int(swapfilesize))
                    except:
                        print '[PESwapMenu] swapfile size is ZERO'

            return (None, -1)
        except IOError:
            return (None, -1)

    def stopSwap(self, result):
        if result is None or result is False:
            print '[PEPanel] stopswap not confirmed'
        else:
            cur_swap = self.checkSwap()
            if cur_swap[0] is not None:
                swapfile = cur_swap[0] + '/swapfile'
                stopcmd = 'echo ' + _('stopping swap for ') + swapfile + ' && swapoff ' + swapfile + ' && rm -rf ' + swapstarter + ' ' + swapfile + ' && free && echo ' + _('swapfile was deleted successfully')
                self.session.open(Console, title=_('Create SwapFile'), cmdlist=[stopcmd])
            else:
                self.session.open(MessageBox, _('no swapfile active...'), MessageBox.TYPE_INFO, timeout=5)

    def buildSwapfile(self, result):
        if result is None or result is False:
            print '[PEPanel] buildswap not confirmed'
        else:
            swapfile = self.swaptarget + '/swapfile'
            if fileExists(swapfile):
                swapoff = 'swapoff ' + swapfile
                system(swapoff)
                unlink(swapfile)
            ddcmd = 'dd if=/dev/zero of=' + swapfile + ' bs=1024k count=' + self.swapsize + ' && echo creating swap signature && mkswap ' + swapfile + ' && echo enable swap && swapon ' + swapfile + ' && free && echo ' + _('swapfile was created successfully')
            socmd = 'swapon ' + swapfile
            self.session.open(Console, title=_('Create SwapFile'), cmdlist=[ddcmd])
            self.enableSwap(socmd)

    def enableSwap(self, swapcmd):
        try:
            unlink(swapstarter)
        except:
            print '[Swapfile] no %s ' % swapstarter

        fp = file(swapstarter, 'w')
        fp.write('#!/bin/sh\n')
        fp.write(swapcmd)
        fp.write('\n')
        fp.close()
        chmod(swapstarter, 493)

    def ipkuninstall(self, result):
        if result is None or result is False:
            print 'no ipk uninstall confirmed'
        else:
            self.session.open(Console, title=_('IPK Uninstall'), cmdlist=['opkg remove ' + self.package])

    def ipkuninstallforce(self, result):
        if result is None or result is False:
            print 'no forced ipk uninstall confirmed'
        else:
            self.session.open(Console, title=_('IPK Uninstall ignore depencies'), cmdlist=['opkg remove -force-depends ' + self.package])

    def delIPKDB(self):
        system('rm -r /tmp/ipkdb')

    def devicePartitions(self, dev):
        partitions = []
        dir = '/sys/block/%s' % dev
        if os_path.exists(dir):
            for partition in listdir(dir):
                if partition.startswith(dev) and partitions.append(partition):
                    return partitions

    def getUuid(self, part):
        uuid = popen('/lib/udev/vol_id -u /dev/%s' % part).read()
        if uuid == '':
            return 'no uuid'
        return uuid[:-1]

    def deviceVendor(self, dev):
        procfile = tryOpen('/sys/block/%s/device/vendor' % dev)
        if procfile == '':
            return ''
        vendor = procfile.readline().strip()
        procfile.close()
        return vendor

    def deviceModel(self, dev):
        procfile = tryOpen('/sys/block/%s/device/model' % dev)
        if procfile == '':
            return ''
        model = procfile.readline().strip()
        procfile.close()
        return model

    def getFilesysTyp(self, part):
        fstype = popen('/lib/udev/vol_id -t /dev/%s' % part).read()
        if fstype == '':
            return 'not formated'
        return fstype[:-1]


class SundtekControlCenter(Screen, ConfigListScreen):

    def __init__(self, session, args = 0):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        ConfigListScreen.__init__(self, [])
        self.updateSettingList()
        self['btt_red'] = Label(_('Exit'))
        self['btt_green'] = Label(_('Setup'))
        self['btt_yellow'] = Label(_('Stop Tuner'))
        self['btt_blue'] = Label(_('Start Tuner'))
        self['ok'] = Label(_('OK/ green = activate settings'))
        self['infos'] = Label(_('Info = show tuner informations'))
        self['bouquets'] = Label(_('Bouquet + = install or update driver'))
        self['netservers'] = Label(_('Bouquet - = scan for IPTV server addresses'))
        self['actions'] = ActionMap(['OkCancelActions',
         'ChannelSelectBaseActions',
         'ColorActions',
         'ChannelSelectEPGActions'], {'ok': self.save,
         'cancel': self.cancel,
         'red': self.cancel,
         'green': self.save,
         'yellow': self.tunerstop,
         'blue': self.tunerstart,
         'showEPGList': self.dvbinfo,
         'nextBouquet': self.fetchsundtekdriver,
         'prevBouquet': self.scannetwork}, -2)
        self.onLayoutFinish.append(self.layoutFinished)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.updateSettingList()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.updateSettingList()

    def updateSettingList(self):
        list = []
        list.append(getConfigListEntry(_('DVB Transmission Way'), config.plugins.sundtekcontrolcenter.dvbtransmission))
        list.append(getConfigListEntry(_('USB/Network'), config.plugins.sundtekcontrolcenter.usbnet.selection))
        if config.plugins.sundtekcontrolcenter.usbnet.selection.value == '1':
            sublist = [getConfigListEntry(_('Network IP'), config.plugins.sundtekcontrolcenter.usbnet.networkip)]
            list.extend(sublist)
        list.append(getConfigListEntry(_('Autostart'), config.plugins.sundtekcontrolcenter.autostart))
        self['config'].list = list
        self['config'].l.setList(list)

    def layoutFinished(self):
        self.setTitle(_('Sundtek Control Center'))

    def fetchsundtekdriver(self):
        self.session.openWithCallback(self.disclaimer, MessageBox, _('Sundtek legal notice:\nThis software comes without any warranty, use it at your own risk?'), MessageBox.TYPE_YESNO)

    def disclaimer(self, result):
        if result:
            chmod('/usr/lib/enigma2/python/Plugins/SystemPlugins/PEPanel/sundtekinstall.sh', 493)
            self.prompt('/usr/lib/enigma2/python/Plugins/SystemPlugins/PEPanel/sundtekinstall.sh')

    def save(self):
        for x in self['config'].list:
            x[1].save()

        configfile.save()
        self.setsettings()

    def cancel(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close(False, self.session)

    def setsettings(self):
        if not os_path.exists('/opt/bin/mediasrv') or not os_path.exists('/opt/bin/mediaclient') or not os_path.exists('/usr/sundtek/sun_dvb.sh'):
            self.session.openWithCallback(self.installdriverrequest, MessageBox, _('It seems the sundtek driver is not installed or not installed properly. Install the driver now?'), MessageBox.TYPE_YESNO)
        else:
            if config.plugins.sundtekcontrolcenter.autostart.value == False:
                self.prompt('/usr/sundtek/sun_dvb.sh noautostart')
            if config.plugins.sundtekcontrolcenter.usbnet.selection.value == '1':
                f = open('/etc/sundtek.net', 'w')
                networkingip = config.plugins.sundtekcontrolcenter.usbnet.networkip.value + '\n'
                networkingip.lstrip().rstrip()
                f.writelines('REMOTE_IPTV_SERVER=' + networkingip)
                f.close()
                if config.plugins.sundtekcontrolcenter.autostart.value == True:
                    self.prompt('/usr/sundtek/sun_dvb.sh enable_net')
            elif config.plugins.sundtekcontrolcenter.dvbtransmission.value == '0':
                if config.plugins.sundtekcontrolcenter.autostart.value == True:
                    self.prompt('/usr/sundtek/sun_dvb.sh enable_s2')
            elif config.plugins.sundtekcontrolcenter.dvbtransmission.value == '1':
                if config.plugins.sundtekcontrolcenter.autostart.value == True:
                    self.prompt('/usr/sundtek/sun_dvb.sh enable_c')
            elif config.plugins.sundtekcontrolcenter.autostart.value == True:
                self.prompt('/usr/sundtek/sun_dvb.sh enable_t')

    def tunerstart(self):
        for x in self['config'].list:
            x[1].save()

        configfile.save()
        self.setsettings()
        if os_path.exists('/opt/bin/mediasrv') and os_path.exists('/opt/bin/mediaclient') and os_path.exists('/usr/sundtek/sun_dvb.sh'):
            if config.plugins.sundtekcontrolcenter.dvbtransmission.value == '0':
                self.prompt('/usr/sundtek/sun_dvb.sh start_s2')
            elif config.plugins.sundtekcontrolcenter.dvbtransmission.value == '1':
                self.prompt('/usr/sundtek/sun_dvb.sh start_c')
            else:
                self.prompt('/usr/sundtek/sun_dvb.sh start_t')
            if config.plugins.sundtekcontrolcenter.usbnet.selection.value == '1':
                self.prompt('/usr/sundtek/sun_dvb.sh start_net')

    def tunerstop(self):
        self.prompt('/usr/sundtek/sun_dvb.sh stop')

    def dvbinfo(self):
        self.prompt('/usr/sundtek/sun_dvb.sh info')

    def scannetwork(self):
        if os_path.exists('/opt/bin//mediaclient'):
            networkingscan = popen('/opt/bin/mediaclient --scan-network', 'r').read()
            networkingip = networkingscan.split()[18]
            if networkingip == '-':
                self.session.open(MessageBox, _('No IPTV media server found'), MessageBox.TYPE_INFO)
            else:
                self.session.openWithCallback(self.usenetip, MessageBox, networkingscan + _('\n\nUse following address as IPTV media server?\n') + networkingip, MessageBox.TYPE_YESNO)

    def usenetip(self, result):
        if result:
            config.plugins.sundtekcontrolcenter.usbnet.selection.value = '1'
            config.plugins.sundtekcontrolcenter.usbnet.networkip.value = popen('/opt/bin/mediaclient --scan-network', 'r').read().split()[18]
            self.updateSettingList()

    def installdriverrequest(self, result):
        if result:
            self.session.openWithCallback(self.disclaimer, MessageBox, _('Sundtek legal notice:\nThis software comes without any warranty, use it at your own risk?'), MessageBox.TYPE_YESNO)

    def prompt(self, com):
        self.session.open(Console, _('comand line: %s') % com, ['%s' % com])


class USBTunerSetupScreen(Screen, ConfigListScreen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        from Components.ActionMap import ActionMap
        from Components.Button import Button
        self['ok'] = Button(_('OK'))
        self['cancel'] = Button(_('Cancel'))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.keyGo,
         'save': self.keyGreen,
         'cancel': self.keyCancel,
         'green': self.keyGreen,
         'red': self.keyCancel}, -2)
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session)
        mode1 = config.plugins.USBTunerSetup.mode1.value
        self.mode1 = ConfigSelection(choices=modelist, default=mode1)
        self.list.append(getConfigListEntry(_('Tuner1 type'), self.mode1))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def keyGreen(self):
        config.plugins.USBTunerSetup.mode1.value = self.mode1.value
        if config.plugins.USBTunerSetup.mode1.value == '0':
            self.doDeInstall()
        if config.plugins.USBTunerSetup.mode1.value == '1':
            self.doInstall()
        config.plugins.USBTunerSetup.save()
        self.close()

    def keyGo(self):
        pass

    def keyCancel(self):
        self.close()

    def doInstall(self):
        ret = int(system('opkg update'))
        if ret != 0:
            self.session.open(MessageBox, _('opkg update error'), MessageBox.TYPE_ERROR, 5)
            return
        ret = int(system('opkg install enigma2-plugin-drivers-dvb-usb-dib0700'))
        if ret != 0:
            self.session.open(MessageBox, _('opkg install error'), MessageBox.TYPE_ERROR, 5)
            return
        usbtype1 = int(config.plugins.USBTunerSetup.mode1.value)
        if usbtype1 == 1:
            ret = int(system('/usr/sbin/update-modules'))
            if ret != 0:
                self.session.open(MessageBox, _('update-modules error'), MessageBox.TYPE_ERROR, 5)
                return
            ret = int(fw_test_dib0700())
            if ret != 0:
                self.session.open(MessageBox, _('firmware download error'), MessageBox.TYPE_ERROR, 5)
                return
        if usbtype1 == 2:
            ret = int(system('/usr/sbin/update-modules'))
            if ret != 0:
                self.session.open(MessageBox, _('update-modules error'), MessageBox.TYPE_ERROR, 5)
                return
            ret = int(fw_test_smsusb())
            if ret != 0:
                self.session.open(MessageBox, _('firmware download error'), MessageBox.TYPE_ERROR, 5)
                return
        config.plugins.USBTunerSetup.save()
        self.session.open(MessageBox, _('done with no errors, please restart'), MessageBox.TYPE_INFO)

    def doDeInstall(self):
        usbtyperemove = 1
        if usbtyperemove == 1:
            ret = int(system('opkg remove --force-depends enigma2-plugin-drivers-dvb-usb-dib0700'))
            ret = int(system('opkg remove --force-depends v4l-dvb-firmware'))
            ret = int(system('opkg remove --force-depends v4l-dvb-module-dib*'))
            ret = int(system('opkg remove --force-depends v4l-dvb-module-dvb-usb*'))
            ret = int(system('opkg remove --force-depends v4l-dvb-module-lgdt3305'))
            ret = int(system('opkg remove --force-depends v4l-dvb-module-mt*'))
            ret = int(system('opkg remove --force-depends v4l-dvb-module-mx*'))
            ret = int(system('opkg remove --force-depends v4l-dvb-module-s5h*'))
            ret = int(system('opkg remove --force-depends v4l-dvb-module-tuner*'))
            ret = int(system('opkg remove --force-depends v4l-dvb-module-xc*'))
            if ret != 0:
                self.session.open(MessageBox, _('opkg remove error'), MessageBox.TYPE_ERROR, 5)
            ret = int(system('/usr/sbin/update-modules'))
            if ret != 0:
                self.session.open(MessageBox, _('update-modules error'), MessageBox.TYPE_ERROR, 5)
                return
        config.plugins.USBTunerSetup.save()
        self.session.open(MessageBox, _('done with no errors, please restart'), MessageBox.TYPE_INFO)


class PEKernelModShow(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self.list = []
        self['list'] = List(self.list)
        self['list'].onSelectionChanged.append(self.schanged)
        self['statuslab'] = Label('')
        self.updateList()
        self['actions'] = ActionMap(['WizardActions'], {'ok': self.close,
         'back': self.close})
        self.onLayoutFinish.append(self.refr_sel)

    def refr_sel(self):
        self['list'].index = 1
        self['list'].index = 0

    def updateList(self):
        rc = system('lsmod > /tmp/extramodules.tmp')
        strview = ''
        if fileExists('/tmp/extramodules.tmp'):
            f = open('/tmp/extramodules.tmp', 'r')
            for line in f.readlines():
                parts = line.strip().split()
                if parts[0] == 'Module':
                    continue
                res = (parts[0], line)
                self.list.append(res)

            f.close()
            remove('/tmp/extramodules.tmp')
            self['list'].list = self.list

    def schanged(self):
        mysel = self['list'].getCurrent()
        if mysel:
            mytext = mysel[1]
            parts = mytext.split()
            size = parts[1]
            pos = len(parts[0]) + len(parts[1])
            used = mytext[pos:]
            mytext = 'Module size: ' + size + ' bytes\n' + 'Module used by: ' + used
            self['statuslab'].setText(mytext)


class PEHdd(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self['infotext'] = ScrollLabel()
        self['lab1'] = Label(_('Status:'))
        self['labstop'] = Label(_('Standby'))
        self['labrun'] = Label(_('Running'))
        self['key_red'] = Label(_('Standby Now'))
        self['key_green'] = Label(_('Set Acoustic'))
        self['key_yellow'] = Label(_('Set Standby'))
        self.cur_state = False
        self['actions'] = ActionMap(['WizardActions', 'ColorActions', 'DirectionActions'], {'back': self.close,
         'up': self['infotext'].pageUp,
         'left': self['infotext'].pageUp,
         'down': self['infotext'].pageDown,
         'right': self['infotext'].pageDown,
         'red': self.setStand,
         'green': self.setAcu,
         'yellow': self.setSsec})
        self.hddloc = ''
        if fileExists('/proc/mounts'):
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if line.find('/hdd') != -1:
                    self.hddloc = line
                    pos = self.hddloc.find(' ')
                    self.hddloc = self.hddloc[0:pos]
                    self.hddloc = self.hddloc.strip()
                    self.hddloc = self.hddloc.replace('part1', 'disc')

            f.close()
        self.onLayoutFinish.append(self.updateHdd)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('Harddisk Settings Setup'))

    def myclose(self):
        self.activityTimer.stop()
        del self.activityTimer
        mybox = self.session.openWithCallback(self.domyclose, MessageBox, _('Sorry, no Hard Disk found.'), type=MessageBox.TYPE_INFO)
        mybox.setTitle('Info')

    def domyclose(self, ret):
        self.close()

    def updateHdd(self):
        if self.hddloc == '':
            self.activityTimer = eTimer()
            self.activityTimer.timeout.get().append(self.myclose)
            self.activityTimer.start(100, True)
        else:
            self['labstop'].hide()
            self['labrun'].hide()
            cmd = 'hdparm -C ' + self.hddloc
            rc = system('hdparm -C ' + self.hddloc)
            rc = system(cmd + '> /tmp/hdpar.tmp')
            strview = ''
            procf = '/sys/block/sda/device/model'
            procf1 = '/sys/block/sda/size'
            if self.hddloc.find('host1') != -1:
                procf = '/proc/ide/hdc/'
            myfile = procf
            if fileExists(myfile):
                f = open(myfile, 'r')
                line = f.readline()
                f.close()
                strview += _('Hard Disk Model: \t') + line
            myfile = procf1
            if fileExists(myfile):
                f = open(myfile, 'r')
                line = f.readline()
                f.close()
                cap = int(line)
                cap = cap / 1000 * 512 / 1000
                cap = '%d.%03d GB' % (cap / 1024, cap % 1024)
                strview += _('Disk Size: \t\t') + cap + '\n'
            stat = statvfs('/media/hdd')
            free = stat.f_bfree / 1000 * stat.f_bsize / 1000
            free = '%d.%03d GB' % (free / 1024, free % 1024)
            strview += _('Available Space: \t') + free + '\n'
            mysett = self.getHconf()
            cvalue1 = config.usage.hdd_standby.value
            if cvalue1 > '60':
                cvalue = int(cvalue1) / 60
                mystand = str(cvalue)
                strview += _('Standby:\t\t') + mystand + _(' Min\n')
            else:
                cvalue = int(cvalue1)
                if cvalue >= 60:
                    cvalue2 = cvalue / 60
                    mystand = str(cvalue2)
                    strview += _('Standby:\t\t') + mystand + _(' Min\n')
                else:
                    mystand = str(cvalue)
                    strview += _('Standby:\t\t') + mystand + _(' Seconds\n')
            self.cur_state = False
            check = False
            if fileExists('/tmp/hdpar.tmp'):
                f = open('/tmp/hdpar.tmp', 'r')
                for line in f.readlines():
                    if line.find('active') != -1:
                        check = True
                        self.cur_state = True

                f.close()
                remove('/tmp/hdpar.tmp')
            if check == False:
                self['labstop'].show()
            else:
                self['labrun'].show()
            self['infotext'].setText(strview)

    def checkhdparm(self):
        self['labstop'].hide()
        self['labrun'].hide()
        cmd = 'hdparm -C ' + self.hddloc + '> /tmp/hdpar.tmp'
        rc = system(cmd)
        self.cur_state = False
        check = False
        if fileExists('/tmp/hdpar.tmp'):
            f = open('/tmp/hdpar.tmp', 'r')
            for line in f.readlines():
                if line.find('active') != -1:
                    check = True
                    self.cur_state = True

            f.close()
            remove('/tmp/hdpar.tmp')
        if check == False:
            self['labstop'].show()
        else:
            self['labrun'].show()

    def setStand(self):
        if self.cur_state == True:
            cmd = 'hdparm -y ' + self.hddloc
            rc = system(cmd)
            self.checkhdparm()
        else:
            mybox = self.session.open(MessageBox, _('Hard Disk is already sleeping'), MessageBox.TYPE_INFO)
            mybox.setTitle('Info')

    def setAcu(self):
        mysett = self.getHconf()
        curvalue = mysett[1]
        self.session.openWithCallback(self.SaveAcu, InputBox, title=_('Range from (0-254), 128: quiet, 254: fast:'), windowTitle=_('Hard Disk Setup'), text=curvalue, type=2)

    def SaveAcu(self, noise):
        if noise:
            mysett = self.getHconf()
            seconds = mysett[0]
            mylist = [seconds, noise]
            self.SaveHconf(mylist)

    def setSsec(self):
        self.session.openWithCallback(self.updateHdd, Setup, 'harddisk')

    def SaveSsec(self, seconds):
        if seconds:
            mysett = self.getHconf()
            noise = mysett[1]
            sec = int(seconds) * 60 / 5
            seconds = str(sec)
            mylist = [seconds, noise]
            self.SaveHconf(mylist)

    def SaveHconf(self, mylist):
        seconds = mylist[0]
        noise = mylist[1]
        out = open('/etc/init.d/hdparm', 'w')
        strview = 'hdparm -M' + noise + ' ' + self.hddloc + '\n'
        out.write(strview)
        out.close()
        system('chmod 0755 /etc/init.d/hdparm')
        try:
            symlink('/etc/init.d/hdparm', '/etc/rcS.d/S61hdparm')
        except OSError:
            print '[PEPanel] symlink already exists. do nothing.'

        cmd = 'hdparm -M' + noise + ' ' + self.hddloc
        rc = system(cmd)
        if rc == 0:
            mybox = self.session.open(MessageBox, _('New Acoustic Settings activated sucessfully'), MessageBox.TYPE_INFO)
        else:
            mybox = self.session.open(MessageBox, _('Setting Acoustic not supported by your Hard Disk.'), MessageBox.TYPE_ERROR)
        mybox.setTitle('Info')
        self.updateHdd()

    def getHconf(self):
        noise = '128'
        seconds = '120'
        if fileExists('/etc/init.d/hdparm'):
            f = open('/etc/init.d/hdparm', 'r')
            for line in f.readlines():
                if line.find('-S') != -1:
                    parts = line.strip().split(' ')
                    seconds = parts[1]
                    seconds = seconds.replace('-S', '')
                if line.find('-M') != -1:
                    parts = line.strip().split(' ')
                    noise = parts[1]
                    noise = noise.replace('-M', '')

            f.close()
        return [seconds, noise]


class PEDVBNTPTime(Screen):

    def __init__(self, session, args = 0):
        self.skin_path = plugin_path
        self.session = session
        Screen.__init__(self, session)
        NetworkConnectionAvailable = None
        self.menu = args
        self.list = []
        self.list.append(('PEDVBNTPTimecheck', _('Check DVB Time'), _('This option check manually if there is a time difference between current system time and the transponder time.')))
        self.list.append(('PEDVBNTPTimeset', _('Set DVB Time'), _('This option set the time from current transponder as system time.')))
        self.list.append(('PEDVBNTPTimesetforced', _('Forced set DVB Time'), _('Setting DVB Time forced is only needed if check shows more then 30 min. time difference.\nATTENTION: With forced option make a Enigma 2 restart at the finish !')))
        self.list.append(('changetime', _('Set system time manually'), _('This option set manually the system time by input with the remote control.')))
        self.list.append(('checkntptime', _('Check and set with NTP-Server'), _('Comparing the system time with a central time server and set the new system time.')))
        self['menu'] = List(self.list)
        self['key_red'] = Label(showmessage)
        self['key_green'] = Label(ntpautostart)
        self['key_yellow'] = Label(tdtautostart)
        self['key_blue'] = Label(transponderupdate)
        self['actions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'ok': self.go,
         'exit': self.keyCancel,
         'back': self.keyCancel,
         'red': self.switchshowmessage,
         'green': self.autostartntpchecknetwork,
         'yellow': self.switchtdt,
         'blue': self.onoffautotrans}, -1)
        self.onShown.append(self.updateSettings)
        self.onLayoutFinish.append(self.layoutFinished)
        self.onShown.append(self.setWindowTitle)

    def updateSettings(self):
        showmessage_state = showmessage
        ntpautostart_state = ntpautostart
        tdtautostart_state = tdtautostart
        transponderupdate_state = transponderupdate
        if config.plugins.dvbntptime.showntpmessage.value:
            showmessage_state += _('On')
        else:
            showmessage_state += _('Off')
        if config.plugins.dvbntptime.ntpautocheck.value:
            ntpautostart_state += _('On')
        else:
            ntpautostart_state += _('Off')
        if config.plugins.dvbntptime.tdtautocheck.value:
            tdtautostart_state += _('On')
        else:
            tdtautostart_state += _('Off')
        if config.misc.useTransponderTime.value:
            transponderupdate_state += _('On')
        else:
            transponderupdate_state += _('Off')
        self['key_red'].setText(showmessage_state)
        self['key_green'].setText(ntpautostart_state)
        self['key_yellow'].setText(tdtautostart_state)
        self['key_blue'].setText(transponderupdate_state)

    def layoutFinished(self):
        idx = 0
        self['menu'].index = idx

    def setWindowTitle(self):
        self.setTitle(_('DVB NTP Time menu'))

    def go(self):
        current = self['menu'].getCurrent()
        if current:
            currentEntry = current[0]
            if self.menu == 0:
                if currentEntry == 'PEDVBNTPTimecheck':
                    self.session.open(Console, _('Checking DVB Time...'), ['dvbdate --print'])
                elif currentEntry == 'PEDVBNTPTimeset':
                    if config.misc.useTransponderTime.value == True:
                        self.session.open(MessageBox, _('Set DVB Time not useful,switch off Enigma 2 Timeupdate first !'), MessageBox.TYPE_INFO, timeout=10)
                    elif config.plugins.dvbntptime.ntpautocheck.value:
                        self.session.open(MessageBox, _('NTP-Server autostart is enabled,please switch off first !'), MessageBox.TYPE_INFO, timeout=10)
                    else:
                        self.DoSetPEDVBNTPTime(True)
                elif currentEntry == 'PEDVBNTPTimesetforced':
                    if config.plugins.dvbntptime.ntpautocheck.value:
                        self.session.open(MessageBox, _('NTP-Server autostart is enabled,please switch off first !'), MessageBox.TYPE_INFO, timeout=10)
                    elif config.misc.useTransponderTime.value == True:
                        self.session.open(MessageBox, _('Forced set DVB Time not useful,switch off Enigma 2 Timeupdate first !'), MessageBox.TYPE_INFO, timeout=10)
                    else:
                        self.DoSetPEDVBNTPTimeforce(True)
                elif currentEntry == 'checkntptime':
                    if config.misc.useTransponderTime.value == True:
                        self.session.open(MessageBox, _('Check and set with NTP-Server not useful,switch off Enigma 2 Timeupdate first !'), MessageBox.TYPE_INFO, timeout=10)
                    else:
                        self.startnetworkcheck()
                elif currentEntry == 'changetime':
                    if config.plugins.dvbntptime.ntpautocheck.value:
                        self.session.open(MessageBox, _('NTP-Server autostart is enabled,please switch off first !'), MessageBox.TYPE_INFO, timeout=10)
                    elif config.misc.useTransponderTime.value == True:
                        self.session.open(MessageBox, _('Set system time manually not useful,switch off Enigma 2 Timeupdate first !'), MessageBox.TYPE_INFO, timeout=10)
                    else:
                        ChangeTimeWizzard(self.session)

    def autostartntpchecknetwork(self, callback = None):
        self.session.open(MessageBox, _('Check Network status.\nPlease wait...'), MessageBox.TYPE_INFO, timeout=10)
        if callback is not None:
            self.NotifierCallback = callback
        iNetwork.checkNetworkState(self.checkNetworkCBautontp)

    def checkNetworkCBautontp(self, data):
        if data is not None:
            if data <= 2:
                PEDVBNTPTime.NetworkConnectionAvailable = True
                self.session.openWithCallback(self.autostartntpcheck, MessageBox, _('Restart Enigma 2 for automatic NTP-Server check on startup (on/off) ?'), MessageBox.TYPE_YESNO)
            else:
                self.session.open(MessageBox, _('Change NTP-Server autostart not not possible:\n\nNetwork status: Unreachable !'), MessageBox.TYPE_ERROR)

    def autostartntpcheck(self, answer):
        if answer is False:
            self.skipPEDVBNTPTimeautostart(_('Reason: Abort by User !'))
        if answer is True:
            if config.plugins.dvbntptime.ntpautocheck.value:
                config.plugins.dvbntptime.showntpmessage.setValue(False)
                config.plugins.dvbntptime.ntpautocheck.setValue(False)
                config.misc.useTransponderTime.setValue(True)
            else:
                config.plugins.dvbntptime.ntpautocheck.setValue(True)
                config.plugins.dvbntptime.showntpmessage.setValue(True)
                config.plugins.dvbntptime.tdtautocheck.setValue(False)
                config.misc.useTransponderTime.setValue(False)
            self.updateSettings()
            config.plugins.dvbntptime.ntpautocheck.save()
            config.plugins.dvbntptime.showntpmessage.save()
            config.plugins.dvbntptime.tdtautocheck.save()
            config.misc.useTransponderTime.save()
            self.callRestart(True)

    def onoffautotrans(self):
        self.session.openWithCallback(self.autotransponder, MessageBox, _('Restart Enigma 2 to switch on/off Enigma 2 Timeupdate on startup ?\nATTENTION: When you switch off,all automatic time updates are disabled !!!'), MessageBox.TYPE_YESNO)

    def autotransponder(self, answer):
        if answer is False:
            self.skipPEDVBNTPTimeautostart(_('Reason: Abort by User !'))
        if answer is True:
            if config.misc.useTransponderTime.value:
                config.misc.useTransponderTime.setValue(False)
            else:
                config.misc.useTransponderTime.setValue(True)
                config.plugins.dvbntptime.tdtautocheck.setValue(False)
                config.plugins.dvbntptime.ntpautocheck.setValue(False)
                config.plugins.dvbntptime.showntpmessage.setValue(False)
            self.updateSettings()
            config.misc.useTransponderTime.save()
            config.plugins.dvbntptime.tdtautocheck.save()
            config.plugins.dvbntptime.ntpautocheck.save()
            config.plugins.dvbntptime.showntpmessage.save()
            self.callRestartTransponder(True)

    def switchtdt(self):
        self.session.openWithCallback(self.autostarttdtcheck, MessageBox, _('Restart Enigma 2 to display DVB Time check results on startup (on/off) ?'), MessageBox.TYPE_YESNO)

    def autostarttdtcheck(self, answer):
        if answer is False:
            self.skipPEDVBNTPTimeautostart(_('Reason: Abort by User !'))
        if answer is True:
            if config.plugins.dvbntptime.tdtautocheck.value:
                config.plugins.dvbntptime.tdtautocheck.setValue(False)
                config.misc.useTransponderTime.setValue(True)
            else:
                config.plugins.dvbntptime.tdtautocheck.setValue(True)
                config.plugins.dvbntptime.ntpautocheck.setValue(False)
                config.plugins.dvbntptime.showntpmessage.setValue(False)
                config.misc.useTransponderTime.setValue(False)
            self.updateSettings()
            config.plugins.dvbntptime.tdtautocheck.save()
            config.plugins.dvbntptime.ntpautocheck.save()
            config.plugins.dvbntptime.showntpmessage.save()
            config.misc.useTransponderTime.save()
            self.callRestart(True)

    def switchMainMenu(self):
        self.session.openWithCallback(self.setMainMenu, MessageBox, _('Restarting Enigma 2 to switch on/off display\nthe DVB Time in the Mainmenu ?'), MessageBox.TYPE_YESNO)

    def setMainMenu(self, answer):
        if answer is False:
            self.skipPEDVBNTPTimeautostart(_('Reason: Abort by User !'))
        if answer is True:
            if config.plugins.dvbntptime.enablemainmenu.value:
                config.plugins.dvbntptime.enablemainmenu.setValue(False)
            else:
                config.plugins.dvbntptime.enablemainmenu.setValue(True)
            self.updateSettings()
            config.plugins.dvbntptime.enablemainmenu.save()
            self.callRestart(True)

    def switchshowmessage(self):
        if config.plugins.dvbntptime.ntpautocheck.value == False:
            self.session.open(MessageBox, _('That makes no sense when turned off the auto start from the NTP-Server.\nPlease switch on the autostart first !'), MessageBox.TYPE_INFO, timeout=10)
        else:
            self.session.openWithCallback(self.onoffshowmessage, MessageBox, _('Restarting Enigma 2 to switch on/off\nthe NTP message on startup ?'), MessageBox.TYPE_YESNO)

    def onoffshowmessage(self, answer):
        if answer is False:
            self.skipPEDVBNTPTimeautostart(_('Reason: Abort by User !'))
        if answer is True:
            if config.plugins.dvbntptime.showntpmessage.value:
                config.plugins.dvbntptime.showntpmessage.setValue(False)
            else:
                config.plugins.dvbntptime.showntpmessage.setValue(True)
            self.updateSettings()
            config.plugins.dvbntptime.showntpmessage.save()
            self.callRestart(True)

    def callRestart(self, answer):
        if answer is None:
            self.skipPEDVBNTPTimeautostart(_('Reason: Answer is none'))
        if answer is False:
            self.skipPEDVBNTPTimeautostart(_('Reason: Abort by User !'))
        if answer is True:
            quitMainloop(3)

    def callRestartTransponder(self, answer):
        if answer is None:
            self.skipPEDVBNTPTimeautostart(_('Reason: Answer is none'))
        if answer is False:
            self.skipPEDVBNTPTimeautostart(_('Reason: Abort by User !'))
        if answer is True:
            quitMainloop(3)

    def skipPEDVBNTPTimeautostart(self, reason):
        self.session.open(MessageBox, _('DVB Time setting aborted:\n\n%s') % reason, MessageBox.TYPE_ERROR)

    def startnetworkcheck(self, callback = None):
        if callback is not None:
            self.NotifierCallback = callback
        iNetwork.checkNetworkState(self.checkNetworkCB)

    def checkNetworkCB(self, data):
        if data is not None:
            if data <= 2:
                PEDVBNTPTime.NetworkConnectionAvailable = True
                self.container = eConsoleAppContainer()
                self.container.appClosed.append(self.finishedntp)
                self.container.execute('ntpdate de.pool.ntp.org tick.fh-augsburg.de time2.one4vision.de')
            else:
                self.session.open(MessageBox, _('NTP check not not possible:\n\nNetwork status: Unreachable !'), MessageBox.TYPE_ERROR)

    def finishedntp(self, retval):
        timenow = strftime('%Y:%m:%d %H:%M', localtime())
        self.session.open(MessageBox, _('NTP-Server check and system time update\nto %s successfully done.') % timenow, MessageBox.TYPE_INFO, timeout=10)

    def DoSetPEDVBNTPTime(self, answer):
        self.container = eConsoleAppContainer()
        self.container.execute('dvbdate --set')
        self.session.openWithCallback(self.finished, MessageBox, _('DVB Time update running.\nPlease wait...'), MessageBox.TYPE_INFO, timeout=10)

    def finished(self, answer):
        if answer is None:
            self.skipPEDVBNTPTime(_('Reason: Answer is none'))
        if answer is False:
            self.skipPEDVBNTPTime(_('Reason: Abort by User !'))
        if answer is True:
            timenow = strftime('%Y:%m:%d %H:%M', localtime())
            self.session.open(MessageBox, _('DVB Time updating to %s\nsuccessfully done.') % timenow, MessageBox.TYPE_INFO, timeout=10)

    def DoSetPEDVBNTPTimeforce(self, answer):
        if answer is None:
            self.skipPEDVBNTPTime(_('Reason: Answer is none'))
        if answer is False:
            self.skipPEDVBNTPTime(_('Reason: Abort by User !'))
        if answer is True:
            self.session.openWithCallback(self.forcefinished, MessageBox, _('Setting DVB Time with forced option.\nWhen finished Enigma 2 restarts automatically !\nPlease wait...'), MessageBox.TYPE_INFO, timeout=30)
            self.container = eConsoleAppContainer()
            self.container.execute('dvbdate --set --force')

    def forcefinished(self, answer):
        if answer is None:
            self.skipPEDVBNTPTime(_('Reason: Answer is none'))
        if answer is False:
            self.skipPEDVBNTPTime(_('Reason: Abort by User !'))
        if answer is True:
            quitMainloop(3)

    def skipPEDVBNTPTime(self, reason):
        self.session.open(MessageBox, _('DVB Time setting aborted:\n\n%s') % reason, MessageBox.TYPE_ERROR)

    def keyCancel(self):
        self.close(None)


class NTPStartup(Screen):
    skin = '\n        <screen position="center,center" size="400,300" title=" " >\n        </screen>'

    def __init__(self, session):
        self.skin = NTPStartup.skin
        self.session = session
        Screen.__init__(self, session)
        NetworkConnectionAvailable = None
        self.TimerPEDVBNTPTimeStartup = eTimer()
        self.TimerPEDVBNTPTimeStartup.stop()
        self.TimerPEDVBNTPTimeStartup.timeout.get().append(self.startnetworkcheckntp)
        self.TimerPEDVBNTPTimeStartup.start(3000, True)

    def startnetworkcheckntp(self, callback = None):
        if callback is not None:
            self.NotifierCallback = callback
        iNetwork.checkNetworkState(self.checkNetworkCBntp)

    def checkNetworkCBntp(self, data):
        if data is not None:
            if data <= 2:
                PEDVBNTPTime.NetworkConnectionAvailable = True
                self.TimerPEDVBNTPTimeStartup.stop()
                self.container = eConsoleAppContainer()
                self.container.appClosed.append(self.finishedntpauto)
                self.container.execute('ntpdate de.pool.ntp.org tick.fh-augsburg.de time2.one4vision.de')
            else:
                self.session.open(MessageBox, _('NTP check not not possible:\n\nNetwork status: Unreachable !'), MessageBox.TYPE_ERROR)

    def finishedntpauto(self, retval):
        if config.plugins.dvbntptime.showntpmessage.value:
            timenow = strftime('%Y:%m:%d %H:%M', localtime())
            self.session.open(MessageBox, _('NTP Time check successfully.\nSystem time set to %s finished.') % timenow, MessageBox.TYPE_INFO, timeout=10)


class PEDVBNTPTimeStartup(Screen):
    skin = '\n        <screen position="center,center" size="400,300" title=" " >\n        </screen>'

    def __init__(self, session):
        self.skin = PEDVBNTPTimeStartup.skin
        self.session = session
        Screen.__init__(self, session)
        self.TimerPEDVBNTPTimeStartup = eTimer()
        self.TimerPEDVBNTPTimeStartup.stop()
        self.TimerPEDVBNTPTimeStartup.timeout.get().append(self.CheckPEDVBNTPTimeStartup)
        self.TimerPEDVBNTPTimeStartup.start(3000, True)

    def CheckPEDVBNTPTimeStartup(self):
        global dvbdateresult
        dvbdateresult = ''
        self.TimerPEDVBNTPTimeStartup.stop()
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.finished)
        self.container.dataAvail.append(self.dataAvail)
        self.container.execute('dvbdate --print')

    def finished(self, retval):
        self.session.open(MessageBox, _('DVB Time check results:\n%s') % dvbdateresult, MessageBox.TYPE_INFO, timeout=10)

    def dataAvail(self, str):
        global dvbdateresult
        dvbdateresult = str


class ChangeTimeWizzard(Screen):

    def __init__(self, session):
        self.session = session
        self.oldtime = strftime('%Y:%m:%d %H:%M', localtime())
        self.session.openWithCallback(self.askForNewTime, InputBox, windowTitle=_('Please Enter new Systemtime:'), title=_('OK will set new time and restart Enigma 2 !'), text='%s' % self.oldtime, maxSize=16, type=Input.NUMBER)

    def askForNewTime(self, newclock):
        try:
            length = len(newclock)
        except:
            length = 0

        if newclock is None:
            self.skipChangeTime(_('No new time input !'))
        elif (length == 16) is False:
            self.skipChangeTime(_('New time string too short !'))
        elif (newclock.count(' ') < 1) is True:
            self.skipChangeTime(_('Invalid format !'))
        elif (newclock.count(':') < 3) is True:
            self.skipChangeTime(_('Invalid format !'))
        else:
            full = []
            full = newclock.split(' ', 1)
            newdate = full[0]
            newtime = full[1]
            parts = []
            parts = newdate.split(':', 2)
            newyear = parts[0]
            newmonth = parts[1]
            newday = parts[2]
            parts = newtime.split(':', 1)
            newhour = parts[0]
            newmin = parts[1]
            maxmonth = 31
            if int(newmonth) == 4 or int(newmonth) == 6 or int(newmonth) == 9 or (int(newmonth) == 11) is True:
                maxmonth = 30
            elif (int(newmonth) == 2) is True:
                if (4 * int(int(newyear) / 4) == int(newyear)) is True:
                    maxmonth = 28
                else:
                    maxmonth = 27
            if int(newyear) < 2010 or int(newyear) > 2015 or (len(newyear) < 4) is True:
                self.skipChangeTime(_('Invalid year %s !') % newyear)
            elif int(newmonth) < 0 or int(newmonth) > 12 or (len(newmonth) < 2) is True:
                self.skipChangeTime(_('Invalid month %s !') % newmonth)
            elif int(newday) < 1 or int(newday) > maxmonth or (len(newday) < 2) is True:
                self.skipChangeTime(_('Invalid day %s !') % newday)
            elif int(newhour) < 0 or int(newhour) > 23 or (len(newhour) < 2) is True:
                self.skipChangeTime(_('Invalid hour %s !') % newhour)
            elif int(newmin) < 0 or int(newmin) > 59 or (len(newmin) < 2) is True:
                self.skipChangeTime(_('Invalid minute %s !') % newmin)
            else:
                self.newtime = '%s%s%s%s%s' % (newyear,
                 newmonth,
                 newday,
                 newhour,
                 newmin)
                self.session.openWithCallback(self.DoChangeTimeRestart, MessageBox, _('Enigma 2 must be restarted to set the new Systemtime ?'), MessageBox.TYPE_YESNO)

    def DoChangeTimeRestart(self, answer):
        if answer is None:
            self.skipChangeTime(_('Answer is none'))
        if answer is False:
            self.skipChangeTime(_('Enigma 2 restart abort by user !'))
        else:
            system('date %s' % self.newtime)
            quitMainloop(3)

    def skipChangeTime(self, reason):
        self.session.open(MessageBox, _('Change Systemtime was canceled:\n\n%s') % reason, MessageBox.TYPE_ERROR)


class PEOpenvpn(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self['lab1'] = Label(_('VPN Version: '))
        self['lab1a'] = Label(_('OpenVPN Panel'))
        self['lab2'] = Label(_('Startup Module:'))
        self['labactive'] = Label(_('Inactive'))
        self['lab3'] = Label(_('Current Status:'))
        self['labstop'] = Label(_('Stopped'))
        self['labrun'] = Label(_('Running'))
        self['key_red'] = Label(_('Start'))
        self['key_green'] = Label(_('Stop'))
        self['key_yellow'] = Label(_('Set Active'))
        self['key_blue'] = Label(_('Show Log'))
        self.my_vpn_active = False
        self.my_vpn_run = False
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close,
         'back': self.close,
         'red': self.restartVpn,
         'green': self.stopVpnstop,
         'yellow': self.activateVpn,
         'blue': self.Vpnshowlog})
        self.onLayoutFinish.append(self.updateVpn)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('OpenVPN Setup'))

    def activateVpn(self):
        myline = 'AUTOSTART="all"'
        mymess = _('OpenVPN Enabled. Autostart activated.')
        if self.my_vpn_active == True:
            myline = 'AUTOSTART="none"'
            mymess = 'OpenVPN disabled.'
        if fileExists('/usr/bin/openvpn_script.sh'):
            inme = open('/usr/bin/openvpn_script.sh', 'r')
            out = open('/usr/bin/openvpn_script.tmp', 'w')
            for line in inme.readlines():
                if line.find('AUTOSTART="') != -1:
                    line = myline + '\n'
                out.write(line)

            out.close()
            inme.close()
        if fileExists('/usr/bin/openvpn_script.tmp'):
            rename('/usr/bin/openvpn_script.tmp', '/usr/bin/openvpn_script.sh')
            system('chmod 0755 /usr/bin/openvpn_script.sh')
        mybox = self.session.open(MessageBox, mymess, MessageBox.TYPE_INFO)
        mybox.setTitle('Info')
        self.updateVpn()

    def restartVpn(self):
        if self.my_vpn_active == False:
            mybox = self.session.open(MessageBox, _('You have to Activate OpenVPN before to start'), MessageBox.TYPE_INFO)
            mybox.setTitle('Info')
        elif self.my_vpn_active == True:
            self.my_vpn_run == False
            rc = system('/usr/bin/openvpn_script.sh start')
            rc = system('ps')
            self.updateVpn()

    def stopVpnstop(self):
        if self.my_vpn_run == True:
            rc = system('/usr/bin/openvpn_script.sh stop')
            rc = system('ps')
            self.updateVpn()

    def Vpnshowlog(self):
        self.session.open(PEVpnLog)

    def updateVpn(self):
        rc = system('ps > /tmp/nvpn.tmp')
        self['labrun'].hide()
        self['labstop'].hide()
        self['labactive'].setText(_('Inactive'))
        self['key_yellow'].setText(_('Set Active'))
        self.my_vpn_active = False
        self.my_vpn_run = False
        if fileExists('/usr/bin/openvpn_script.sh'):
            f = open('/usr/bin/openvpn_script.sh', 'r')
            for line in f.readlines():
                if line.find('AUTOSTART="all"') != -1:
                    self['labactive'].setText(_('Active/Autostart enabled'))
                    self['key_yellow'].setText(_('Deactivate'))
                    self.my_vpn_active = True

            f.close()
        if fileExists('/tmp/nvpn.tmp'):
            f = open('/tmp/nvpn.tmp', 'r')
            for line in f.readlines():
                if line.find('/usr/sbin/openvpn') != -1:
                    self.my_vpn_run = True

            f.close()
            remove('/tmp/nvpn.tmp')
        if self.my_vpn_run == True:
            self['labstop'].hide()
            self['labrun'].show()
            self['key_red'].setText(_('Restart'))
        else:
            self['labrun'].hide()
            self['labstop'].show()


class PEVpnLog(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self['infotext'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close,
         'back': self.close,
         'up': self['infotext'].pageUp,
         'down': self['infotext'].pageDown})
        strview = ''
        if not fileExists('/etc/openvpn/openvpn.log'):
            system('mkdir -p /etc/openvpn')
            fp = file('/etc/openvpn/openvpn.log', 'w')
            fp.close()
        rc = system('tail /etc/openvpn/openvpn.log > /etc/openvpn/tmp.log')
        if fileExists('/etc/openvpn/tmp.log'):
            f = open('/etc/openvpn/tmp.log', 'r')
            for line in f.readlines():
                strview += line

            f.close()
            remove('/etc/openvpn/tmp.log')
        self['infotext'].setText(strview)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('OpenVPN Log'))


class PECronMang(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self['key_red'] = Label(_('Add'))
        self['key_yellow'] = Label(_('Delete'))
        self.list = []
        self['list'] = List(self.list)
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close,
         'back': self.close,
         'red': self.addtocron,
         'yellow': self.delcron})
        self.updateList()
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('Cronmanager Setup'))

    def addtocron(self):
        self.session.openWithCallback(self.updateList, PESetupCronConf)

    def updateList(self):
        self.list = []
        if fileExists('/etc/cron/crontabs/root'):
            f = open('/etc/cron/crontabs/root', 'r')
            for line in f.readlines():
                parts = line.strip().split()
                line2 = _('Time: ') + parts[1] + ':' + parts[0] + '\t' + _('Command: ') + line[line.rfind('*') + 1:]
                res = (line2, line)
                self.list.append(res)

            f.close()
        self['list'].list = self.list

    def delcron(self):
        mysel = self['list'].getCurrent()
        if mysel:
            myline = mysel[1]
            out = open('/etc/cron/crontabs/root.helper', 'w')
            f = open('/etc/cron/crontabs/root', 'r')
            for line in f.readlines():
                if line != myline:
                    out.write(line)

            f.close()
            out.close()
            rc = system('crontab /etc/cron/crontabs/root.helper  -c /etc/cron/crontabs/')
            rc = system('/etc/init.d/busybox-cron stop')
            rc = system('/etc/init.d/busybox-cron start')
            self.updateList()


class PESetupCronConf(Screen, ConfigListScreen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['key_red'] = Label(_('Save'))
        self['key_green'] = Label(_('virt. Keyboard'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.checkentry,
         'back': self.close,
         'green': self.vkeyb})
        self.updateList()
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('Add Cronjob'))

    def updateList(self):
        self.cmdtime = NoSave(ConfigClock(default=0))
        self.defaultcommandlist = []
        self.defaultcommandlist.append(('None', 'None'))
        self.defaultcommandlist.append(('wget -q -O - http://127.0.0.1/web/powerstate?newstate=0', _('standby')))
        self.defaultcommandlist.append(('wget -q -O - http://127.0.0.1/web/powerstate?newstate=1', _('shutdown')))
        self.defaultcommandlist.append(('wget -q -O - http://127.0.0.1/web/powerstate?newstate=2', _('reboot')))
        self.defaultcommandlist.append(('wget -q -O - http://127.0.0.1/web/powerstate?newstate=3', _('restart enigma2')))
        self.defaultcommandlist.append(('wget -q -O - http://127.0.0.1/web/remotecontrol?command=116', _('wakeup/switch from/to standby')))
        if fileExists(resolveFilename(SCOPE_PLUGINS, '/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/plugin.pyo')):
            self.defaultcommandlist.append(('/etc/init.d/softcam restart', _('restart softcam')))
        self.default_command = NoSave(ConfigSelection(default='None', choices=self.defaultcommandlist))
        self.user_command = NoSave(ConfigText(fixed_size=False))
        self.cmdtime.value = mytmpt = [0, 0]
        self.default_command.value = 'None'
        self.user_command.value = 'None'
        res = getConfigListEntry(_('Time to execute command or script'), self.cmdtime)
        self.list.append(res)
        res = getConfigListEntry(_('Predefined Command to execute'), self.default_command)
        self.list.append(res)
        res = getConfigListEntry(_('Custom Command'), self.user_command)
        self.list.append(res)
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def vkeyb(self):
        sel = self['config'].getCurrent()
        if sel:
            self.vkvar = sel[0]
            value = 'xmeo'
            if self.vkvar == _('Custom Command'):
                value = self.user_command.value
                if value == 'None':
                    value = ''
            if value != 'xmeo':
                self.session.openWithCallback(self.UpdateAgain, VirtualKeyBoard, title=self.vkvar, text=value)
            else:
                self.session.open(MessageBox, _('Please use Virtual Keyboard for text rows only (e. g. custom command)'), MessageBox.TYPE_INFO)

    def UpdateAgain(self, newt):
        self.list = []
        if newt is None or newt == '':
            newt = 'None'
        self.user_command.value = newt
        res = getConfigListEntry(_('Time to execute command or script'), self.cmdtime)
        self.list.append(res)
        res = getConfigListEntry(_('Predefined Command to execute'), self.default_command)
        self.list.append(res)
        res = getConfigListEntry(_('Custom Command'), self.user_command)
        self.list.append(res)
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def checkentry(self):
        msg = ''
        if self.user_command.value == 'None':
            self.user_command.value = ''
        if self.default_command.value == 'None' and self.user_command.value == '':
            msg = _('You must set at least one Command')
        if self.default_command.value != 'None' and self.user_command.value != '':
            msg = _('Entering a Custom command you have to set Predefined command: None ')
        if msg:
            self.session.open(MessageBox, msg, MessageBox.TYPE_ERROR)
        else:
            self.saveMycron()

    def saveMycron(self):
        hour = '%02d' % self.cmdtime.value[0]
        minutes = '%02d' % self.cmdtime.value[1]
        if self.default_command.value != 'None':
            command = self.default_command.value
        else:
            command = self.user_command.value
        newcron = minutes + ' ' + hour + ' * * * ' + command.strip() + '\n'
        try:
            if not fileExists('/etc/cron/crontabs/root.helper'):
                system('mkdir -p /etc/cron/crontabs')
                fp = file('/etc/cron/crontabs/root.helper', 'w')
                fp.close()
        except OSError:
            self.session.open(MessageBox, _('Could not create the Roothelper Directory or File.'), MessageBox.TYPE_ERROR, 5)

        out = open('/etc/cron/crontabs/root.helper', 'w')
        try:
            if not fileExists('/etc/cron/crontabs/root'):
                system('mkdir -p /etc/cron/crontabs')
                fp = file('/etc/cron/crontabs/root', 'w')
                fp.close()
        except OSError:
            self.session.open(MessageBox, _('Could not create the Root Directory or File.'), MessageBox.TYPE_ERROR, 5)

        if fileExists('/etc/cron/crontabs/root'):
            f = open('/etc/cron/crontabs/root', 'r')
            for line in f.readlines():
                out.write(line)

            f.close()
        out.write(newcron)
        out.close()
        rc = system('crontab /etc/cron/crontabs/root.helper  -c /etc/cron/crontabs/')
        rc = system('/etc/init.d/busybox-cron stop')
        rc = system('/etc/init.d/busybox-cron start')
        self.close()


class PEDownPanel(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self.flist = []
        idx = 0
        pkgs = listdir('/tmp')
        for fil in pkgs:
            if fil.find('.tar.gz') != -1 or fil.find('.tgz') != -1:
                res = (fil, idx)
                self.flist.append(res)
                idx = idx + 1

        self['list'] = List(self.flist)
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'back': self.close})

    def KeyOk(self):
        self.sel = self['list'].getCurrent()
        if self.sel:
            self.sel = self.sel[0]
            message = 'Do you want to install the Addon:\n ' + self.sel + ' ?'
            ybox = self.session.openWithCallback(self.installadd2, MessageBox, message, MessageBox.TYPE_YESNO)
            ybox.setTitle('Installation Confirm')

    def installadd2(self, answer):
        if answer is True:
            dest = '/tmp/' + self.sel
            mydir = getcwd()
            chdir('/')
            cmd = 'tar -xzf ' + dest
            rc = system(cmd)
            chdir(mydir)
            cmd = 'rm -f ' + dest
            rc = system(cmd)
            if fileExists('/usr/sbin/nab_e2_restart.sh'):
                rc = system('rm -f /usr/sbin/nab_e2_restart.sh')
                mybox = self.session.openWithCallback(self.hrestEn, MessageBox, 'Enigma2 will be now hard restarted to complete package installation.\nPress ok to continue', MessageBox.TYPE_INFO)
                mybox.setTitle('Info')
            else:
                mybox = self.session.open(MessageBox, 'Addon Sucessfully Installed.', MessageBox.TYPE_INFO)
                mybox.setTitle('Info')
                self.close()

    def hrestEn(self, answer):
        rc = system('killall -9 enigma2')


class PEInfo(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self['mem_labels'] = Label(_('\nTotal:\nFree:\nUsed:\nUsed(%):'))
        self['ram'] = Label()
        self['root'] = Label()
        self['swap'] = Label()
        self['mem_tot'] = Label()
        self['membar'] = ProgressBar()
        self['rootbar'] = ProgressBar()
        self['swapbar'] = ProgressBar()
        self['memtotalbar'] = ProgressBar()
        self['space_labels'] = Label(_('\nTotal:\nFree:\nUsed:\nUsed(%):'))
        self['hdd'] = Label()
        self['usb'] = Label()
        self['usb1'] = Label()
        self['usb2'] = Label()
        self['hddbar'] = ProgressBar()
        self['usbbar'] = ProgressBar()
        self['usb1bar'] = ProgressBar()
        self['usb2bar'] = ProgressBar()
        self['HDDCPULabels'] = Label(_('Sensor:\nValue:'))
        self['usb3'] = Label()
        self['hddtemperature'] = Label(_('HDD Temp:\n....'))
        self['cpusys'] = Label()
        self['cpuusr'] = Label()
        self['usb3bar'] = ProgressBar()
        self['hddtempbar'] = ProgressBar()
        self['cpusysbar'] = ProgressBar()
        self['cpuusrbar'] = ProgressBar()
        self['ftp_on'] = Pixmap()
        self['telnet_on'] = Pixmap()
        self['smb_on'] = Pixmap()
        self['nfs_on'] = Pixmap()
        self['ssh_on'] = Pixmap()
        self['ftp_on'].hide()
        self['telnet_on'].hide()
        self['smb_on'].hide()
        self['nfs_on'].hide()
        self['ssh_on'].hide()
        self['uptime'] = Pixmap()
        self['utday'] = Label()
        self['uthour'] = Label()
        self['utmin'] = Label()
        self['utsec'] = Label()
        self['utdayval'] = Label()
        self['uthourval'] = Label()
        self['utminval'] = Label()
        self['utsecval'] = Label()
        self['utday'].hide()
        self['uthour'].hide()
        self['utmin'].hide()
        self['utsec'].hide()
        self['utdayval'].hide()
        self['uthourval'].hide()
        self['utminval'].hide()
        self['utsecval'].hide()
        self['kernelversion'] = Label('N/A')
        self['key1'] = Pixmap()
        self['key2'] = Pixmap()
        self['key3'] = Pixmap()
        self['key4'] = Pixmap()
        self['key5'] = Pixmap()
        self['key6'] = Pixmap()
        self['key_redtxt'] = Label(_('Refresh'))
        self['key_greentxt'] = Label(_('HDD Temp'))
        self['key_yellowtxt'] = Label(_('Memory'))
        self['key_bluetxt'] = Label(_('CPU'))
        self['video'] = StaticText(_('Video'))
        self['audio'] = StaticText(_('Audio'))
        self['min'] = StaticText(_('Min'))
        self['max'] = StaticText(_('Max'))
        self['cur'] = StaticText(_('Current'))
        self['avg'] = StaticText(_('Average'))
        self['vmin'] = Label('')
        self['vmax'] = Label('')
        self['vavg'] = Label('')
        self['vcur'] = Label('')
        self['amin'] = Label('')
        self['amax'] = Label('')
        self['aavg'] = Label('')
        self['acur'] = Label('')
        self['actions'] = ActionMap(['OkCancelActions',
         'WizardActions',
         'ColorActions',
         'NumberActions'], {'ok': self.KeyOk,
         'cancel': self.keyCancel,
         'back': self.KeyOk,
         'red': self.KeyRed2,
         'green': self.KeyGreen,
         'yellow': self.KeyYellow2,
         'blue': self.KeyBlue2,
         '1': self.KeyOne,
         '2': self.KeyTwo,
         '3': self.KeyThree,
         '4': self.KeyFour,
         '5': self.KeyFive,
         '6': self.KeySix})
        self.onLayoutFinish.append(self.updateList)

    def startShow(self):
        self.smallmontxt = ''
        self.activityTimer.start(10)

    def updateList(self):
        self.getUptime()
        self.getMemInfo()
        self.getSpaceInfo()
        self.getServicesInfo()
        self.getCPUInfo()
        self.getKernelVersion()

    def moniShow(self):
        self.x = 644
        self.y = 350
        self.w = 0
        self.h = 0
        self.moniTimer.start(10)

    def moveON(self):
        self.moniTimer.stop()
        self['moni'].instance.move(ePoint(int(self.x), int(self.y)))
        self['moni'].instance.resize(eSize(int(self.w), int(self.h)))
        if self.x > 364:
            self.x -= 280 / 20
        if self.y > 80:
            self.y -= 270 / 20
        if self.h < 560:
            self.h += 560 / 20
        if self.w < 560:
            self.w += 560 / 20
            self.moniTimer.start(80)
        else:
            self['monipix'].show()
            self['moni2'].show()
            self.moni_state = 1

    def KeyRed2(self):
        self.refresh()

    def KeyOk(self):
        self.close()

    def getCPUInfo(self):
        system('/usr/lib/enigma2/python/Plugins/SystemPlugins/PEPanel/cpu.sh')
        if fileExists('/tmp/cpuinfo.tmp'):
            f = open('/tmp/cpuinfo.tmp', 'r')
        line = f.readlines()
        for lines in line:
            parts = lines.strip().split()
            if parts[0] == 'CPU:':
                usr = parts[1].replace('%', '')
                sys = parts[3].replace('%', '')
                self['cpuusrbar'].setValue(int(usr))
                self['cpusysbar'].setValue(int(sys))
                self['cpuusr'].setText('CPU Usr:\n' + usr + ' %')
                self['cpusys'].setText('CPU Sys:\n' + sys + ' %')
                f.close()
                remove('/tmp/cpuinfo.tmp')

    def getUptime(self):
        fp = open('/proc/uptime')
        contents = fp.read().split()
        fp.close()
        total_seconds = float(contents[0])
        days = int(total_seconds / 86400)
        hours = int(total_seconds / 3600 - days * 24)
        minutes = int(total_seconds / 60 - days * 1440 - hours * 60)
        seconds = int(total_seconds % 60)
        if days > 0:
            if days == 1:
                days = str(days)
                self['utday'].setText(_('Day'))
                self['utday'].show()
                self['utdayval'].setText(days)
                self['utdayval'].show()
            else:
                days = str(days)
                self['utday'].setText(_('Days'))
                self['utday'].show()
                self['utdayval'].setText(days)
                self['utdayval'].show()
        if hours > 0:
            if hours == 1:
                hours = str(hours)
                self['uthour'].setText(_('Hour:'))
                self['uthour'].show()
                self['uthourval'].setText(hours)
                self['uthourval'].show()
            else:
                hours = str(hours)
                self['uthour'].setText(_('Hours:'))
                self['uthour'].show()
                self['uthourval'].setText(hours)
                self['uthourval'].show()
        if minutes > 0:
            if minutes == 1:
                minutes = str(minutes)
                self['utmin'].setText(_('Minute:'))
                self['utmin'].show()
                self['utminval'].setText(minutes)
                self['utminval'].show()
            else:
                minutes = str(minutes)
                self['utmin'].setText(_('Minutes:'))
                self['utmin'].show()
                self['utminval'].setText(minutes)
                self['utminval'].show()
        if seconds > 0:
            if seconds == 1:
                seconds = str(seconds)
                self['utsec'].setText(_('Second:'))
                self['utsec'].show()
                self['utsecval'].setText(seconds)
                self['utsecval'].show()
            else:
                seconds = str(seconds)
                self['utsec'].setText(_('Seconds:'))
                self['utsec'].show()
                self['utsecval'].setText(seconds)
                self['utsecval'].show()

    def getKernelVersion(self):
        try:
            fp = open('/proc/version', 'r')
            line = fp.readline()
            fp.close
        except:
            line = 'N/A'

        self['kernelversion'].setText(line.replace('\n', ''))

    def getMemo(self):
        ramused = 0
        swapused = 0
        totused = 0
        rc = system('free > /tmp/ninfo.tmp')
        if fileExists('/tmp/ninfo.tmp'):
            f = open('/tmp/ninfo.tmp', 'r')
            for line in f.readlines():
                parts = line.strip().split()
                if parts[0] == 'Mem:':
                    ramused = int(int(parts[2]) * 100 / int(parts[1]))
                elif parts[0] == 'Swap:':
                    if int(parts[1]) > 1:
                        swapused = int(int(parts[2]) * 100 / int(parts[1]))
                elif parts[0] == 'Total:':
                    totused = int(int(parts[2]) * 100 / int(parts[1]))

            f.close()
            remove('/tmp/ninfo.tmp')
        self.smallmontxt += 'Ram in use: ' + str(ramused) + ' %\n'
        self.smallmontxt += 'Swap in use: ' + str(swapused) + ' %\n'

    def getMemInfo(self):
        ramperc = 0
        swapperc = 0
        totperc = 0
        ramtot = 0
        swaptot = 0
        tottot = 0
        ramfree = 0
        swapfree = 0
        totfree = 0
        ramused = 0
        swapused = 0
        totused = 0
        rc = system('free > /tmp/ninfo.tmp')
        if fileExists('/tmp/ninfo.tmp'):
            f = open('/tmp/ninfo.tmp', 'r')
            for line in f.readlines():
                parts = line.strip().split()
                if parts[0] == 'Mem:':
                    ramperc = int(int(parts[2]) * 100 / int(parts[1]))
                    ramtot = int(int(parts[1]) / 1000)
                    ramfree = int(int(parts[3]) / 1000)
                    ramused = int(int(parts[2]) / 1000)
                elif parts[0] == 'Swap:':
                    if int(parts[1]) > 1:
                        swapperc = int(int(parts[2]) * 100 / int(parts[1]))
                        swaptot = int(int(parts[1]) / 1000)
                        swapfree = int(int(parts[3]) / 1000)
                        swapused = int(int(parts[2]) / 1000)
                elif parts[0] == 'Total:':
                    totperc = int(int(parts[2]) * 100 / int(parts[1]))
                    tottot = int(int(parts[1]) / 1000)
                    totfree = int(int(parts[3]) / 1000)
                    totused = int(int(parts[2]) / 1000)

            f.close()
            remove('/tmp/ninfo.tmp')
        self['ram'].setText('Ram:\n' + str(ramtot) + 'MB\n' + str(ramfree) + 'MB\n' + str(ramused) + 'MB\n' + str(ramperc) + '%')
        self['swap'].setText('Swap:\n' + str(swaptot) + 'MB\n' + str(swapfree) + 'MB\n' + str(swapused) + 'MB\n' + str(swapperc) + '%')
        self['mem_tot'].setText('Total:\n' + str(tottot) + 'MB\n' + str(totfree) + 'MB\n' + str(totused) + 'MB\n' + str(totperc) + '%')
        self['memtotalbar'].setValue(int(totperc))
        self['swapbar'].setValue(int(swapperc))
        self['membar'].setValue(int(ramperc))

    def getSpace(self):
        rc = system('df -m > /tmp/ninfo.tmp')
        flashperc = 0
        flashused = 0
        flashtot = 0
        cfused = 0
        cftot = 0
        cfperc = 0
        usused = 0
        ustot = 0
        usperc = 0
        us1used = 0
        us1tot = 0
        us1perc = 0
        hdused = 0
        hdtot = 0
        hdperc = 0
        fperc = 0
        if fileExists('/tmp/ninfo.tmp'):
            f = open('/tmp/ninfo.tmp', 'r')
            for line in f.readlines():
                line = line.replace('part1', ' ')
                parts = line.strip().split()
                totsp = len(parts) - 1
                if parts[totsp] == '/':
                    flashperc2 = parts[4]
                    flashperc = int(parts[4].replace('%', ''))
                    flashtot = int(parts[1])
                    flashused = int(parts[2])
                if parts[totsp] == '/media/usb':
                    usperc = int(parts[4].replace('%', ''))
                    ustot = int(parts[1])
                    usused = int(parts[2])
                if parts[totsp] == '/media/usb1':
                    us1perc = int(parts[4].replace('%', ''))
                    us1tot = int(parts[1])
                    us1used = int(parts[2])
                if parts[totsp] == '/media/hdd':
                    strview = parts[4].replace('%', '')
                    if strview.isdigit():
                        hdperc = int(parts[4].replace('%', ''))
                        hdtot = int(parts[1])
                        hdused = int(parts[2])

            f.close()
            remove('/tmp/ninfo.tmp')
            ftot = cftot + ustot + us1used + hdtot
            fused = int(cfused) + int(usused) + int(us1used) + int(hdused)
            if ftot > 100:
                fperc = fused * 100 / ftot
        self.smallmontxt += 'Flash in use: ' + str(flashperc) + ' %\n'
        self.smallmontxt += 'Usb in use: ' + str(usperc) + ' %\n'
        self.smallmontxt += 'Usb1 in use: ' + str(us1perc) + ' %\n'
        self.smallmontxt += 'Hdd in use: ' + str(hdperc) + ' %\n'
        self['flashg'].setValue(int(flashperc))
        self['usbg'].setValue(int(usperc * 100 / 120 + 50))
        hddbar = str(hdperc)
        self['hddg'].setValue(int(hdperc))

    def getSpaceInfo(self):
        rc = system('df -h > /tmp/ninfo.tmp')
        flashperc = 0
        flashused = 0
        flashtot = 0
        rootperc = 0
        roottot = 0
        rootused = 0
        rootfree = 0
        usbused = 0
        usbtot = 0
        usbperc = 0
        usb1used = 0
        usb1tot = 0
        usb1perc = 0
        usb2used = 0
        usb2tot = 0
        usb2perc = 0
        usb3used = 0
        usb3tot = 0
        usb3perc = 0
        hddused = 0
        hddtot = 0
        hddperc = 0
        fperc = 0
        usbsumm = 'USB:\n.... \n.... \n.... \n....'
        usb1summ = 'USB1:\n.... \n.... \n.... \n....'
        usb2summ = 'USB2:\n.... \n.... \n.... \n....'
        usb3summ = 'USB3:\n.... \n.... \n.... \n....'
        hddsumm = 'HDD:\n.... \n.... \n.... \n....'
        if fileExists('/tmp/ninfo.tmp'):
            f = open('/tmp/ninfo.tmp', 'r')
            for line in f.readlines():
                line = line.replace('part1', ' ')
                parts = line.strip().split()
                totsp = len(parts) - 1
                if parts[totsp] == '/':
                    rootperc = parts[4]
                    roottot = parts[1]
                    rootused = parts[2]
                    rootfree = parts[3]
                    self['root'].setText('Flash:\n' + str(roottot) + 'B\n' + str(rootfree) + 'B\n' + str(rootused) + 'B\n' + str(rootperc))
                    rootperc = rootperc.replace('%', '')
                    self['rootbar'].setValue(int(rootperc))
                if parts[totsp] == '/media/usb':
                    usbperc = parts[4]
                    usbtot = parts[1]
                    usbused = parts[2]
                    usbfree = parts[3]
                    usbsumm = 'USB:\n' + str(usbtot) + 'B\n' + str(usbfree) + 'B\n' + str(usbused) + 'B\n' + str(usbperc)
                    usbperc = usbperc.replace('%', '')
                if parts[totsp] == '/media/usb1':
                    usb1perc = parts[4]
                    usb1tot = parts[1]
                    usb1used = parts[2]
                    usb1free = parts[3]
                    usb1summ = 'USB1:\n' + str(usb1tot) + 'B\n' + str(usb1free) + 'B\n' + str(usb1used) + 'B\n' + str(usb1perc)
                    usb1perc = usb1perc.replace('%', '')
                if parts[totsp] == '/media/usb2':
                    usb2perc = parts[4]
                    usb2tot = parts[1]
                    usb2used = parts[2]
                    usb2free = parts[3]
                    usb2summ = 'USB2:\n' + str(usb2tot) + 'B\n' + str(usb2free) + 'B\n' + str(usb2used) + 'B\n' + str(usb2perc)
                    usb2perc = usb2perc.replace('%', '')
                if parts[totsp] == '/media/usb3':
                    usb3perc = parts[4]
                    usb3tot = parts[1]
                    usb3used = parts[2]
                    usb3free = parts[3]
                    usb3summ = 'USB3:\n' + str(usb3tot) + 'B\n' + str(usb3free) + 'B\n' + str(usb3used) + 'B\n' + str(usb3perc)
                    usb3perc = usb3perc.replace('%', '')
                if parts[totsp] == '/media/hdd':
                    strview = parts[4].replace('%', '')
                    if strview.isdigit():
                        hddperc = parts[4]
                        hddtot = parts[1]
                        hddused = parts[2]
                        hddfree = parts[3]
                        hddsumm = 'HDD:\n' + str(hddtot) + 'B\n' + str(hddfree) + 'B\n' + str(hddused) + 'B\n' + str(hddperc)
                        hddperc = hddperc.replace('%', '')

            f.close()
            remove('/tmp/ninfo.tmp')
            self['usb'].setText(usbsumm)
            self['usb1'].setText(usb1summ)
            self['usb2'].setText(usb2summ)
            self['usb3'].setText(usb3summ)
            self['hdd'].setText(hddsumm)
            self['usbbar'].setValue(int(usbperc))
            self['usb1bar'].setValue(int(usb1perc))
            self['usb2bar'].setValue(int(usb2perc))
            self['usb3bar'].setValue(int(usb3perc))
            self['hddbar'].setValue(int(hddperc))

    def getServicesInfo(self):
        assh = False
        atelnet = False
        aftp = False
        avpn = False
        asamba = False
        anfs = False
        rc = system('ps > /tmp/nvpn.tmp')
        if fileExists('/etc/inetd.conf'):
            f = open('/etc/inetd.conf', 'r')
            for line in f.readlines():
                parts = line.strip().split()
                if parts[0] == 'telnet':
                    atelnet = True
                if parts[0] == 'ftp':
                    aftp = True

            f.close()
        if fileExists('/tmp/nvpn.tmp'):
            f = open('/tmp/nvpn.tmp', 'r')
            for line in f.readlines():
                if line.find('/usr/sbin/openvpn') != -1:
                    avpn = True
                if line.find('/usr/sbin/dropbear') != -1:
                    assh = True
                if line.find('smbd') != -1:
                    asamba = True
                if line.find('/usr/sbin/rpc.mountd') != -1:
                    anfs = True

            f.close()
            remove('/tmp/nvpn.tmp')
        if assh == True:
            self['ssh_on'].show()
        else:
            self['ssh_on'].hide()
        if atelnet == True:
            self['telnet_on'].show()
        else:
            self['telnet_on'].hide()
        if aftp == True:
            self['ftp_on'].show()
        else:
            self['ftp_on'].hide()
        if asamba == True:
            self['smb_on'].show()
        else:
            self['smb_on'].hide()
        if anfs == True:
            self['nfs_on'].show()
        else:
            self['nfs_on'].hide()

    def getHddtemp(self):
        temperature = 'N/A'
        temperc = 0
        hddloc = ''
        if fileExists('/proc/mounts'):
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if line.find('/hdd') != -1:
                    hddloc = line
                    pos = hddloc.find(' ')
                    hddloc = hddloc[0:pos]
                    hddloc = hddloc.strip()

            f.close()
        if hddloc:
            cmd = 'hddtemp -w ' + hddloc + ' > /tmp/ninfo.tmp'
            rc = system(cmd)
            if fileExists('/tmp/ninfo.tmp'):
                f = open('/tmp/ninfo.tmp', 'r')
                for line in f.readlines():
                    if line.find('WARNING') != -1:
                        continue
                    parts = line.strip().split(':')
                    temperature = parts[2].strip()
                    pos = temperature.find(' ')
                    temperature = temperature[0:pos]
                    if temperature.isdigit():
                        temperc = int(temperature)
                    else:
                        temperature = 'N/A'

                f.close()
            remove('/tmp/ninfo.tmp')
            temperature = str(temperc)
        self.smallmontxt += 'Hdd temp: ' + temperature + ' C'
        self['hddtempg'].setRange((0, 80))
        self['hddtempg'].setValue(temperc)
        self['hddtempbar'].setRange((0, 80))
        self['hddtempbar'].setValue(temperc)

    def getHddTempInfo(self):
        temperature = 'HDD Temp:\nN/A'
        temperc = 0
        hddloc = ''
        if fileExists('/proc/mounts'):
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if line.find('/hdd') != -1:
                    hddloc = line
                    pos = hddloc.find(' ')
                    hddloc = hddloc[0:pos]
                    hddloc = hddloc.strip()

            f.close()
        if hddloc:
            cmd = 'hddtemp -w ' + hddloc + ' > /tmp/ninfo.tmp'
            rc = system(cmd)
            if fileExists('/tmp/ninfo.tmp'):
                f = open('/tmp/ninfo.tmp', 'r')
                for line in f.readlines():
                    if line.find('WARNING') != -1:
                        continue
                    parts = line.strip().split(':')
                    temperature = parts[2].strip()
                    pos = temperature.find(' ')
                    temperature = temperature[0:pos]
                    if temperature.isdigit():
                        temperc = int(temperature)
                    else:
                        temperature = 'HDD Temp:\nN/A'

                f.close()
            remove('/tmp/ninfo.tmp')
            temperature = str(temperc)
        self['hddtempbar'].setRange((0, 80))
        self['hddtempbar'].setValue(int(temperc))
        self['hddtemperature'].setText('HDD Temp:\n' + temperature + ' \xc2\xb0C')

    def KeyGreen(self):
        self.getHddTempInfo()

    def KeyBlue2(self):
        self.session.open(CpuInfo)

    def KeyYellow2(self):
        self.session.open(MemInfo)

    def KeyYellow(self):
        if self.moni_state == 0:
            self.moniShow()
        mytext = ''
        count = 0
        if fileExists('/proc/stat'):
            f = open('/proc/stat', 'r')
            for line in f.readlines():
                if line.find('intr') != -1:
                    continue
                if line.find('cpu0') != -1:
                    continue
                mytext += line

            f.close()
        if fileExists('/proc/stat'):
            f = open('/proc/cpuinfo', 'r')
            for line in f.readlines():
                parts = line.strip().split(':')
                strview = parts[0].strip()
                strview2 = ''
                if len(parts) == 3:
                    strview2 = ' ' + parts[2]
                mytext += strview + ':  ' + parts[1] + strview2 + '\n'
                count += 1
                if count == 9:
                    break

            f.close()
        self['moni2'].setText(mytext)
        self.getUptime()

    def KeyBlue(self):
        self.session.open(PEProcInfo)

    def KeyOne(self):
        self.session.open(PEEnsetInfo)

    def KeyTwo(self):
        self.session.open(ServiceInfo)

    def KeyThree(self):
        self.session.open(DmesgInfo)

    def KeyFour(self):
        self.session.open(TopInfo)

    def KeyFive(self):
        self.session.open(PEProcInfo)

    def KeySix(self):
        self.session.open(About)

    def delTimer(self):
        del self.activityTimer
        del self.moniTimer

    def keyCancel(self):
        self.close()

    def bitrateStopped(self, retval):
        self.close()

    def refresh(self):
        self.updateList()


class PEProcInfo(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self['pibartit'] = Label(' Pid \t Uid \t Command')
        self['infotext'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.close,
         'back': self.close,
         'up': self['infotext'].pageUp,
         'left': self['infotext'].pageUp,
         'down': self['infotext'].pageDown,
         'right': self['infotext'].pageDown})
        self.updatetext()

    def updatetext(self):
        strview = ''
        rc = system('ps > /tmp/ninfo.tmp')
        if fileExists('/tmp/ninfo.tmp'):
            f = open('/tmp/ninfo.tmp', 'r')
            for line in f.readlines():
                parts = line.strip().split()
                if parts[0] == 'PID':
                    continue
                strview += line + '\n'

            f.close()
            remove('/tmp/ninfo.tmp')
        self['infotext'].setText(strview)


class PEEnsetInfo(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self['infotext'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.close,
         'back': self.close,
         'up': self['infotext'].pageUp,
         'left': self['infotext'].pageUp,
         'down': self['infotext'].pageDown,
         'right': self['infotext'].pageDown})
        self.onLayoutFinish.append(self.updatetext)

    def updatetext(self):
        strview = ''
        if fileExists('/etc/enigma2/settings'):
            f = open('/etc/enigma2/settings', 'r')
            for line in f.readlines():
                strview += line

            f.close()
            self['infotext'].setText(strview)


class DmesgInfo(Screen):

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self['config'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'back': self.close,
         'up': self['config'].pageUp,
         'down': self['config'].pageDown,
         'left': self['config'].pageUp,
         'right': self['config'].lastPage})
        self.setScreen()

    def keyExit(self):
        self.close()

    def setScreen(self):
        msg = ''
        dmesg = popen('dmesg').readlines()
        anz = len(dmesg)
        start = anz - 100
        if start < 0:
            start = 0
        for line in dmesg[start:]:
            txt = line.strip() + '\n'
            if len(txt) > 1:
                msg += txt

        self['config'].setText(msg)


class TopInfo(Screen):

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self['config'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'back': self.close,
         'up': self['config'].pageUp,
         'down': self['config'].pageDown,
         'left': self['config'].pageUp,
         'right': self['config'].lastPage})
        self.setScreen()

    def keyExit(self):
        self.close()

    def setScreen(self):
        msg = ''
        topinfo = system('top -n3 > /tmp/procinfo.tmp')
        f = open('/tmp/procinfo.tmp')
        for line in f.readlines():
            txt = line.strip() + '\n'
            if len(txt) > 1:
                msg += txt

        f.close()
        remove('/tmp/procinfo.tmp')
        self['config'].setText(msg)


class MemInfo(Screen):

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self['config'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'back': self.close,
         'up': self['config'].pageUp,
         'down': self['config'].pageDown,
         'left': self['config'].pageUp,
         'right': self['config'].lastPage})
        self.setScreen()

    def keyExit(self):
        self.close()

    def setScreen(self):
        msg = ''
        meminfo = system('cat /proc/meminfo > /tmp/meminfo.tmp')
        f = open('/tmp/meminfo.tmp')
        for line in f.readlines():
            txt = line.strip() + '\n'
            if len(txt) > 1:
                msg += txt

        f.close()
        remove('/tmp/meminfo.tmp')
        self['config'].setText(msg)


class CpuInfo(Screen):

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self['config'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'back': self.close,
         'up': self['config'].pageUp,
         'down': self['config'].pageDown,
         'left': self['config'].pageUp,
         'right': self['config'].lastPage})
        self.setScreen()

    def keyExit(self):
        self.close()

    def setScreen(self):
        msg = ''
        cpuinfo = system('cat /proc/cpuinfo > /tmp/cpuinfo.tmp')
        f = open('/tmp/cpuinfo.tmp')
        for line in f.readlines():
            txt = line.strip() + '\n'
            if len(txt) > 1:
                msg += txt

        f.close()
        remove('/tmp/cpuinfo.tmp')
        self['config'].setText(msg)


class ECMBluePanel(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self['lab1'] = Label(_('xx CAMs Installed'))
        self['lab2'] = Label(_('Set Default CAM'))
        self['lab3'] = Label(_('Active CAM'))
        self['Ilab1'] = Label()
        self['Ilab2'] = Label()
        self['Ilab3'] = Label()
        self['Ilab4'] = Label()
        self['activecam'] = Label()
        self['Ecmtext'] = ScrollLabel()
        self.emlist = []
        self.populate_List()
        self['list'] = MenuList(self.emlist)
        totcam = str(len(self.emlist))
        self['lab1'].setText(totcam + '   CAMs Installed')
        self.onShow.append(self.updateBP)
        self['myactions'] = ActionMap(['OkCancelActions', 'DirectionActions'], {'ok': self.keyOk,
         'cancel': self.close,
         'up': self['Ecmtext'].pageUp,
         'down': self['Ecmtext'].pageDown}, -1)

    def populate_List(self):
        self.camnames = {}
        cams = listdir('/etc/init.d/')
        for fil in cams:
            if fil.startswith('softcam.'):
                cn = fil[8:]
                self.emlist.append(cn)
                self.camnames[cn] = fil[8:]

    def updateBP(self):
        name = 'N/A'
        provider = 'N/A'
        aspect = 'N/A'
        videosize = 'N/A'
        myserviceinfo = ''
        myservice = self.session.nav.getCurrentService()
        if myservice is not None:
            myserviceinfo = myservice.info()
            if self.session.nav.getCurrentlyPlayingServiceReference():
                name = ServiceReference(self.session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
            provider = self.getServiceInfoValue(iServiceInformation.sProvider, myserviceinfo)
            aspect = self.getServiceInfoValue(iServiceInformation.sAspect, myserviceinfo)
            if aspect in (1, 2, 5, 6, 9, 10, 13, 14):
                aspect = '4:3'
            else:
                aspect = '16:9'
            if myserviceinfo:
                if not (myserviceinfo and myserviceinfo.getInfo(iServiceInformation.sVideoWidth)):
                    width = -1
                    if not (myserviceinfo and myserviceinfo.getInfo(iServiceInformation.sVideoHeight)):
                        height = -1
                        if width != -1 and height != -1:
                            videosize = '%dx%d' % (width, height)
                self['Ilab1'].setText('Name: ' + name)
                self['Ilab2'].setText('Provider: ' + provider)
                self['Ilab3'].setText('Aspect Ratio: ' + aspect)
                self['Ilab4'].setText('Videosize: ' + videosize)
                try:
                    currentcam = readlink('/etc/init.d/softcam')
                except OSError:
                    currentcam = 'Not installed'

                self.currentcam = currentcam[8:]
                curCamname = 'Not installed'
                for c in self.camnames.keys():
                    if self.camnames[c] == self.currentcam:
                        curCamname = c

                pos = 0
                for x in self.emlist:
                    if x == curCamname:
                        self['list'].moveToIndex(pos)
                        break
                    pos += 1

                mytext = ''
                f = fileExists('/tmp/ecm.info') and open('/tmp/ecm.info', 'r')
                for line in f.readlines():
                    line = line.replace('\n', '')
                    line = line.strip()
                    if len(line) > 3:
                        mytext = mytext + line + '\n'

                f.close()
            mytext = len(mytext) < 5 and '\n\n    Ecm Info not available.'
        self['activecam'].setText(curCamname)
        self['Ecmtext'].setText(mytext)

    def getServiceInfoValue(self, what, myserviceinfo):
        if myserviceinfo is None:
            return ''
        v = myserviceinfo.getInfo(what)
        if v == -2:
            v = myserviceinfo.getInfoString(what)
        elif v == -1:
            v = 'N/A'
        return v

    def keyOk(self):
        self.sel = self['list'].getCurrent()
        try:
            self.newcam = self.camnames[self.sel]
        except KeyError:
            print '[PEPanel] No CAM is List'
            self.newcam = 'Not installed'

        try:
            system('/etc/init.d/softcam stop')
            remove('/etc/init.d/softcam')
        except OSError:
            print '[PEPanel] no softcam there.'

        try:
            if not self.newcam == 'Not installed':
                symlink('softcam.' + self.newcam, '/etc/init.d/softcam')
        except OSError:
            print '[PEPanel] CAM symlink already exists. do nothing.'

        cmd = '/etc/init.d/softcam restart'
        system(cmd)
        if not self.newcam == 'Not installed':
            self.session.openWithCallback(self.myclose, PEDoStartCam, self.sel)
        else:
            message = _("No Cam installed. Can't restart a cam.")
            self.session.open(MessageBox, message, MessageBox.TYPE_INFO, timeout=10)

    def myclose(self):
        self.close()


class PEDoStartCam(Screen):

    def __init__(self, session, title):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        msg = '\nPlease wait while starting...\n' + title + '...'
        self['connect'] = MultiPixmap()
        self['lab1'] = Label(msg)
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.updatepix)
        self.onShow.append(self.startShow)

    def startShow(self):
        self.activityTimer.start(1000)

    def updatepix(self):
        self.activityTimer.stop()
        del self.activityTimer
        self.close()


class PEPacketManager(Screen, NumericalTextInput):

    def __init__(self, session, plugin_path, wanted_extensions, cache_prefix, title_prefix, args = None):
        Screen.__init__(self, session)
        NumericalTextInput.__init__(self)
        self.session = session
        self.skin_path = plugin_path
        self.wanted_extensions = wanted_extensions
        self.cachename = cache_prefix
        self.titlename = title_prefix
        self.setUseableChars(u'1234567890abcdefghijklmnopqrstuvwxyz')
        self['shortcuts'] = NumberActionMap(['ShortcutActions',
         'WizardActions',
         'NumberActions',
         'InputActions',
         'InputAsciiActions',
         'KeyboardInputActions'], {'ok': self.go,
         'back': self.exit,
         'red': self.exit,
         'green': self.reload,
         'gotAsciiCode': self.keyGotAscii,
         '1': self.keyNumberGlobal,
         '2': self.keyNumberGlobal,
         '3': self.keyNumberGlobal,
         '4': self.keyNumberGlobal,
         '5': self.keyNumberGlobal,
         '6': self.keyNumberGlobal,
         '7': self.keyNumberGlobal,
         '8': self.keyNumberGlobal,
         '9': self.keyNumberGlobal,
         '0': self.keyNumberGlobal}, -1)
        self.list = []
        self.statuslist = []
        self['list'] = List(self.list)
        self['key_red'] = StaticText(_('Close'))
        self['key_green'] = StaticText(_('Reload'))
        self.list_updating = True
        self.packetlist = []
        self.installed_packetlist = {}
        self.upgradeable_packages = {}
        self.Console = ComConsole()
        self.cmdList = []
        self.cachelist = []
        self.cache_ttl = 600
        self.cache_file = eEnv.resolve('${libdir}/enigma2/python/Plugins/SystemPlugins/PEPanel/' + self.cachename)
        self.oktext = _('\nAfter pressing OK, please wait!')
        self.unwanted_extensions = ('-dbg', '-dev', '-doc', 'busybox')
        self.opkgAvail = fileExists('/usr/bin/opkg')
        self.ipkg = IpkgComponent()
        self.ipkg.addCallback(self.ipkgCallback)
        self.onShown.append(self.setWindowTitle)
        self.onLayoutFinish.append(self.rebuildList)
        rcinput = eRCInput.getInstance()
        rcinput.setKeyboardMode(rcinput.kmAscii)

    def keyNumberGlobal(self, val):
        key = self.getKey(val)
        if key is not None:
            keyvalue = key.encode('utf-8')
            if len(keyvalue) == 1:
                self.setNextIdx(keyvalue[0])

    def keyGotAscii(self):
        keyvalue = unichr(getPrevAsciiCode()).encode('utf-8')
        if len(keyvalue) == 1:
            self.setNextIdx(keyvalue[0])

    def setNextIdx(self, char):
        if char in ('0', '1', 'a'):
            self['list'].setIndex(0)
        else:
            idx = self.getNextIdx(char)
            if idx and idx <= self['list'].count:
                self['list'].setIndex(idx)

    def getNextIdx(self, char):
        idx = 0
        for i in self['list'].list:
            if i[0][0] == char:
                return idx
            idx += 1

    def exit(self):
        self.ipkg.stop()
        if self.Console is not None:
            if len(self.Console.appContainers):
                for name in self.Console.appContainers.keys():
                    self.Console.kill(name)

        rcinput = eRCInput.getInstance()
        rcinput.setKeyboardMode(rcinput.kmNone)
        self.close()

    def reload(self):
        if os_path.exists(self.cache_file) == True:
            remove(self.cache_file)
            self.list_updating = True
            self.rebuildList()

    def setWindowTitle(self):
        self.setTitle(self.titlename)

    def setStatus(self, status = None):
        if status:
            self.statuslist = []
            divpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/div-h.png'))
            if status == 'update':
                statuspng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, 'SystemPlugins/SoftwareManager/upgrade.png'))
                self.statuslist.append((_('Package list update'),
                 '',
                 _('Trying to download a new packetlist. Please wait...'),
                 '',
                 statuspng,
                 divpng))
                self['list'].setList(self.statuslist)
            elif status == 'error':
                statuspng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, 'SystemPlugins/SoftwareManager/remove.png'))
                self.statuslist.append((_('Error'),
                 '',
                 _('There was an error downloading the packetlist. Please try again.'),
                 '',
                 statuspng,
                 divpng))
                self['list'].setList(self.statuslist)

    def rebuildList(self):
        self.setStatus('update')
        self.inv_cache = 0
        self.vc = valid_cache(self.cache_file, self.cache_ttl)
        if self.cache_ttl > 0 and self.vc != 0:
            try:
                self.buildPacketList()
            except:
                self.inv_cache = 1

        if self.cache_ttl == 0 or self.inv_cache == 1 or self.vc == 0:
            self.run = 0
            self.ipkg.startCmd(IpkgComponent.CMD_UPDATE)

    def go(self, returnValue = None):
        cur = self['list'].getCurrent()
        if cur:
            status = cur[3]
            package = cur[0]
            self.cmdList = []
            if status == 'installed':
                self.cmdList.append((IpkgComponent.CMD_REMOVE, {'package': package}))
                if len(self.cmdList):
                    self.session.openWithCallback(self.runRemove, MessageBox, _('Do you want to remove the package:\n') + package + '\n' + self.oktext)
            elif status == 'upgradeable':
                if package.startswith('enigma2-plugin-picons'):
                    partitions = harddiskmanager.getMountedPartitions()
                    partitiondict = {}
                    for partition in partitions:
                        partitiondict[partition.mountpoint] = partition

                    supported_filesystems = ['ext4',
                     'ext2',
                     'ext3',
                     'reiser',
                     'reiser4']
                    self.piconlist = []
                    mountpoint = '/'
                    if mountpoint in partitiondict.keys() and partitiondict[mountpoint].free() > 5242880:
                        self.piconlist.append((partitiondict[mountpoint].description, '', partitiondict[mountpoint]))
                    mountpoint = '/media/usb'
                    if mountpoint in partitiondict.keys() and partitiondict[mountpoint].filesystem() in supported_filesystems:
                        self.piconlist.append((partitiondict[mountpoint].description, '-d usb', partitiondict[mountpoint]))
                    mountpoint = '/media/usb1'
                    if mountpoint in partitiondict.keys() and partitiondict[mountpoint].filesystem() in supported_filesystems:
                        self.piconlist.append((partitiondict[mountpoint].description, '-d usb1', partitiondict[mountpoint]))
                    mountpoint = '/media/usb2'
                    if mountpoint in partitiondict.keys() and partitiondict[mountpoint].filesystem() in supported_filesystems:
                        self.piconlist.append((partitiondict[mountpoint].description, '-d usb2', partitiondict[mountpoint]))
                    mountpoint = '/media/usb3'
                    if mountpoint in partitiondict.keys() and partitiondict[mountpoint].filesystem() in supported_filesystems:
                        self.piconlist.append((partitiondict[mountpoint].description, '-d usb3', partitiondict[mountpoint]))
                    mountpoint = '/media/hdd'
                    if mountpoint in partitiondict.keys() and partitiondict[mountpoint].filesystem() in supported_filesystems:
                        self.piconlist.append((partitiondict[mountpoint].description, '-d hdd', partitiondict[mountpoint]))
                    if len(self.piconlist):
                        self.session.openWithCallback(self.runUpgradeCallback, MessageBox, _('Do you want to upgrade the package:\n') + package + '\n' + self.oktext)
                    return
                self.cmdList.append((IpkgComponent.CMD_INSTALL, {'package': package}))
                if len(self.cmdList):
                    self.session.openWithCallback(self.runUpgrade, MessageBox, _('Do you want to upgrade the package:\n') + package + '\n' + self.oktext)
            elif status == 'installable':
                if package.startswith('enigma2-plugin-picons'):
                    partitions = harddiskmanager.getMountedPartitions()
                    partitiondict = {}
                    for partition in partitions:
                        partitiondict[partition.mountpoint] = partition

                    supported_filesystems = ['ext3',
                     'ext2',
                     'reiser',
                     'reiser4']
                    self.piconlist = []
                    mountpoint = '/'
                    if mountpoint in partitiondict.keys() and partitiondict[mountpoint].free() > 5242880:
                        self.piconlist.append((partitiondict[mountpoint].description, '', partitiondict[mountpoint]))
                    mountpoint = '/media/usb'
                    if mountpoint in partitiondict.keys() and partitiondict[mountpoint].filesystem() in supported_filesystems:
                        self.piconlist.append((partitiondict[mountpoint].description, '-d usb', partitiondict[mountpoint]))
                    mountpoint = '/media/usb1'
                    if mountpoint in partitiondict.keys() and partitiondict[mountpoint].filesystem() in supported_filesystems:
                        self.piconlist.append((partitiondict[mountpoint].description, '-d usb1', partitiondict[mountpoint]))
                    mountpoint = '/media/usb2'
                    if mountpoint in partitiondict.keys() and partitiondict[mountpoint].filesystem() in supported_filesystems:
                        self.piconlist.append((partitiondict[mountpoint].description, '-d usb2', partitiondict[mountpoint]))
                    mountpoint = '/media/usb3'
                    if mountpoint in partitiondict.keys() and partitiondict[mountpoint].filesystem() in supported_filesystems:
                        self.piconlist.append((partitiondict[mountpoint].description, '-d usb3', partitiondict[mountpoint]))
                    mountpoint = '/media/hdd'
                    if mountpoint in partitiondict.keys() and partitiondict[mountpoint].filesystem() in supported_filesystems:
                        self.piconlist.append((partitiondict[mountpoint].description, '-d hdd', partitiondict[mountpoint]))
                    if len(self.piconlist):
                        self.session.openWithCallback(self.runUpgradeCallback, MessageBox, _('Do you want to install the package:\n') + package + '\n' + self.oktext)
                    return
                self.cmdList.append((IpkgComponent.CMD_INSTALL, {'package': package}))
                if len(self.cmdList):
                    self.session.openWithCallback(self.runUpgrade, MessageBox, _('Do you want to install the package:\n') + package + '\n' + self.oktext)

    def runRemove(self, result):
        if result:
            self.session.openWithCallback(self.runRemoveFinished, Ipkg, cmdList=self.cmdList)

    def runRemoveFinished(self):
        self.session.openWithCallback(self.RemoveReboot, MessageBox, _('Remove finished.') + ' ' + _('Do you want to restart Enigma2?'), MessageBox.TYPE_YESNO)

    def RemoveReboot(self, result):
        if result is None:
            return
        if result is False:
            cur = self['list'].getCurrent()
            if cur:
                item = self['list'].getIndex()
                self.list[item] = self.buildEntryComponent(cur[0], cur[1], cur[2], 'installable')
                self.cachelist[item] = [cur[0],
                 cur[1],
                 cur[2],
                 'installable']
                self['list'].setList(self.list)
                write_cache(self.cache_file, self.cachelist)
                self.reloadPluginlist()
        if result:
            cur = self['list'].getCurrent()
            if cur:
                item = self['list'].getIndex()
                self.list[item] = self.buildEntryComponent(cur[0], cur[1], cur[2], 'installable')
                self.cachelist[item] = [cur[0],
                 cur[1],
                 cur[2],
                 'installable']
                self['list'].setList(self.list)
                write_cache(self.cache_file, self.cachelist)
                self.reloadPluginlist()
            quitMainloop(3)

    def runUpgrade(self, result):
        if result:
            self.session.openWithCallback(self.runUpgradeFinished, Ipkg, cmdList=self.cmdList)

    def runUpgradeCallback(self, result):
        if result:
            self.session.openWithCallback(self.installDestinationCallback, ChoiceBox, title=_('Install Picons on Media:'), list=self.piconlist)

    def installDestinationCallback(self, result):
        if result:
            cur = self['list'].getCurrent()
            if cur:
                status = cur[3]
                package = cur[0]
                self.cmdList = []
                self.cmdList.append((IpkgComponent.CMD_INSTALL, {'package': package + ' ' + result[1]}))
                self.session.openWithCallback(self.runUpgradeFinished, Ipkg, cmdList=self.cmdList)

    def runUpgradeFinished(self):
        self.session.openWithCallback(self.UpgradeReboot, MessageBox, _('Installation/Upgrade finished.') + ' ' + _('Do you want to restart Enigma2?'), MessageBox.TYPE_YESNO)

    def UpgradeReboot(self, result):
        if result is None:
            return
        if result is False:
            cur = self['list'].getCurrent()
            if cur:
                item = self['list'].getIndex()
                self.list[item] = self.buildEntryComponent(cur[0], cur[1], cur[2], 'installed')
                self.cachelist[item] = [cur[0],
                 cur[1],
                 cur[2],
                 'installed']
                self['list'].setList(self.list)
                write_cache(self.cache_file, self.cachelist)
                self.reloadPluginlist()
        if result:
            cur = self['list'].getCurrent()
            if cur:
                item = self['list'].getIndex()
                self.list[item] = self.buildEntryComponent(cur[0], cur[1], cur[2], 'installed')
                self.cachelist[item] = [cur[0],
                 cur[1],
                 cur[2],
                 'installed']
                self['list'].setList(self.list)
                write_cache(self.cache_file, self.cachelist)
                self.reloadPluginlist()
            quitMainloop(3)

    def ipkgCallback(self, event, param):
        if event == IpkgComponent.EVENT_ERROR:
            self.list_updating = False
            self.setStatus('error')
        elif event == IpkgComponent.EVENT_DONE:
            if self.list_updating:
                self.list_updating = False
                if not self.Console:
                    self.Console = ComConsole()
                cmd = self.ipkg.ipkg + ' list'
                self.Console.ePopen(cmd, self.IpkgList_Finished)

    def IpkgList_Finished(self, result, retval, extra_args = None):
        if result:
            self.packetlist = []
            last_name = ''
            for x in result.splitlines():
                tokens = x.split(' - ')
                name = tokens[0].strip()
                split = x.split(' - ')
                if any((name.startswith(self.wanted_extensions) for x in self.wanted_extensions)) and not any((name.endswith(x) for x in self.unwanted_extensions)):
                    l = len(tokens)
                    version = l > 1 and tokens[1].strip() or ''
                    descr = l > 2 and tokens[2].strip() or ''
                    if name == last_name:
                        continue
                    last_name = name
                    self.packetlist.append([name, version, descr])

        if not self.Console:
            self.Console = ComConsole()
        cmd = self.ipkg.ipkg + ' list_installed'
        self.Console.ePopen(cmd, self.IpkgListInstalled_Finished)

    def IpkgListInstalled_Finished(self, result, retval, extra_args = None):
        if result:
            self.installed_packetlist = {}
            for x in result.splitlines():
                tokens = x.split(' - ')
                name = tokens[0].strip()
                if any((name.startswith(self.wanted_extensions) for x in self.wanted_extensions)) and not any((name.endswith(x) for x in self.unwanted_extensions)):
                    l = len(tokens)
                    version = l > 1 and tokens[1].strip() or ''
                    self.installed_packetlist[name] = version

        if self.opkgAvail:
            if not self.Console:
                self.Console = ComConsole()
            cmd = 'opkg list-upgradable'
            self.Console.ePopen(cmd, self.OpkgListUpgradeable_Finished)
        else:
            self.buildPacketList()

    def OpkgListUpgradeable_Finished(self, result, retval, extra_args = None):
        if result:
            self.upgradeable_packages = {}
            for x in result.splitlines():
                tokens = x.split(' - ')
                name = tokens[0].strip()
                if any((name.startswith(self.wanted_extensions) for x in self.wanted_extensions)) and not any((name.endswith(x) for x in self.unwanted_extensions)):
                    l = len(tokens)
                    version = l > 2 and tokens[2].strip() or ''
                    self.upgradeable_packages[name] = version

        self.buildPacketList()

    def buildEntryComponent(self, name, version, description, state):
        divpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/div-h.png'))
        if state == 'installed':
            installedpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, 'SystemPlugins/SoftwareManager/installed.png'))
            return (name,
             version,
             _(description),
             state,
             installedpng,
             divpng)
        elif state == 'upgradeable':
            upgradeablepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, 'SystemPlugins/SoftwareManager/upgradeable.png'))
            return (name,
             version,
             _(description),
             state,
             upgradeablepng,
             divpng)
        else:
            installablepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, 'SystemPlugins/SoftwareManager/installable.png'))
            return (name,
             version,
             _(description),
             state,
             installablepng,
             divpng)

    def buildPacketList(self):
        self.list = []
        self.cachelist = []
        if self.cache_ttl > 0 and self.vc != 0:
            try:
                self.cachelist = load_cache(self.cache_file)
                if len(self.cachelist) > 0:
                    for x in self.cachelist:
                        self.list.append(self.buildEntryComponent(x[0], x[1], x[2], x[3]))

                    self['list'].setList(self.list)
            except:
                self.inv_cache = 1

        if self.cache_ttl == 0 or self.inv_cache == 1 or self.vc == 0:
            for x in self.packetlist:
                status = ''
                if self.installed_packetlist.has_key(x[0]):
                    if self.opkgAvail:
                        if self.upgradeable_packages.has_key(x[0]):
                            status = 'upgradeable'
                        else:
                            status = 'installed'
                    elif self.installed_packetlist[x[0]] == x[1]:
                        status = 'installed'
                    else:
                        status = 'upgradeable'
                else:
                    status = 'installable'
                self.list.append(self.buildEntryComponent(x[0], x[1], x[2], status))
                self.cachelist.append([x[0],
                 x[1],
                 x[2],
                 status])

            write_cache(self.cache_file, self.cachelist)
            self['list'].setList(self.list)

    def reloadPluginlist(self):
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))


class PasswdScreen(Screen):

    def __init__(self, session, args = 0):
        Screen.__init__(self, session)
        self.title = _('Change Root Password')
        try:
            self['title'] = StaticText(self.title)
        except:
            print 'self["title"] was not found in skin'

        self.user = 'root'
        self.output_line = ''
        self.list = []
        self['passwd'] = ConfigList(self.list)
        self['key_red'] = StaticText(_('Close'))
        self['key_green'] = StaticText(_('Set Password'))
        self['key_yellow'] = StaticText(_('new Random'))
        self['key_blue'] = StaticText(_('virt. Keyboard'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'red': self.close,
         'green': self.SetPasswd,
         'yellow': self.newRandom,
         'blue': self.bluePressed,
         'cancel': self.close}, -1)
        self.buildList(self.GeneratePassword())
        self.onShown.append(self.setWindowTitle)

    def newRandom(self):
        self.buildList(self.GeneratePassword())

    def buildList(self, password):
        self.password = password
        self.list = []
        self.list.append(getConfigListEntry(_('Enter new Password'), ConfigText(default=self.password, fixed_size=False)))
        self['passwd'].setList(self.list)

    def GeneratePassword(self):
        passwdChars = string.letters + string.digits
        passwdLength = 8
        return ''.join(Random().sample(passwdChars, passwdLength))

    def SetPasswd(self):
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)
        self.container.dataAvail.append(self.dataAvail)
        retval = self.container.execute('passwd %s' % self.user)
        if retval == 0:
            self.session.open(MessageBox, _('Sucessfully changed password for root user to:\n%s ' % self.password), MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, _('Unable to change/reset password for root user'), MessageBox.TYPE_ERROR)

    def dataAvail(self, data):
        self.output_line += data
        while True:
            i = self.output_line.find('\n')
            if i == -1:
                break
            self.processOutputLine(self.output_line[:i + 1])
            self.output_line = self.output_line[i + 1:]

    def processOutputLine(self, line):
        if line.find('password: '):
            self.container.write('%s\n' % self.password)

    def runFinished(self, retval):
        del self.container.dataAvail[:]
        del self.container.appClosed[:]
        del self.container
        self.close()

    def bluePressed(self):
        self.session.openWithCallback(self.VirtualKeyBoardTextEntry, VirtualKeyBoard, title=_('Enter your password here:'), text=self.password)

    def VirtualKeyBoardTextEntry(self, callback = None):
        if callback is not None and len(callback):
            self.buildList(callback)

    def setWindowTitle(self, title = None):
        if not title:
            title = self.title
        try:
            self['title'] = StaticText(title)
        except:
            print 'self["title"] was not found in skin'

def fw_test_dib0700():
    if os_path.exists('/lib/firmware/dvb-usb-dib0700-1.20.fw'):
        return 0
    return system('wget http://www.linuxtv.org/downloads/firmware/dvb-usb-dib0700-1.20.fw -O /lib/firmware/dvb-usb-dib0700-1.20.fw')

def fw_test_smsusb():
    if os_path.exists('/lib/firmware/sms1xxx-hcw-55xxx-dvbt-02.fw'):
        return 0
    return system('wget http://www.steventoth.net/linux/sms1xxx/sms1xxx-hcw-55xxx-dvbt-02.fw -O /lib/firmware/sms1xxx-hcw-55xxx-dvbt-02.fw')

def DVBNTPautostart(reason, **kwargs):
    global session
    if config.plugins.dvbntptime.tdtautocheck.value:
        if reason == 0 and kwargs.has_key('session'):
            session = kwargs['session']
            session.open(PEDVBNTPTimeStartup)
    if config.plugins.dvbntptime.ntpautocheck.value:
        if reason == 0 and kwargs.has_key('session'):
            session = kwargs['session']
            session.open(NTPStartup)

def find_in_list(list, search, listpos = 0):
    index = -1
    for item in list:
        index = index + 1
        if item[listpos] == search:
            return index
    return -1

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

def find_in_list(list, search, listpos = 0):
    for item in list:
        if item[listpos] == search:
            return True

    return False

global_session = None

def startPEmenu(menuid):
    if menuid == 'mainmenu':
        return [(_('PEPanel'),
          main,
          'pepanel',
          2)]
    return []

def PELock():
    try:
        from pe import gettitle
        petitle = gettitle()
        return petitle
    except:
        return False

def main(session, **kwargs):
    if PELock() == False:
        return
    else:
        session.open(PEMainMenu)

def Plugins(path, **kwargs):
    global plugin_path
    list = []
    plugin_path = path
    loadPluginSkin(plugin_path)
    list.append(PluginDescriptor(name='PEPanel', description=_('Manage Your PE Image'), icon='pepanel.png', where=[PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=main))
    list.append(PluginDescriptor(name='DVBNTP Time', description='', where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=DVBNTPautostart))
    list.append(PluginDescriptor(name='PEPanel', description=_('Manage Your PE Image'), icon='pepanel.png', where=PluginDescriptor.WHERE_MENU, fnc=startPEmenu))
    return list