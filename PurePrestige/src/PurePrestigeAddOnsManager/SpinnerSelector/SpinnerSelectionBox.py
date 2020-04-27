# -*- coding: utf-8 -*-
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.config import config
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from Spinner import Spinner
import os
from enigma import eTimer

class SpinnerSelectionBox(Screen):
    skin = '\n\t<screen name="SpinnerSelectionBox" position="center,center" size="550,400" title="Spinner Preview" backgroundColor="transparent"  flags="wfNoBorder">\n\t\t\n                <widget name="text" position="200,300" size="250,100" font="Regular;24" backgroundColor="transparent" transparent="1" zPosition="2" />\n\t\t\n\t\t<widget name="bild" position="200,10"  size="300,200" transparent="1" zPosition="2" />\n\t\t\n\t</screen>'

    def __init__(self, session, defpath = None):
        self.skin = SpinnerSelectionBox.skin
        Screen.__init__(self, session)
        list = []
        self['text'] = Label('please wait while downloading preview /n Press Ok to exits')
        self.url = 'http://www.tunisia-dreambox.info/e2-addons-manager/Spinners/spinners_collection/enigma2-spinner-elephant_06.05.2011_mipsel2.ipk'
        self['actions'] = ActionMap(['SetupActions'], {'ok': self.close,
         'cancel': self.close}, -1)
        cursel = 'spinner'
        self.Bilder = []
        if cursel:
            for i in range(64):
                if os.path.isfile('/usr/share/enigma2/skin_default/%s/wait%d.png' % (cursel, i + 1)):
                    self.Bilder.append('/usr/share/enigma2/skin_default/%s/wait%d.png' % (cursel, i + 1))

        else:
            self.Bilder = []
        self['text'].setText('Press ok to exit')
        self['bild'] = Spinner(self.Bilder)
