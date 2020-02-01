from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from SpinnerSelectionBox import SpinnerSelectionBox
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import os
from enigma import eTimer
from Components.Console import Console

def deletefiles(dr):
    for i in range(64):
        if os.path.isfile(dr + '/wait%d.png' % (i + 1)):
            os.remove(dr + '/wait%d.png' % (i + 1))

class downloadScreen(Screen):
    skin = '\n\t<screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\n               \n                <widget name="text" position="10,10" size="620,390" font="Regular;22" backgroundColor="transparent" halign="center" valign="center" transparent="1" zPosition="2" />\n\t\t\n\t\t\n\t\t\n\t</screen>'

    def __init__(self, session, url = None):
        self.skin = downloadScreen.skin
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        Screen.__init__(self, session)
        self['text'] = Label('please wait while downloading preview')
        self.url = url
        self['actions'] = ActionMap(['ActionMap', 'SetupActions', 'ColorActions'], {'ok': self.close,
         'cancel': self.close}, -2)
        self.download = False
        self.timer = eTimer()
        self.timer.callback.append(self.downloadspinner)
        self.timer.start(100, 1)

    def downloadspinner(self):
        path = '/usr/share/enigma2/skin_default/spinner'
        deletefiles(path)
        Console().ePopen('opkg install -force-overwrite %s' % self.url)
        dirs = []
        self.p = ''
        try:
            dirs = os.listdir(path)
            if len(dirs) > 0:
                p = dirs[0]
                self.p = p
            else:
                self['text'].setText('Unable to download preview')
                return
        except:
            self['text'].setText('Unable to download preview')
            return

        self.download = True
        defpath = '/usr/share/enigma2/skin_default/spinner/'
        self.session.openWithCallback(self.close, SpinnerSelectionBox, defpath)

    def cancel(self):
        self.close()
