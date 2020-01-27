import os
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from mediabackends.E2MediaBackend import E2MediaBackend
from protocol_handler import AirplayProtocolHandler
from AirTunes import AirtunesProtocolHandler
from Components.config import config
from Components.config import ConfigSelection
from Components.config import getConfigListEntry
from Components.config import ConfigInteger
from Components.config import ConfigText
from Components.config import ConfigYesNo
from Components.Network import iNetwork
from Screens.MessageBox import MessageBox
from Components.Label import Label
from enigma import getImageVersionString
from Tools import Notifications
from Components.Console import Console
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

currentVersion = getImageVersionString()

config.plugins.airplayer.startuptype = ConfigYesNo(default=True)
config.plugins.airplayer.name = ConfigText(default='Open Vision', fixed_size=False)
config.plugins.airplayer.path = ConfigText(default='/media/hdd/', fixed_size=False)
config.plugins.airplayer.audioBackend = ConfigSelection(default='alsa', choices={'proxy': _('proxy'),
 'alsa': _('ALSA')})
config.plugins.airplayer.setSeekOnStart = ConfigYesNo(default=True)
config.plugins.airplayer.version = ConfigText(default=currentVersion)
config.plugins.airplayer.stopTVOnPicture = ConfigYesNo(default=True)
config.plugins.airplayer.allowiOSVolumeControl = ConfigYesNo(default=True)
config.plugins.airplayer.useProxyIfPossible = ConfigYesNo(default=False)
config.plugins.airplayer.allowWakeupFromStandby = ConfigYesNo(default=True)
config.plugins.airplayer.screensaverEnabled = ConfigYesNo(default=True)
config.plugins.airplayer.cacheMbBeforePlayback = ConfigInteger(default=5)
config.plugins.airplayer.cacheMbBeforeLivePlayback = ConfigInteger(default=5)
config.plugins.airplayer.delayAudioPlayback = ConfigYesNo(default=False)
config.plugins.airplayer.save()

global_session = None
global_protocol_handler = None
global_media_backend = None
global_airtunes_protocol_handler = None

class AP_MainMenu(Screen, ConfigListScreen):
    skin = '<screen name="AP_MainMenu" title="AirPlayer Settings" position="center,center" size="565,370">\n\t\t<ePixmap pixmap="buttons/red.png" position="0,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="buttons/blue.png" position="420,0" size="140,40" alphatest="on" />\n\t\t<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="text" position="5,50" size="555,250" halign="center" valign="center" font="Regular;20" />\n\t</screen>'

    def __init__(self, session, args = None):
        self.skin = AP_MainMenu.skin
        Screen.__init__(self, session)
        self._session = session
        self._hasChanged = False
        self['key_red'] = StaticText(_('Settings'))
        self['key_yellow'] = StaticText(_('Start Service'))
        self['key_blue'] = StaticText(_('Stop Service'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'red': self.keySettings,
         'blue': self.keyStop,
         'yellow': self.keyStart,
         'cancel': self.close}, -2)
        self['text'] = Label()
        self['text'].setText('AirPlayer enigma2 plugin (Open Vision edition)\nVersion: %s\n\nThis plugin is based on AirPlayer from PascalW (https://github.com/PascalW/Airplayer)\n\nFor more information visit https://openvision.tech' % config.plugins.airplayer.version.value)
        self.onLayoutFinish.append(self.setCustomTitle)

    def _changed(self):
        self._hasChanged = True

    def keyStart(self):
        global global_session
        print '[AirPlayer] pressed start'
        print '[AirPlayer] trying to stop if running'
        stopWebserver(global_session)
        print '[AirPlayer] trying to start'
        startWebserver(global_session)
        self.session.openWithCallback(self.close, MessageBox, _('Service successfully started'), MessageBox.TYPE_INFO, timeout=5)

    def keyStop(self):
        print '[AirPlayer] pressed stop'
        stopWebserver(global_session)
        self.session.openWithCallback(self.close, MessageBox, _('Service successfully stoped'), MessageBox.TYPE_INFO, timeout=5)

    def keySettings(self):
        print '[AirPlayer] open Settings'
        self.session.open(AP_ConfigScreen)

    def setCustomTitle(self):
        self.setTitle(_('AirPlayer'))


class AP_ConfigScreen(Screen, ConfigListScreen):
    skin = '<screen name="AP_ConfigScreen" title="AirPlayer Settings" position="center,center" size="565,370">\n\t\t<ePixmap pixmap="buttons/red.png" position="0,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="buttons/green.png" position="140,0" size="140,40" alphatest="on" />\n\t\t<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="config" position="5,50" size="555,250" scrollbarMode="showOnDemand" />\n\t\t<ePixmap pixmap="div-h.png" position="0,301" zPosition="1" size="565,2" />\n\t</screen>'

    def __init__(self, session, args = None):
        self.skin = AP_ConfigScreen.skin
        Screen.__init__(self, session)
        ConfigListScreen.__init__(self, [getConfigListEntry(_('Startup type'), config.plugins.airplayer.startuptype, _('Should the airplayer start automatically on startup?')),
         getConfigListEntry(_('Interface'), config.plugins.airplayer.interface, _('Which interface should be used for the airport service?')),
         getConfigListEntry(_('Service name'), config.plugins.airplayer.name, _('Which name should be used to identify the device with active airport service?')),
         getConfigListEntry(_('Skin'), config.plugins.airplayer.skin, _('Skin')),
         getConfigListEntry(_('Path'), config.plugins.airplayer.path, _('Path for the temp files.')),
         getConfigListEntry(_('Play Audio-Stream via'), config.plugins.airplayer.audioBackend, _('Play Audio-Stream via')),
         getConfigListEntry(_('Set start position'), config.plugins.airplayer.setSeekOnStart, _('Set Start Position of stream')),
         getConfigListEntry(_('Stop TV while displaying pictures'), config.plugins.airplayer.stopTVOnPicture, _('Stop TV while displaying Pictures')),
         getConfigListEntry(_('Allow volume-control from iOS device'), config.plugins.airplayer.allowiOSVolumeControl, _('Allow Volume-Control from iOS Device')),
         getConfigListEntry(_('Use built-In Proxy'), config.plugins.airplayer.useProxyIfPossible, _('Use Built-in Proxy')),
         getConfigListEntry(_('Start playback on MB cached'), config.plugins.airplayer.cacheMbBeforePlayback, _('Start Playback on percent cached')),
         getConfigListEntry(_('Start live-Stream on MB cached'), config.plugins.airplayer.cacheMbBeforeLivePlayback, _('Start Live-Stream on seconds cached')),
         getConfigListEntry(_('Allow wakeup from standby'), config.plugins.airplayer.allowWakeupFromStandby, _('Allow wakeup from Standby')),
         getConfigListEntry(_('Enable screensaver'), config.plugins.airplayer.screensaverEnabled, _('Enable screensaver')),
         getConfigListEntry(_('Async start of Audioplayer (Workaround)'), config.plugins.airplayer.delayAudioPlayback, _('Async start of Audioplayer (Workaround)'))], session=session, on_change=self._changed)
        self._session = session
        self._hasChanged = False
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Save'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {'green': self.keySave,
         'cancel': self.keyCancel}, -2)
        self.onLayoutFinish.append(self.setCustomTitle)

    def _changed(self):
        self._hasChanged = True

    def keySave(self):
        print '[AirPlayer] pressed save'
        self.saveAll()
        if self._hasChanged:
            self.session.openWithCallback(self.restartGUI, MessageBox, _('Some settings may need a GUI restart\nDo you want to Restart the GUI now?'), MessageBox.TYPE_YESNO)
        else:
            self.session.openWithCallback(self.quitPlugin, MessageBox, _('Nothing was changed. Do you want to quit?'), MessageBox.TYPE_YESNO)

    def quitPlugin(self, answer):
        if answer is True:
            self.close()

    def restartGUI(self, answer):
        if answer is True:
            from Screens.Standby import TryQuitMainloop
            stopWebserver(global_session)
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def setCustomTitle(self):
        self.setTitle(_('Settings for Airplayer'))


def stopWebserver(session):
    Console().ePopen('killall -9 zeroconfig &')
    print '[AirPlayer] service stopped'


def startWebserver(session):
    global global_airtunes_protocol_handler
    global global_protocol_handler
    global global_media_backend
    config.plugins.airplayer.version.value = currentVersion
    print '[AirPlayer] starting AirPlayer version', config.plugins.airplayer.version.value
    print '[AirPlayer] starting webserver'
    print '[AirPlayer] init Backend'
    media_backend = E2MediaBackend(session)
    print '[AirPlayer] init protocol handler'
    protocol_handler = AirplayProtocolHandler(6002, media_backend)
    aitrunes_ph = AirtunesProtocolHandler(media_backend)
    global_protocol_handler = protocol_handler
    global_media_backend = media_backend
    global_airtunes_protocol_handler = aitrunes_ph
    print '[AirPlayer] starting protocol hadler'
    protocol_handler.start()
    aitrunes_ph.start()
    print '[AirPlayer] starting webserver done'
    print '[AirPlayer] starting zeroconf'
    Console().ePopen('killall -9 zeroconfig')
    Console().ePopen("%s %s %s &") % (resolveFilename(SCOPE_PLUGINS, "Extensions/AirPlayer/zeroconfig"), config.plugins.airplayer.name.value, config.plugins.airplayer.interface.value))
    print '[AirPlayer] starting zeroconf done'


def sessionstart(reason, session):
    global global_session
    global_session = session


def networkstart(reason, **kwargs):
    interfaces = []
    for i in iNetwork.getAdapterList():
        interfaces.append((i, i))
        print '[AirPlayer] found network dev', i

    config.plugins.airplayer.interface = ConfigSelection(choices=interfaces, default='eth0')
    if reason == 1 and config.plugins.airplayer.startuptype.value:
        startWebserver(global_session)
    elif reason == 0:
        stopWebserver(global_session)


def main(session, **kwargs):
    session.open(AP_MainMenu)


def Plugins(**kwargs):
    return [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart), PluginDescriptor(where=[PluginDescriptor.WHERE_NETWORKCONFIG_READ], fnc=networkstart), PluginDescriptor(name='AirPlayer', description='Special version for Open Vision', where=PluginDescriptor.WHERE_PLUGINMENU, icon='plugin.png', fnc=main)]
