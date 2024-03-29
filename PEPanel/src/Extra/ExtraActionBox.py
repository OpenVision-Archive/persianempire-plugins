# -*- coding: utf-8 -*-
from enigma import *
from Screens.Screen import Screen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS


class ExtraActionBox(Screen):
    skin = '\n\t<screen name="ExtraActionBox" position="360,325" size="560,70" title=" ">\n\t\t<widget alphaTest="on" name="logo" position="10,10" size="48,48" transparent="1" zPosition="2"/>\n\t\t<widget font="Regular;20" horizontalAlignment="center" name="message" position="60,10" size="490,48" verticalAlignment="center"/>\n\t</screen>'

    def __init__(self, session, message, title, action):
        self.skin = ExtraActionBox.skin
        Screen.__init__(self, session)
        self.session = session
        self.ctitle = title
        self.caction = action
        self['message'] = Label(message)
        self['logo'] = Pixmap()
        self.timer = eTimer()
        self.timer.callback.append(self.__setTitle)
        self.timer.start(200, 1)

    def __setTitle(self):
        if self['logo'].instance is not None:
            self['logo'].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/pictures/run.png'))
        self.setTitle(self.ctitle)
        self.timer = eTimer()
        self.timer.callback.append(self.__start)
        self.timer.start(200, 1)

    def __start(self):
        self.close(self.caction())
