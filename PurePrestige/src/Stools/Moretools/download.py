#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from xml.dom import Node, minidom
import os
from Plugins.Extensions.PurePrestige.Console2 import *
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from enigma import *
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from twisted.web.client import downloadPage, getPage
import urllib
from Components.Label import Label
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

currversion = '3.0'

class PurePrestigelangdownload(Screen):
    skin = '\n\n                <screen name="PurePrestigeSatelliteImport" position="center,center" size="640,520" title="Language download"  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\t\t\t\n                        <widget name="list" position="25,25" size="590,475" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t\t<eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />\n\t\t\t<widget name="info" position="0,100" zPosition="4" size="640,300" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t\n                </screen>'

    def __init__(self, session):
        self.skin = PurePrestigelangdownload.skin
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        Screen.__init__(self, session)
        self.list = []
        self['list'] = MenuList([])
        self['info'] = Label()
        self['fspace'] = Label()
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['info'].setText('Getting language packs,please wait..')
        self.timer = eTimer()
        self.timer.callback.append(self.downloadxmlpage)
        self.timer.start(100, 1)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okClicked,
         'cancel': self.close}, -2)

    def okClicked(self):
        try:
            selection_country = self['list'].getCurrent()
        except:
            return

        self.selection = 'Language-Packages'
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.prombt(urlserver, pluginname)

    def prombt(self, com, dom):
        self.com = com
        self.dom = dom
        instr = 'Please wait while language pack is being downloaded...'
        endstr = 'Press OK to exit'
        self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.close, False, instr, endstr)

    def downloadxmlpage(self):
        url = 'http://www.tunisia-dreambox.info/e2-addons-manager/Language/packs.xml'
        getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print(str(error))
        self['info'].setText('Addons Download Failure,No internet connection or server down !')
        self.downloading = False

    def _gotPageLoad(self, data):
        self.xml = data
        try:
            if self.xml:
                xmlstr = minidom.parseString(self.xml)
            else:
                self.downloading = False
                self['info'].setText('Addons Download Failure,No internet connection or server down !')
                return
            self.data = []
            self.names = []
            icount = 0
            list = []
            xmlparse = xmlstr
            self.xmlparse = xmlstr
            for plugins in self.xmlparse.getElementsByTagName('plugins'):
                for plugin in plugins.getElementsByTagName('plugin'):
                    list.append(plugin.getAttribute('name').encode('utf8'))

            list.sort()
            self.list = list
            self['info'].setText('')
            self['list'].setList(self.list)
            self.downloading = True
        except:
            self.downloading = False
            self['info'].setText('Error processing server addons data')


class IpkgPackages(Screen):
    skin = '\n\t\t<screen position="center,center" size="600,430" title="Tunisiasat Addons Manager v3.0" >\n\t\t\t  <widget name="countrymenu" position="10,0" size="590,373" scrollbarMode="showOnDemand" />\n\t                 \n        \t</screen>\n\t\t'

    def __init__(self, session, xmlparse, selection):
        self.skin = IpkgPackages.skin
        Screen.__init__(self, session)
        self.xmlparse = xmlparse
        self.selection = selection
        list = []
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    list.append(plugin.getAttribute('name').encode('utf8'))

        list.sort()
        self['countrymenu'] = MenuList(list)
        self['actions'] = ActionMap(['SetupActions'], {'ok': self.selclicked,
         'cancel': self.close}, -2)

    def selclicked(self):
        try:
            selection_country = self['countrymenu'].getCurrent()
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.prombt(urlserver, pluginname)

    def prombt(self, com, dom):
        self.com = com
        self.dom = dom
        instr = ' Please wait while language pack is being downloaded...'
        self.session.open(Console2.Console2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.close, False, instr)
