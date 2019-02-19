from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Components.Pixmap import Pixmap
from Plugins.Extensions.PersianPalace import *
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigSelection, NoSave
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists
from os import remove as os_remove
from Screens.Console import Console

class PESpeedUp(Screen, ConfigListScreen):
    skin = '\n\t<screen position="center,center" size="902,570" title="PE Speed Up">\n\t\t<widget name="lab1" position="10,10" size="882,60" font="Regular;20" valign="top" transparent="1"/>\n\t\t<widget name="config" position="30,70" size="840,450" scrollbarMode="showOnDemand"/>\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="200,530" size="140,40" alphatest="on"/>\n\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="550,530" size="140,40" alphatest="on"/>\n\t\t<widget name="key_red" position="200,530" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>\n\t\t<widget name="key_green" position="550,530" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['lab1'] = Label("Remove All The Plugins You Don't Need\nThis Will Speed Up The Performance")
        self['key_red'] = Label(_('Save'))
        self['key_green'] = Label(_('Cancel'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.saveMypoints,
         'green': self.close,
         'back': self.close})
        self.pluglist = []
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/AddStreamUrl'):
            self.pluglist.append(['AddStreamUrl', 'enigma2-plugin-extensions-addstreamurl'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection'):
            self.pluglist.append(['AdvancedMovieSelection', 'enigma2-plugin-extensions-advancedmovieselection'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/AirPlayer'):
            self.pluglist.append(['AirPlayer', 'enigma2-plugin-extensions-airplayer'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/AudioPiP'):
            self.pluglist.append(['AudioPiP', 'enigma2-plugin-extensions-audiopip'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/AudioRestart'):
            self.pluglist.append(['AudioRestart', 'enigma2-plugin-extensions-audiorestart'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/AudioSync'):
            self.pluglist.append(['AudioSync', 'enigma2-plugin-extensions-audiosync'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/AutoBackup'):
            self.pluglist.append(['AutoBackup', 'enigma2-plugin-extensions-autobackup'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/AutoTimer'):
            self.pluglist.append(['AutoTimer', 'enigma2-plugin-extensions-autotimer'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/Bitrate'):
            self.pluglist.append(['Bitrate', 'enigma2-plugin-extensions-bitrate'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/BitrateViewer'):
            self.pluglist.append(['BitrateViewer', 'enigma2-plugin-extensions-bitrateviewer'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/BMediaCenter'):
            self.pluglist.append(['BMediaCenter', 'enigma2-plugin-extensions-bmediacenter'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/CCcamInfo'):
            self.pluglist.append(['CCcamInfo', 'enigma2-plugin-extensions-cccaminfo'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/CDInfo'):
            self.pluglist.append(['CDInfo', 'enigma2-plugin-extensions-cdinfo'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/ChangeRootPassword'):
            self.pluglist.append(['ChangeRootPassword', 'enigma2-plugin-extensions-changerootpassword'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/DLNABrowser'):
            self.pluglist.append(['DLNABrowser', 'enigma2-plugin-extensions-dlnabrowser'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/DLNAServer'):
            self.pluglist.append(['DLNAServer', 'enigma2-plugin-extensions-dlnaserver'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/DreamExplorer'):
            self.pluglist.append(['DreamExplorer', 'enigma2-plugin-extensions-dreamexplorer'])	
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/DynDNS'):
            self.pluglist.append(['DynDNS', 'enigma2-plugin-extensions-dyndns'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/EmailClient'):
            self.pluglist.append(['EmailClient', 'enigma2-plugin-extensions-emailclient'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/EnhancedMovieCenter'):
            self.pluglist.append(['EnhancedMovieCenter', 'enigma2-plugin-extensions-enhancedmoviecenter'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/EPGRefresh'):
            self.pluglist.append(['EPGRefresh', 'enigma2-plugin-extensions-epgrefresh'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/EPGSearch'):
            self.pluglist.append(['EPGSearch', 'enigma2-plugin-extensions-epgsearch'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/FanControl2'):
            self.pluglist.append(['FanControl2', 'enigma2-plugin-extensions-fancontrol2'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/Filebrowser'):
            self.pluglist.append(['Filebrowser', 'enigma2-plugin-extensions-filebrowser'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/FontMagnifier'):
            self.pluglist.append(['FontMagnifier', 'enigma2-plugin-extensions-fontmagnifier'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/Foreca'):
            self.pluglist.append(['Foreca', 'enigma2-plugin-extensions-foreca'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/fstabEditor'):
            self.pluglist.append(['fstabEditor', 'enigma2-plugin-extensions-fstabeditor'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/FTPBrowser'):
            self.pluglist.append(['FTPBrowser', 'enigma2-plugin-extensions-ftpbrowser'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/GoogleMaps'):
            self.pluglist.append(['GoogleMaps', 'enigma2-plugin-extensions-googlemaps'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/HbbTV'):
            self.pluglist.append(['HbbTV', 'enigma2-plugin-extensions-hbbtv'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/HdmiTest'):
            self.pluglist.append(['HdmiTest', 'enigma2-plugin-extensions-hdmitest'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/IMDb'):
            self.pluglist.append(['IMDb', 'enigma2-plugin-extensions-imdb'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/InfoBarTunerState'):
            self.pluglist.append(['InfoBarTunerState', 'enigma2-plugin-extensions-infobartunerstate'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/IPTV-List-Updater'):
            self.pluglist.append(['IPTV-List-Updater', 'enigma2-plugin-extensions-iptvlistupdater'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/LastFM'):
            self.pluglist.append(['LastFM', 'enigma2-plugin-extensions-lastfm'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/LCD4linux'):
            self.pluglist.append(['LCD4linux', 'enigma2-plugin-extensions-lcd4linux'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/LetterBox'):
            self.pluglist.append(['LetterBox', 'enigma2-plugin-extensions-letterbox'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/LocaleManager'):
            self.pluglist.append(['LocaleManager', 'enigma2-plugin-extensions-localemanager'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/LogoManager'):
            self.pluglist.append(['LogoManager', 'enigma2-plugin-extensions-logomanager'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter'):
            self.pluglist.append(['MediaCenter', 'enigma2-plugin-extensions-mediacenter'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/MenuSort'):
            self.pluglist.append(['MenuSort', 'enigma2-plugin-extensions-menusort'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/Modem'):
            self.pluglist.append(['Modem', 'enigma2-plugin-extensions-modem'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/Mosaic'):
            self.pluglist.append(['Mosaic', 'enigma2-plugin-extensions-mosaic'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/MovieCut'):
            self.pluglist.append(['MovieCut', 'enigma2-plugin-extensions-moviecut'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/MovieEPG'):
            self.pluglist.append(['MovieEPG', 'enigma2-plugin-extensions-movieepg'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/MovielistPreview'):
            self.pluglist.append(['MovielistPreview', 'enigma2-plugin-extensions-movielistpreview'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/MovieRetitle'):
            self.pluglist.append(['MovieRetitle', 'enigma2-plugin-extensions-movieretitle'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/MovieSearch'):
            self.pluglist.append(['MovieSearch', 'enigma2-plugin-extensions-moviesearch'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/MovieSelectionQuickButton'):
            self.pluglist.append(['MovieSelectionQuickButton', 'enigma2-plugin-extensions-movieselectionquickbutton'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/MovieTagger'):
            self.pluglist.append(['MovieTagger', 'enigma2-plugin-extensions-movietagger'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton'):
            self.pluglist.append(['MultiQuickButton', 'enigma2-plugin-extensions-multiquickbutton'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/MyTube'):
            self.pluglist.append(['MyTube', 'enigma2-plugin-extensions-mytube'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/NameZap'):
            self.pluglist.append(['NameZap', 'enigma2-plugin-extensions-namezap'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/NewsReader'):
            self.pluglist.append(['NewsReader', 'enigma2-plugin-extensions-newsreader'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/NfsServer'):
            self.pluglist.append(['NfsServer', 'enigma2-plugin-extensions-nfsserver'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/OnDemand'):
            self.pluglist.append(['OnDemand', 'enigma2-plugin-extensions-ondemand'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/PackageManager'):
            self.pluglist.append(['PackageManager', 'enigma2-plugin-extensions-packagemanager'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/PECamManager'):
            self.pluglist.append(['PECamManager', 'enigma2-plugin-extensions-pecammanager'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/PEFAQ'):
            self.pluglist.append(['PEFAQ', 'enigma2-plugin-extensions-pefaq'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/PEInfo'):
            self.pluglist.append(['PEInfo', 'enigma2-plugin-extensions-peinfo'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/PEMultiBoot'):
            self.pluglist.append(['PEMultiBoot', 'enigma2-plugin-extensions-pemultiboot'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/PermanentClock'):
            self.pluglist.append(['PermanentClock', 'enigma2-plugin-extensions-permanentclock'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/PEWeather'):
            self.pluglist.append(['PEWeather', 'enigma2-plugin-extensions-peweather'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/pipzap'):
            self.pluglist.append(['pipzap', 'enigma2-plugin-extensions-pipzap'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/PluginHider'):
            self.pluglist.append(['PluginHider', 'enigma2-plugin-extensions-pluginhider'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige'):
            self.pluglist.append(['PurePrestige', 'enigma2-plugin-extensions-pureprestige'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/PushService'):
            self.pluglist.append(['PushService', 'enigma2-plugin-extensions-pushservice'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/QuickWeather'):
            self.pluglist.append(['QuickWeather', 'enigma2-plugin-extensions-quickweather'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/ReconstructApSc'):
            self.pluglist.append(['ReconstructApSc', 'enigma2-plugin-extensions-reconstructapsc'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/RemoteChannelStreamConverter'):
            self.pluglist.append(['RemoteChannelStreamConverter', 'enigma2-plugin-extensions-remotechannelstreamconverter'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/RemoteControlChannel'):
            self.pluglist.append(['RemoteControlChannel', 'enigma2-plugin-extensions-remotecontrolchannel'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/ScreenPosition'):
            self.pluglist.append(['ScreenPosition', 'enigma2-plugin-extensions-screenposition'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/SetPicon'):
            self.pluglist.append(['SetPicon', 'enigma2-plugin-extensions-setpicon'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/ShootYourScreen'):
            self.pluglist.append(['ShootYourScreen', 'enigma2-plugin-extensions-shootyourscreen'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/ShowClock'):
            self.pluglist.append(['ShowClock', 'enigma2-plugin-extensions-showclock'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/SimpleRSS'):
            self.pluglist.append(['SimpleRSS', 'enigma2-plugin-extensions-simplerss'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/SimpleUmount'):
            self.pluglist.append(['SimpleUmount', 'enigma2-plugin-extensions-simpleumount'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/SnmpAgent'):
            self.pluglist.append(['SnmpAgent', 'enigma2-plugin-extensions-snmpagent'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/SoftCamUpdater'):
            self.pluglist.append(['SoftCamUpdater', 'enigma2-plugin-extensions-softcamupdater'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/StartupToStandby'):
            self.pluglist.append(['StartupToStandby', 'enigma2-plugin-extensions-startuptostandby'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/StreamInterface'):
            self.pluglist.append(['StreamInterface', 'enigma2-plugin-extensions-streaminterface'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/StreamTV'):
            self.pluglist.append(['StreamTV', 'enigma2-plugin-extensions-streamtv'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/TagEditor'):
            self.pluglist.append(['TagEditor', 'enigma2-plugin-extensions-tageditor'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/TunerServer'):
            self.pluglist.append(['TunerServer', 'enigma2-plugin-extensions-tunerserver'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/UsbFormatWizard'):
            self.pluglist.append(['UsbFormatWizard', 'enigma2-plugin-extensions-usbformatwizard'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/UShare'):
            self.pluglist.append(['UShare', 'enigma2-plugin-extensions-ushare'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/VirtualZap'):
            self.pluglist.append(['VirtualZap', 'enigma2-plugin-extensions-virtualzap'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/VlcPlayer'):
            self.pluglist.append(['VlcPlayer', 'enigma2-plugin-extensions-vlcplayer'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/WeatherPlugin'):
            self.pluglist.append(['WeatherPlugin', 'enigma2-plugin-extensions-weatherplugin'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/WebBrowser'):
            self.pluglist.append(['WebBrowser', 'enigma2-plugin-extensions-webbrowser'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/XPower'):
            self.pluglist.append(['XPower', 'enigma2-plugin-extensions-xpower'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/ZapHistoryBrowser'):
            self.pluglist.append(['ZapHistoryBrowser', 'enigma2-plugin-extensions-zaphistorybrowser'])
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/ZapStatistic'):
            self.pluglist.append(['ZapStatistic', 'enigma2-plugin-extensions-zapstatistic'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/3DSettings'):
            self.pluglist.append(['3DSettings', 'enigma2-plugin-systemplugins-3dsettings'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/3GModemManager'):
            self.pluglist.append(['3GModemManager', 'enigma2-plugin-systemplugins-3gmodemmanager'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/AdvHdmi'):
            self.pluglist.append(['AdvHdmi', 'enigma2-plugin-systemplugins-advhdmi'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/AspectRatioSwitch'):
            self.pluglist.append(['AspectRatioSwitch', 'enigma2-plugin-systemplugins-aspectratioswitch'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/AudioEffect'):
            self.pluglist.append(['AudioEffect', 'enigma2-plugin-systemplugins-audioeffect'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/AutoBouquetsMaker'):
            self.pluglist.append(['AutoBouquetsMaker', 'enigma2-plugin-systemplugins-autobouquetsmaker'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/AutomaticCleanup'):
            self.pluglist.append(['AutomaticCleanup', 'enigma2-plugin-systemplugins-automaticcleanup'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/AutomaticVolumeAdjustment'):
            self.pluglist.append(['AutomaticVolumeAdjustment', 'enigma2-plugin-systemplugins-automaticvolumeadjustment'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/AutoResolution'):
            self.pluglist.append(['AutoResolution', 'enigma2-plugin-systemplugins-autoresolution'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/AutoShutDown'):
            self.pluglist.append(['AutoShutDown', 'enigma2-plugin-systemplugins-autoshutdown'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/BouquetProtection'):
            self.pluglist.append(['BouquetProtection', 'enigma2-plugin-systemplugins-bouquetprotection'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/CrossEPG'):
            self.pluglist.append(['CrossEPG', 'enigma2-plugin-systemplugins-crossepg'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/DeviceManager'):
            self.pluglist.append(['DeviceManager', 'enigma2-plugin-systemplugins-devicemanager'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/LEDBrightnessSetup'):
            self.pluglist.append(['LEDBrightnessSetup', 'enigma2-plugin-systemplugins-ledbrightnesssetup'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/NetDrive'):
            self.pluglist.append(['NetDrive', 'enigma2-plugin-systemplugins-netdrive'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/NetworkServer'):
            self.pluglist.append(['NetworkServer', 'enigma2-plugin-systemplugins-networkserver'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/PiPServiceRelation'):
            self.pluglist.append(['PiPServiceRelation', 'enigma2-plugin-systemplugins-pipservicerelation'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/RemoteControlCode'):
            self.pluglist.append(['RemoteControlCode', 'enigma2-plugin-systemplugins-remotecontrolcode'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SambaServer'):
            self.pluglist.append(['SambaServer', 'enigma2-plugin-systemplugins-sambaserver'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SatelliteEditor'):
            self.pluglist.append(['SatelliteEditor', 'enigma2-plugin-systemplugins-satelliteeditor'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceEditor'):
            self.pluglist.append(['ServiceEditor', 'enigma2-plugin-systemplugins-serviceeditor'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SetPasswd'):
            self.pluglist.append(['SetPasswd', 'enigma2-plugin-systemplugins-setpasswd'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/SimpleSatScan'):
            self.pluglist.append(['SimpleSatScan', 'enigma2-plugin-systemplugins-simplesatscan'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/TransCodingSetup'):
            self.pluglist.append(['TransCodingSetup', 'enigma2-plugin-systemplugins-transcodingsetup'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/VideoColorSpace'):
            self.pluglist.append(['VideoColorSpace', 'enigma2-plugin-systemplugins-videocolorspace'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/WirelessAccessPoint'):
            self.pluglist.append(['WirelessAccessPoint', 'enigma2-plugin-systemplugins-wirelessaccesspoint'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/WOLSetup'):
            self.pluglist.append(['WOLSetup', 'enigma2-plugin-systemplugins-wolsetup'])
        if pathExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/ZappingModeSelection'):
            self.pluglist.append(['ZappingModeSelection', 'enigma2-plugin-systemplugins-zappingmodeselection'])
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
            self.session.open(Console, title=_('PE Speed Up Is Working - Please Wait'), cmdlist=self.mycmdlist, finishedCallback=self.allDone)
        else:
            self.close()

    def RemovePlug(self, name):
        cmd = ''
        for plug in self.pluglist:
            if plug[0] == name:
                cmd = 'opkg remove --force-depends %s' % plug[1]
        return cmd

    def allDone(self):
        mybox = self.session.openWithCallback(self.RestartGUI, MessageBox, 'Plugin(s) Removed !\n\nYou Can Install It(Them) Again From Download Manager 5.0\n\nYour STB Will Be Restarted\n\nPress OK To Continue', MessageBox.TYPE_INFO)
        mybox.setTitle('Info')

    def RestartGUI(self, answer):
        self.session.open(TryQuitMainloop, 3)


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
        session.open(PESpeedUp)


def Plugins(**kwargs):
    return PluginDescriptor(name='PE Speed Up', description=_('Special Version For Persian Empire'), where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], icon='pespeedup.png', fnc=main)
