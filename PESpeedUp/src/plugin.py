# for localized messages
from . import _
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigSelection, NoSave
from Components.Sources.List import List
from Tools.Directories import pathExists, fileExists
from Screens.Console import Console

class PESpeedUp(Screen, ConfigListScreen):
    skin = '\n\t<screen position="center,center" size="902,570" title="PE Speed Up">\n\t\t<widget name="lab1" position="10,10" size="882,60" font="Regular;20" valign="top" transparent="1"/>\n\t\t<widget name="config" position="30,70" size="840,450" scrollbarMode="showOnDemand"/>\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="200,530" size="140,40" alphatest="on"/>\n\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="550,530" size="140,40" alphatest="on"/>\n\t\t<widget name="key_red" position="200,530" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>\n\t\t<widget name="key_green" position="550,530" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['lab1'] = Label(_("Remove all the packages you don't need.\nThis will speed up the performance."))
        self['key_red'] = Label(_("Save"))
        self['key_green'] = Label(_("Cancel"))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.saveMypoints,
         'green': self.close,
         'back': self.close})
        self.packagelist = []
        if fileExists('/usr/bin/astra'):
            self.packagelist.append(['astra-sm', 'astra-sm'])
        if fileExists('/usr/sbin/anacron'):
            self.packagelist.append(['cronie', 'cronie'])
        if fileExists('/usr/bin/curl'):
            self.packagelist.append(['curl', 'curl'])
        if fileExists('/usr/bin/streamproxy'):
            self.packagelist.append(['streamproxy', 'streamproxy'])
        if fileExists('/usr/bin/oscam'):
            self.packagelist.append(['OSCam', 'enigma2-plugin-softcams-oscam'])
        if fileExists('/usr/bin/oscam-emu'):
            self.packagelist.append(['OSCam-Emu', 'enigma2-plugin-softcams-oscam-emu'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/AudioSync'):
            self.packagelist.append(['AudioSync', 'enigma2-plugin-extensions-audiosync'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/AutoBackup'):
            self.packagelist.append(['AutoBackup', 'enigma2-plugin-extensions-autobackup'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite'):
            self.packagelist.append(['BackupSuite', 'enigma2-plugin-extensions-backupsuite'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/BTDevicesManager'):	
            self.packagelist.append(['BTDevicesManager', 'enigma2-plugin-extensions-btdevicesmanager'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/CacheFlush'):
            self.packagelist.append(['CacheFlush', 'enigma2-plugin-extensions-cacheflush'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/CDInfo'):	
            self.packagelist.append(['CDInfo', 'enigma2-plugin-extensions-cdinfo'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/CutListEditor'):
            self.packagelist.append(['CutListEditor', 'enigma2-plugin-extensions-cutlisteditor'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/DLNABrowser'):
            self.packagelist.append(['DLNABrowser', 'enigma2-plugin-extensions-dlnabrowser'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/DLNAServer'):
            self.packagelist.append(['DLNAServer', 'enigma2-plugin-extensions-dlnaserver'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/DVDPlayer'):
            self.packagelist.append(['DVDPlayer', 'enigma2-plugin-extensions-dvdplayer'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/Filebrowser'):
            self.packagelist.append(['Filebrowser', 'enigma2-plugin-extensions-filebrowser'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/Foreca'):
            self.packagelist.append(['Foreca', 'enigma2-plugin-extensions-foreca'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/GraphMultiEPG'):
            self.packagelist.append(['GraphMultiEPG', 'enigma2-plugin-extensions-graphmultiepg'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/HbbTV'):
            self.packagelist.append(['HbbTV', 'enigma2-plugin-extensions-hbbtv'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer'):
            self.packagelist.append(['IPTVPlayer', 'enigma2-plugin-extensions-e2iplayer'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/LCD4linux'):
            self.packagelist.append(['LCD4linux', 'enigma2-plugin-extensions-lcd4linux'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/Modem'):
            self.packagelist.append(['Modem', 'enigma2-plugin-extensions-modem'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/MovieCut'):
            self.packagelist.append(['MovieCut', 'enigma2-plugin-extensions-moviecut'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/PluginSkinMover'):
            self.packagelist.append(['PluginSkinMover', 'enigma2-plugin-extensions-pluginskinmover'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/TunerServer'):
            self.packagelist.append(['TunerServer', 'enigma2-plugin-extensions-tunerserver'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/VlcPlayer'):
            self.packagelist.append(['VlcPlayer', 'enigma2-plugin-extensions-vlcplayer'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/3DSettings'):
            self.packagelist.append(['3DSettings', 'enigma2-plugin-systemplugins-3dsettings'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/3GModemManager'):
            self.packagelist.append(['3GModemManager', 'enigma2-plugin-systemplugins-3gmodemmanager'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/AnimationSetup'):
            self.packagelist.append(['AnimationSetup', 'enigma2-plugin-systemplugins-animationsetup'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/FSBLUpdater'):
            self.packagelist.append(['FSBLUpdater', 'enigma2-plugin-systemplugins-fsblupdater'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/HdmiCEC'):
            self.packagelist.append(['HdmiCEC', 'enigma2-plugin-systemplugins-hdmicec'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/KeymapManager'):
            self.packagelist.append(['KeymapManager', 'enigma2-plugin-systemplugins-keymapmanager'])      
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/MultiTransCodingSetup'):
            self.packagelist.append(['MultiTransCodingSetup', 'enigma2-plugin-systemplugins-multitranscodingsetup']) 
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/OSD3DSetup'):
            self.packagelist.append(['OSD3DSetup', 'enigma2-plugin-systemplugins-osd3dsetup'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/OSDPositionSetup'):
            self.packagelist.append(['OSDPositionSetup', 'enigma2-plugin-systemplugins-osdpositionsetup'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SatipClient'):
            self.packagelist.append(['SatipClient', 'enigma2-plugin-systemplugins-satipclient'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SetPasswd'):
            self.packagelist.append(['SetPasswd', 'enigma2-plugin-systemplugins-setpasswd'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SH4BoosterControl'):
            self.packagelist.append(['SH4BoosterControl', 'enigma2-plugin-systemplugins-sh4boostercontrol'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SH4OSDAdjustment'):
            self.packagelist.append(['SH4OSDAdjustment', 'enigma2-plugin-systemplugins-sh4osdadjustment'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SparkUnionTunerType'):
            self.packagelist.append(['SparkUnionTunerType', 'enigma2-plugin-systemplugins-sparkuniontunertype'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SystemTime'):
            self.packagelist.append(['SystemTime', 'enigma2-plugin-systemplugins-systemtime'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement'):
            self.packagelist.append(['VideoEnhancement', 'enigma2-plugin-systemplugins-videoenhancement'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/TransCodingSetup'):
            self.packagelist.append(['TransCodingSetup', 'enigma2-plugin-systemplugins-transcodingsetup'])
        if fileExists('/usr/share/enigma2/OctEtFHD/skin.xml'):
            self.packagelist.append(['OctEtFHD', 'enigma2-plugin-skins-octetfhd'])
        if fileExists('/usr/share/enigma2/OctEtSD/skin.xml'):
            self.packagelist.append(['OctEtSD', 'enigma2-plugin-skins-octetsd'])
        if fileExists('/usr/share/enigma2/PLi-HD/skin.xml'):
            self.packagelist.append(['PLi-HD', 'enigma2-plugin-skins-pli-hd'])
        self.updateList()

    def updateList(self):
        self.list = []
        for package in self.packagelist:
            item = NoSave(ConfigSelection(default='Installed', choices=[("Installed", _("Installed")), ("Remove", _("Remove"))]))
            res = getConfigListEntry(package[0], item)
            self.list.append(res)
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def saveMypoints(self):
        self.mycmdlist = []
        for x in self['config'].list:
            if x[1].value == 'Remove':
                cmd = self.RemovePlug(x[0])
                self.mycmdlist.append(cmd)
        if len(self.mycmdlist) > 0:
            self.session.open(Console, title=_("PE Speed Up is working, please wait..."), cmdlist=self.mycmdlist, finishedCallback=self.allDone)
        else:
            self.close()

    def RemovePlug(self, name):
        cmd = ''
        for package in self.packagelist:
            if package[0] == name:
                cmd = 'opkg remove %s' % package[1]
        return cmd

    def allDone(self):
        mybox = self.session.openWithCallback(self.RestartGUI, MessageBox, _("Package(s) removed!\nYou could install it(them) again from online feeds.\nYour STB will be restarted!\nPress OK to continue."), MessageBox.TYPE_INFO)
        mybox.setTitle('Info')

    def RestartGUI(self, answer):
        self.session.open(TryQuitMainloop, 3)

def OVLock():
    try:
        from ov import gettitle
        ovtitle = gettitle()
        return ovtitle
    except:
        return False

def main(session, **kwargs):
    if OVLock() == False:
        return
    else:
        session.open(PESpeedUp)

def Plugins(**kwargs):
    return PluginDescriptor(name = _("PE Speed Up"), description = _("Special version for Open Vision"), where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], icon='pespeedup.png', fnc=main)
