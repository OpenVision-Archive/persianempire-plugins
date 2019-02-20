from enigma import *
from Screens.Screen import Screen
from Components.Button import Button
from Components.Label import Label
from Components.ActionMap import ActionMap
from __init__ import _, loadPluginSkin

class AboutTeam(Screen):

    def __init__(self, session, args = 0):
        Screen.__init__(self, session)
        abouttxt = '\nOpen Vision\n\nhttps://openvision.tech\n'
        self['about'] = Label(abouttxt)
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'cancel': self.quit}, -2)

    def quit(self):
        self.close()
