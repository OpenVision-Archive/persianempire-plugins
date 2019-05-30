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
from Tools.Directories import pathExists
from Screens.Console import Console

class PESpeedUp(Screen, ConfigListScreen):
    skin = '\n\t<screen position="center,center" size="902,570" title="PE Speed Up">\n\t\t<widget name="lab1" position="10,10" size="882,60" font="Regular;20" valign="top" transparent="1"/>\n\t\t<widget name="config" position="30,70" size="840,450" scrollbarMode="showOnDemand"/>\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="200,530" size="140,40" alphatest="on"/>\n\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="550,530" size="140,40" alphatest="on"/>\n\t\t<widget name="key_red" position="200,530" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>\n\t\t<widget name="key_green" position="550,530" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['lab1'] = Label("Remove all the packages you don't need.\nThis will speed up the performance.")
        self['key_red'] = Label(_('Save'))
        self['key_green'] = Label(_('Cancel'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.saveMypoints,
         'green': self.close,
         'back': self.close})
        self.pluglist = []
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/AudioSync'):
            self.pluglist.append(['AudioSync', 'enigma2-plugin-extensions-audiosync'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/AutoBackup'):
            self.pluglist.append(['AutoBackup', 'enigma2-plugin-extensions-autobackup'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite'):
            self.pluglist.append(['BackupSuite', 'enigma2-plugin-extensions-backupsuite'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/BTDevicesManager'):	
            self.pluglist.append(['BTDevicesManager', 'enigma2-plugin-extensions-btdevicesmanager'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/CacheFlush'):
            self.pluglist.append(['CacheFlush', 'enigma2-plugin-extensions-cacheflush'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/CDInfo'):	
            self.pluglist.append(['CDInfo', 'enigma2-plugin-extensions-cdinfo'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/CutListEditor'):
            self.pluglist.append(['CutListEditor', 'enigma2-plugin-extensions-cutlisteditor'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/DLNABrowser'):
            self.pluglist.append(['DLNABrowser', 'enigma2-plugin-extensions-dlnabrowser'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/DLNAServer'):
            self.pluglist.append(['DLNAServer', 'enigma2-plugin-extensions-dlnaserver'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/DVDPlayer'):
            self.pluglist.append(['DVDPlayer', 'enigma2-plugin-extensions-dvdplayer'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/Filebrowser'):
            self.pluglist.append(['Filebrowser', 'enigma2-plugin-extensions-filebrowser'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/Foreca'):
            self.pluglist.append(['Foreca', 'enigma2-plugin-extensions-foreca'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/GraphMultiEPG'):
            self.pluglist.append(['GraphMultiEPG', 'enigma2-plugin-extensions-graphmultiepg'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/HbbTV'):
            self.pluglist.append(['HbbTV', 'enigma2-plugin-extensions-hbbtv'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer'):
            self.pluglist.append(['IPTVPlayer', 'enigma2-plugin-extensions-e2iplayer'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/LCD4linux'):
            self.pluglist.append(['LCD4linux', 'enigma2-plugin-extensions-lcd4linux'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/LocaleManager'):
            self.pluglist.append(['LocaleManager', 'enigma2-plugin-extensions-localemanager'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/Modem'):
            self.pluglist.append(['Modem', 'enigma2-plugin-extensions-modem'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/MovieCut'):
            self.pluglist.append(['MovieCut', 'enigma2-plugin-extensions-moviecut'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/PluginSkinMover'):
            self.pluglist.append(['PluginSkinMover', 'enigma2-plugin-extensions-pluginskinmover'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/TunerServer'):
            self.pluglist.append(['TunerServer', 'enigma2-plugin-extensions-tunerserver'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/VlcPlayer'):
            self.pluglist.append(['VlcPlayer', 'enigma2-plugin-extensions-vlcplayer'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/3DSettings'):
            self.pluglist.append(['3DSettings', 'enigma2-plugin-systemplugins-3dsettings'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/3GModemManager'):
            self.pluglist.append(['3GModemManager', 'enigma2-plugin-systemplugins-3gmodemmanager'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/AnimationSetup'):
            self.pluglist.append(['AnimationSetup', 'enigma2-plugin-systemplugins-animationsetup'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/FSBLUpdater'):
            self.pluglist.append(['FSBLUpdater', 'enigma2-plugin-systemplugins-fsblupdater'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/HdmiCEC'):
            self.pluglist.append(['HdmiCEC', 'enigma2-plugin-systemplugins-hdmicec'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/KeymapManager'):
            self.pluglist.append(['KeymapManager', 'enigma2-plugin-systemplugins-keymapmanager'])      
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/MultiTransCodingSetup'):
            self.pluglist.append(['MultiTransCodingSetup', 'enigma2-plugin-systemplugins-multitranscodingsetup']) 
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/OSD3DSetup'):
            self.pluglist.append(['OSD3DSetup', 'enigma2-plugin-systemplugins-osd3dsetup'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/OSDPositionSetup'):
            self.pluglist.append(['OSDPositionSetup', 'enigma2-plugin-systemplugins-osdpositionsetup'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SatipClient'):
            self.pluglist.append(['SatipClient', 'enigma2-plugin-systemplugins-satipclient'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SetPasswd'):
            self.pluglist.append(['SetPasswd', 'enigma2-plugin-systemplugins-setpasswd'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SH4BoosterControl'):
            self.pluglist.append(['SH4BoosterControl', 'enigma2-plugin-systemplugins-sh4boostercontrol'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SH4OSDAdjustment'):
            self.pluglist.append(['SH4OSDAdjustment', 'enigma2-plugin-systemplugins-sh4osdadjustment'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SparkUnionTunerType'):
            self.pluglist.append(['SparkUnionTunerType', 'enigma2-plugin-systemplugins-sparkuniontunertype'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SystemTime'):
            self.pluglist.append(['SystemTime', 'enigma2-plugin-systemplugins-systemtime'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement'):
            self.pluglist.append(['VideoEnhancement', 'enigma2-plugin-systemplugins-videoenhancement'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/TransCodingSetup'):
            self.pluglist.append(['TransCodingSetup', 'enigma2-plugin-systemplugins-transcodingsetup'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/WirelessAccessPoint'):
            self.pluglist.append(['WirelessAccessPoint', 'enigma2-plugin-systemplugins-wirelessaccesspoint'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/WOLSetup'):
            self.pluglist.append(['WOLSetup', 'enigma2-plugin-systemplugins-wolsetup'])
        self.updateList()

    def updateList(self):
        self.list = []
        for plug in self.pluglist:
            item = NoSave(ConfigSelection(default='Installed', choices=[('Installed', 'Installed'), ('Remove', 'Remove')]))
            res = getConfigListEntry(plug[0], item)
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
            self.session.open(Console, title=_('PE Speed Up is working, please wait...'), cmdlist=self.mycmdlist, finishedCallback=self.allDone)
        else:
            self.close()

    def RemovePlug(self, name):
        cmd = ''
        for plug in self.pluglist:
            if plug[0] == name:
                cmd = 'opkg remove %s' % plug[1]
        return cmd

    def allDone(self):
        mybox = self.session.openWithCallback(self.RestartGUI, MessageBox, 'Package(s) removed!\n\nYou could install it(them) again from online feeds.\n\nYour STB will be restarted!\n\nPress OK to continue.', MessageBox.TYPE_INFO)
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
    return PluginDescriptor(name='PE Speed Up', description=_('Special version for Open Vision'), where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], icon='pespeedup.png', fnc=main)
