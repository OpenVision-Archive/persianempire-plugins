#!/usr/bin/python
# -*- coding: utf-8 -*-
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.Console import Console
from Components.ActionMap import ActionMap
from Components.Label import Label, MultiColorLabel
from GlobalActions import globalActionMap
import os


class passreset(Screen):
    skin = '\n\t\t<screen position="center,center" size="250,120" title="PurePrestige-Password reset" >\n\t\t<widget name="buttonred" position="10,60" size="120,40" backgroundColor="red" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>\n\t\t\n\t\t<widget name="buttongreen" position="130,60" size="120,40" backgroundColor="green" valign="center" halign="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>\n\t\t\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin = passreset.skin
        self['buttonred'] = Label(_('Cancel'))
        self['buttongreen'] = Label(_('Reset'))
        self['setupActions'] = ActionMap(['ColorActions', 'SetupActions'], {'red': self.cancel,
         'green': self.reset,
         'save': self.save,
         'cancel': self.cancel,
         'ok': self.save})

    def save(self):
        self.close(True)

    def cancel(self):
        self.close(False)

    def reset(self):
        f = open('/etc/passwd', 'r')
        text = f.readline()
        text = f.read()
        f.close
        text = 'root::0:0:root:/home/root:/bin/sh\n' + text
        f = open('/etc/passwd', 'w')
        f.write(text)
        f.close
        self.session.open(MessageBox, _('Password was reset to blank'), MessageBox.TYPE_INFO, 4)
