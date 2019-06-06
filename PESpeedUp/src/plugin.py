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
        self['actions'] = ActionMap(['WizardActions','ColorActions','OkCancelActions'], {'red': self.saveList,
         'green': self.cancel,
         'stop': self.cancel,
         'cancel': self.cancel,
         'back': self.cancel})
        self.packagelist = []
        self.packagelist.append(['                                        Binaries', 'astra-sm cronie curl streamproxy'])
        if fileExists('/usr/bin/astra'):
            self.packagelist.append(['astra-sm', 'astra-sm'])
        if fileExists('/usr/sbin/anacron'):
            self.packagelist.append(['cronie', 'cronie'])
        if fileExists('/usr/bin/curl'):
            self.packagelist.append(['curl', 'curl'])
        if fileExists('/usr/bin/streamproxy'):
            self.packagelist.append(['streamproxy', 'streamproxy'])
        self.packagelist.append(['                                        Cams', 'enigma2-plugin-softcams-oscam enigma2-plugin-softcams-oscam-emu'])
        if fileExists('/usr/bin/oscam'):
            self.packagelist.append(['OSCam', 'enigma2-plugin-softcams-oscam'])
        if fileExists('/usr/bin/oscam-emu'):
            self.packagelist.append(['OSCam-Emu', 'enigma2-plugin-softcams-oscam-emu'])
        self.packagelist.append(['                                        Plugins (Extensions)', 'enigma2-plugin-extensions-audiosync enigma2-plugin-extensions-autobackup enigma2-plugin-extensions-backupsuite enigma2-plugin-extensions-btdevicesmanager enigma2-plugin-extensions-cacheflush enigma2-plugin-extensions-cdinfo enigma2-plugin-extensions-cutlisteditor enigma2-plugin-extensions-dlnabrowser enigma2-plugin-extensions-dlnaserver enigma2-plugin-extensions-dvdplayer enigma2-plugin-extensions-filecommander enigma2-plugin-extensions-foreca enigma2-plugin-extensions-graphmultiepg enigma2-plugin-extensions-hbbtv enigma2-plugin-extensions-e2iplayer enigma2-plugin-extensions-e2iplayer-deps enigma2-plugin-extensions-lcd4linux enigma2-plugin-extensions-modem enigma2-plugin-extensions-moviecut enigma2-plugin-extensions-pluginskinmover enigma2-plugin-extensions-tunerserver enigma2-plugin-extensions-vlcplayer'])
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
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/FileCommander'):
            self.packagelist.append(['FileCommander', 'enigma2-plugin-extensions-filecommander'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/Foreca'):
            self.packagelist.append(['Foreca', 'enigma2-plugin-extensions-foreca'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/GraphMultiEPG'):
            self.packagelist.append(['GraphMultiEPG', 'enigma2-plugin-extensions-graphmultiepg'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/HbbTV'):
            self.packagelist.append(['HbbTV', 'enigma2-plugin-extensions-hbbtv'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer'):
            self.packagelist.append(['IPTVPlayer', 'enigma2-plugin-extensions-e2iplayer enigma2-plugin-extensions-e2iplayer-deps'])
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
        self.packagelist.append(['                                        Plugins (System)', 'enigma2-plugin-systemplugins-3dsettings enigma2-plugin-systemplugins-3gmodemmanager enigma2-plugin-systemplugins-animationsetup enigma2-plugin-systemplugins-fsblupdater enigma2-plugin-systemplugins-hdmicec enigma2-plugin-systemplugins-keymapmanager enigma2-plugin-systemplugins-multitranscodingsetup enigma2-plugin-systemplugins-osd3dsetup enigma2-plugin-systemplugins-osdpositionsetup enigma2-plugin-systemplugins-satipclient enigma2-plugin-systemplugins-setpasswd enigma2-plugin-systemplugins-sh4boostercontrol enigma2-plugin-systemplugins-sh4osdadjustment enigma2-plugin-systemplugins-sparkuniontunertype enigma2-plugin-systemplugins-systemtime enigma2-plugin-systemplugins-videoenhancement enigma2-plugin-systemplugins-transcodingsetup'])
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
        self.packagelist.append(['                                        Locales', 'enigma2-locale-ar enigma2-locale-bg enigma2-locale-ca enigma2-locale-cs enigma2-locale-da enigma2-locale-de enigma2-locale-el enigma2-locale-es enigma2-locale-et enigma2-locale-fa enigma2-locale-fi enigma2-locale-fr enigma2-locale-fy enigma2-locale-he enigma2-locale-hr enigma2-locale-hu enigma2-locale-id enigma2-locale-is enigma2-locale-it enigma2-locale-ku enigma2-locale-lt enigma2-locale-lv enigma2-locale-nb enigma2-locale-nl enigma2-locale-nn enigma2-locale-pl enigma2-locale-pt enigma2-locale-pt-br enigma2-locale-ro enigma2-locale-ru enigma2-locale-sk enigma2-locale-sl enigma2-locale-sr enigma2-locale-sv enigma2-locale-th enigma2-locale-tr enigma2-locale-uk enigma2-locale-zh-cn enigma2-locale-zh-hk'])
        if pathExists('/usr/share/enigma2/po/ar'):
            self.packagelist.append(['locale-ar', 'enigma2-locale-ar'])
        if pathExists('/usr/share/enigma2/po/bg'):
            self.packagelist.append(['locale-bg', 'enigma2-locale-bg'])
        if pathExists('/usr/share/enigma2/po/ca'):
            self.packagelist.append(['locale-ca', 'enigma2-locale-ca'])
        if pathExists('/usr/share/enigma2/po/cs'):
            self.packagelist.append(['locale-cs', 'enigma2-locale-cs'])
        if pathExists('/usr/share/enigma2/po/da'):
            self.packagelist.append(['locale-da', 'enigma2-locale-da'])
        if pathExists('/usr/share/enigma2/po/de'):
            self.packagelist.append(['locale-de', 'enigma2-locale-de'])
        if pathExists('/usr/share/enigma2/po/el'):
            self.packagelist.append(['locale-el', 'enigma2-locale-el'])
        if pathExists('/usr/share/enigma2/po/es'):
            self.packagelist.append(['locale-es', 'enigma2-locale-es'])
        if pathExists('/usr/share/enigma2/po/et'):
            self.packagelist.append(['locale-et', 'enigma2-locale-et'])
        if pathExists('/usr/share/enigma2/po/fa'):
            self.packagelist.append(['locale-fa', 'enigma2-locale-fa'])
        if pathExists('/usr/share/enigma2/po/fi'):
            self.packagelist.append(['locale-fi', 'enigma2-locale-fi'])
        if pathExists('/usr/share/enigma2/po/fr'):
            self.packagelist.append(['locale-fr', 'enigma2-locale-fr'])
        if pathExists('/usr/share/enigma2/po/fy'):
            self.packagelist.append(['locale-fy', 'enigma2-locale-fy'])
        if pathExists('/usr/share/enigma2/po/he'):
            self.packagelist.append(['locale-he', 'enigma2-locale-he'])
        if pathExists('/usr/share/enigma2/po/hr'):
            self.packagelist.append(['locale-hr', 'enigma2-locale-hr'])
        if pathExists('/usr/share/enigma2/po/hu'):
            self.packagelist.append(['locale-hu', 'enigma2-locale-hu'])
        if pathExists('/usr/share/enigma2/po/id'):
            self.packagelist.append(['locale-id', 'enigma2-locale-id'])
        if pathExists('/usr/share/enigma2/po/is'):
            self.packagelist.append(['locale-is', 'enigma2-locale-is'])
        if pathExists('/usr/share/enigma2/po/it'):
            self.packagelist.append(['locale-it', 'enigma2-locale-it'])
        if pathExists('/usr/share/enigma2/po/ku'):
            self.packagelist.append(['locale-ku', 'enigma2-locale-ku'])
        if pathExists('/usr/share/enigma2/po/lt'):
            self.packagelist.append(['locale-lt', 'enigma2-locale-lt'])
        if pathExists('/usr/share/enigma2/po/lv'):
            self.packagelist.append(['locale-lv', 'enigma2-locale-lv'])
        if pathExists('/usr/share/enigma2/po/nb'):
            self.packagelist.append(['locale-nb', 'enigma2-locale-nb'])
        if pathExists('/usr/share/enigma2/po/nl'):
            self.packagelist.append(['locale-nl', 'enigma2-locale-nl'])
        if pathExists('/usr/share/enigma2/po/nn'):
            self.packagelist.append(['locale-nn', 'enigma2-locale-nn'])
        if pathExists('/usr/share/enigma2/po/pl'):
            self.packagelist.append(['locale-pl', 'enigma2-locale-pl'])
        if pathExists('/usr/share/enigma2/po/pt'):
            self.packagelist.append(['locale-pt', 'enigma2-locale-pt'])
        if pathExists('/usr/share/enigma2/po/pt_BR'):
            self.packagelist.append(['locale-pt-br', 'enigma2-locale-pt-br'])
        if pathExists('/usr/share/enigma2/po/ro'):
            self.packagelist.append(['locale-ro', 'enigma2-locale-ro'])
        if pathExists('/usr/share/enigma2/po/ru'):
            self.packagelist.append(['locale-ru', 'enigma2-locale-ru'])
        if pathExists('/usr/share/enigma2/po/sk'):
            self.packagelist.append(['locale-sk', 'enigma2-locale-sk'])
        if pathExists('/usr/share/enigma2/po/sl'):
            self.packagelist.append(['locale-sl', 'enigma2-locale-sl'])
        if pathExists('/usr/share/enigma2/po/sr'):
            self.packagelist.append(['locale-sr', 'enigma2-locale-sr'])
        if pathExists('/usr/share/enigma2/po/sv'):
            self.packagelist.append(['locale-sv', 'enigma2-locale-sv'])
        if pathExists('/usr/share/enigma2/po/th'):
            self.packagelist.append(['locale-th', 'enigma2-locale-th'])
        if pathExists('/usr/share/enigma2/po/tr'):
            self.packagelist.append(['locale-tr', 'enigma2-locale-tr'])
        if pathExists('/usr/share/enigma2/po/uk'):
            self.packagelist.append(['locale-uk', 'enigma2-locale-uk'])
        if pathExists('/usr/share/enigma2/po/zh_CN'):
            self.packagelist.append(['locale-zh-cn', 'enigma2-locale-zh-cn'])
        if pathExists('/usr/share/enigma2/po/zh_HK'):
            self.packagelist.append(['locale-zh-hk', 'enigma2-locale-zh-hk'])
        self.packagelist.append(['                                        Skins', 'enigma2-plugin-skins-octetfhd enigma2-plugin-skins-pli-hd'])
        if fileExists('/usr/share/enigma2/OctEtFHD/skin.xml'):
            self.packagelist.append(['OctEtFHD', 'enigma2-plugin-skins-octetfhd'])
        if fileExists('/usr/share/enigma2/PLi-HD/skin.xml'):
            self.packagelist.append(['PLi-HD', 'enigma2-plugin-skins-pli-hd'])
        self.updateList()

    def cancel(self):
        self.close()

    def updateList(self):
        self.list = []
        for package in self.packagelist:
            item = NoSave(ConfigSelection(default='Installed', choices=[("Installed", _("Installed")), ("Remove", _("Remove"))]))
            res = getConfigListEntry(package[0], item)
            self.list.append(res)
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def saveList(self):
        self.mycmdlist = []
        for x in self['config'].list:
            if x[1].value == 'Remove':
                cmd = self.removePackages(x[0])
                self.mycmdlist.append(cmd)
        if len(self.mycmdlist) > 0:
            self.session.open(Console, title=_("PE Speed Up is working, please wait..."), cmdlist=self.mycmdlist, finishedCallback=self.allDone)
        else:
            self.close()

    def removePackages(self, name):
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
