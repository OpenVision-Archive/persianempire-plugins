# -*- coding: utf-8 -*-
from __future__ import print_function
from enigma import *
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ScrollLabel import ScrollLabel
from Components.GUIComponent import *
from Components.MenuList import MenuList
from Components.Input import Input
from Screens.Console import Console
import os
from Components.Sources.StaticText import StaticText
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools import Notifications
from os import popen
from time import strftime, gmtime, localtime
from enigma import eTimer
from time import *
import time
import datetime
from Components.ConfigList import ConfigListScreen
from Components.Element import cached
from Components.Label import Label
from Components.Console import Console

class PurePrestigeSetTimeChanger(Screen):
    skin = '\n        <screen position="center,center" size="500,300" title="Change Time Menu" >\n            <widget source="key_blue" render="Label" position="180,160" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n            <ePixmap pixmap="buttons/blue.png" position="180,160" size="140,40" transparent="1" alphatest="on" />\n            <widget source="introduction" render="Label" position="0,50" size="550,80" zPosition="10" font="Regular;21" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />\n        </screen>'

    def __init__(self, session, args = 0):
        self.skin = PurePrestigeSetTimeChanger.skin
        self.session = session
        Screen.__init__(self, session)
        self.menu = args
        self['key_blue'] = StaticText(_('Change'))
        self['introduction'] = StaticText(_('Local: ' + strftime('%H:%M', localtime()) + ', UTC: ' + strftime('%H:%M', gmtime())))
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'ok': self.startchanger,
         'back': self.close,
         'blue': self.startchanger}, -1)

    def startchanger(self):
        ChangeTimeWizzard(self.session)


class ChangeTimeWizzard(Screen):

    def __init__(self, session):
        self.session = session
        jetzt = time.time()
        timezone = datetime.datetime.utcnow()
        delta = jetzt - time.mktime(timezone.timetuple())
        print('delta: %i' % delta)
        print('oldtime: %i' % jetzt)
        self.oldtime = strftime('%Y:%m:%d %H:%M', localtime())
        self.session.openWithCallback(self.askForNewTime, InputBox, title=_('Please Enter new Systemtime - OK will restart enigma2 !'), text='%s' % self.oldtime, maxSize=16, type=Input.NUMBER)

    def askForNewTime(self, newclock):
        try:
            length = len(newclock)
        except:
            length = 0

        if newclock is None:
            self.skipChangeTime('no new time')
        elif (length == 16) is False:
            self.skipChangeTime('new time string too short')
        elif (newclock.count(' ') < 1) is True:
            self.skipChangeTime('invalid format')
        elif (newclock.count(':') < 3) is True:
            self.skipChangeTime('invalid format')
        else:
            full = []
            full = newclock.split(' ', 1)
            newdate = full[0]
            newtime = full[1]
            print('newdate %s newtime %s' % (newdate, newtime))
            parts = []
            parts = newdate.split(':', 2)
            newyear = parts[0]
            newmonth = parts[1]
            newday = parts[2]
            parts = newtime.split(':', 1)
            newhour = parts[0]
            newmin = parts[1]
            maxmonth = 31
            if int(newmonth) == 4 or int(newmonth) == 6 or int(newmonth) == 9 or (int(newmonth) == 11) is True:
                maxmonth = 30
            elif (int(newmonth) == 2) is True:
                if (4 * int(int(newyear) / 4) == int(newyear)) is True:
                    maxmonth = 28
                else:
                    maxmonth = 27
            if int(newyear) < 2007 or int(newyear) > 2027 or (len(newyear) < 4) is True:
                self.skipChangeTime('invalid year %s' % newyear)
            elif int(newmonth) < 0 or int(newmonth) > 12 or (len(newmonth) < 2) is True:
                self.skipChangeTime('invalid month %s' % newmonth)
            elif int(newday) < 1 or int(newday) > maxmonth or (len(newday) < 2) is True:
                self.skipChangeTime('invalid day %s' % newday)
            elif int(newhour) < 0 or int(newhour) > 23 or (len(newhour) < 2) is True:
                self.skipChangeTime('invalid hour %s' % newhour)
            elif int(newmin) < 0 or int(newmin) > 59 or (len(newmin) < 2) is True:
                self.skipChangeTime('invalid minute %s' % newmin)
            else:
                self.newtime = '%s.%s.%s-%s:%s:%s' % (newyear,
                 newmonth,
                 newday,
                 newhour,
                 newmin,
                 '30')
                print('date -s %s' % self.newtime)
                self.session.openWithCallback(self.DoChangeTimeRestart, MessageBox, _('Enigma2 will restart to change Systemtime - OK ?'), MessageBox.TYPE_YESNO)
        return

    def DoChangeTimeRestart(self, answer):
        if answer is None:
            self.skipChangeTime('answer is None')
        if answer is False:
            self.skipChangeTime('you were not confirming')
        else:
            Console().ePopen('date -s %s' % self.newtime)
            quitMainloop(3)
        return

    def skipChangeTime(self, reason):
        self.session.open(MessageBox, _('Change Systemtime was canceled, because %s' % reason), MessageBox.TYPE_WARNING)
