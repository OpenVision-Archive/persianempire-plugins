#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from Screens.Screen import Screen
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
import xml.dom.minidom
import os
from Screens.Standby import TryQuitMainloop
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, copyfile, fileExists, removeDir, SCOPE_PLUGINS, SCOPE_LIBDIR
from Components.Sources.List import List
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from enigma import eListboxPythonMultiContent, getDesktop, gFont, loadPNG
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Screens.MessageBox import MessageBox
from Screens.Console import Console
import urllib
from Components.Label import Label
from enigma import iPlayableService, iServiceInformation, eServiceReference, eListboxPythonMultiContent, getDesktop, gFont, loadPNG
from Tools.LoadPixmap import LoadPixmap
from Plugins.Extensions.PurePrestige.Console2 import *
import download

langpypath = resolveFilename(SCOPE_LIBDIR, 'enigma2/python/Components/Language.pyo')
locallangpypath = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Stools/language/Language.pyo')
defaultlanguagepack = ''


def listskins():
    path = '/usr/share/enigma2/po'
    for x in os.listdir(path):
        filepath = path + x + '/skin.xml'


class PurePrestigelangsScreen(Screen):
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    HD_Res = False
    if HD_Res:
        skin = '\n\t\t<screen position="center,center" size="800,500" title="TSiPanel-Language Manager " >\n\t\t\t  <widget name="info1" position="580,460" zPosition="4" size="220,40" font="Regular;18" foregroundColor="yellow" transparent="1" halign="right" valign="top" />\n                          <widget name="ButtonGreentext" position="400,0" size="380,40" valign="center" halign="left" zPosition="10" font="Regular;25" transparent="1" />\n\t\t\t  <widget name="ButtonGreen" pixmap="~/images/button_green.png" position="380,10" zPosition="10" size="100,100" transparent="1" alphatest="on" />\n\t\t\t  <widget name="ButtonBluetext" position="30,0" size="350,40" valign="center" halign="left" zPosition="10" font="Regular;25" transparent="1" />\n\t\t\t  <widget name="ButtonBlue" pixmap="~/images/button_blue.png" position="10,10" zPosition="10" size="100,100" transparent="1" alphatest="on" />\n                          <widget name="ButtonYellowtext" position="20,460" size="350,40" valign="center" halign="left" zPosition="10" font="Regular;25" transparent="1" />\n\t\t\t  <widget name="ButtonYellow" pixmap="~/images/button_yellow.png" position="10,470" zPosition="10" size="100,100" transparent="1" alphatest="on" />\n                          \n\t                  <widget source="menu" render="Listbox" position="10,40" size="780,407" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (100, 0), size = (460, 26), font=0, flags = RT_HALIGN_LEFT, text = 1,color=0xFFA500, color_sel=0xFFA500),\n                                                        MultiContentEntryPixmapAlphaTest(pos = (75, 0), size = (25, 26), png = 1),\t\t\t\t\t\t\t\n                                                        MultiContentEntryPixmapAlphaTest(pos = (5, 0), size = (70, 26), png = 0),\n\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 26)],\n\t\t\t\t\t"itemHeight": 26\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t          </widget>\n        \t</screen>\n\t\t'
    else:
        skin = '\n                        <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                        <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\t\n\t\n\t\t\t<ePixmap position="15,55" size="610,5" pixmap="~/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\n                          <widget name="ButtonGreentext" position="325,20" size="280,40" valign="center" halign="left" zPosition="10" font="Regular;22" transparent="1" />\n\t\t\t  <widget name="ButtonGreen" pixmap="~/images/button_green.png" position="305,30" zPosition="10" size="100,100" transparent="1" alphatest="on" />\n\t\t\t  <widget name="ButtonBluetext" position="45,20" size="280,40" valign="center" halign="left" zPosition="10" font="Regular;22" transparent="1" />\n\t\t\t  <widget name="ButtonBlue" pixmap="~/images/button_blue.png" position="25,30" zPosition="10" size="100,100" transparent="1" alphatest="on" />\n                          <widget name="ButtonYellowtext" position="45,440" size="350,40" valign="center" halign="left" zPosition="10" font="Regular;22" transparent="1" />\n\t\t\t  <widget name="ButtonYellow" pixmap="~/images/button_yellow.png" position="25,450" zPosition="10" size="100,100" transparent="1" alphatest="on" />\n                          <widget source="menu" render="Listbox" position="20,65" size="590,372" scrollbarMode="showOnDemand" transparent="1" zPosition="2" >\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t                \n\t\t\t\t\t\t\tMultiContentEntryText(pos = (195, 0), size = (300, 50), font=0, flags = RT_HALIGN_LEFT, text = 0,color=0xFFA500, color_sel=0xFFA500),\n\t\t\t\t\t\t\n                                                        MultiContentEntryPixmapAlphaTest(pos = (5, 0), size = (25, 50), png = 2),\n\t\t\t\t\t\t        MultiContentEntryPixmapAlphaTest(pos = (40, 0), size = (150, 50), png = 3)\n                                                ],\n\t\t\t\t\t"fonts": [gFont("Regular", 23)],\n\t\t\t\t\t"itemHeight": 62\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t \t  </widget>\n        \t</screen>\n\t\t'

    def __init__(self, session):
        self.skin = PurePrestigelangsScreen.skin
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        Screen.__init__(self, session)
        self.changed = False
        list = []
        self.langs = []
        self.menuList = []
        self['menu'] = List(self.menuList)
        self['ButtonYellow'] = Pixmap()
        self['ButtonYellowtext'] = Label(_('Select all'))
        self['ButtonBlue'] = Pixmap()
        self['ButtonBluetext'] = Label(_('Remove languages'))
        self['ButtonGreen'] = Pixmap()
        self['ButtonGreentext'] = Label(_('Add language'))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'blue': self.prompt,
         'yellow': self.selectall,
         'green': self.langdownload,
         'ok': self.changeSelection,
         'cancel': self.exitlan}, -2)
        self.removelist = []
        if fileExists(locallangpypath) and fileExists(langpypath):
            copyfile(locallangpypath, langpypath)
        self.languagaes()
        self.fillskins()

    def languagaes(self):
        self.langs.append([_('English'), 'en', 'EN'])
        self.langs.append([_('Chinese'), 'zh', 'CN'])
        self.langs.append([_('Chineseh'), 'hk', 'HK'])
        self.langs.append([_('Bulgarian'), 'bg', 'BG'])
        self.langs.append([_('German'), 'de', 'DE'])
        self.langs.append([_('Arabic'), 'ar', 'AE'])
        self.langs.append([_('Catalan'), 'ca', 'AD'])
        self.langs.append([_('Croatian'), 'hr', 'HR'])
        self.langs.append([_('Czech'), 'cs', 'CZ'])
        self.langs.append([_('Danish'), 'da', 'DK'])
        self.langs.append([_('Dutch'), 'nl', 'NL'])
        self.langs.append([_('Estonian'), 'et', 'EE'])
        self.langs.append([_('Finnish'), 'fi', 'FI'])
        self.langs.append([_('French'), 'fr', 'FR'])
        self.langs.append([_('Greek'), 'el', 'GR'])
        self.langs.append([_('Hungarian'), 'hu', 'HU'])
        self.langs.append([_('Lithuanian'), 'lt', 'LT'])
        self.langs.append([_('Latvian'), 'lv', 'LV'])
        self.langs.append([_('Icelandic'), 'is', 'IS'])
        self.langs.append([_('Italian'), 'it', 'IT'])
        self.langs.append([_('Norwegian'), 'no', 'NO'])
        self.langs.append([_('Persian'), 'fa', 'IR'])
        self.langs.append([_('Polish'), 'pl', 'PL'])
        self.langs.append([_('Portuguese'), 'pt', 'PT'])
        self.langs.append([_('Russian'), 'ru', 'RU'])
        self.langs.append([_('Serbian'), 'sr', 'YU'])
        self.langs.append([_('Slovakian'), 'sk', 'SK'])
        self.langs.append([_('Slovenian'), 'sl', 'SI'])
        self.langs.append([_('Spanish'), 'es', 'ES'])
        self.langs.append([_('Swedish'), 'sv', 'SE'])
        self.langs.append([_('Turkish'), 'tr', 'TR'])
        self.langs.append([_('Ukrainian'), 'uk', 'UA'])
        self.langs.append([_('Frisian'), 'fy', 'x-FY'])

    def getsecondkey(self, name):
        for item in self.langs:
            if name == item[1]:
                print(name)
                print(item)
                secondkey = item[2]
                secondkey = secondkey.lower()
                return secondkey

        return 'missing'

    def getlan(Self, key):
        lan = {'bg': 'Bulgarian',
         'hk': 'Chineseh',
         'zh': 'Chinese',
         'fa': 'Persian',
         'en': 'English',
         'de': 'German',
         'ar': 'Arabic',
         'ca': 'Catalan',
         'hr': 'Croatian',
         'cs': 'Czech',
         'da': 'Danish',
         'nl': 'Dutch',
         'et': 'Estonian',
         'fi': 'Finnish',
         'fr': 'French',
         'el': 'Greek',
         'hu': 'Hungarian',
         'lt': 'Lithuanian',
         'lv': 'Latvian',
         'is': 'Icelandic',
         'it': 'Italian',
         'no': 'Norwegian',
         'pl': 'Polish',
         'pt': 'Portuguese',
         'ru': 'Russian',
         'sr': 'Serbian',
         'sk': 'Slovakian',
         'sl': 'Slovenian',
         'es': 'Spanish',
         'sv': 'Swedish',
         'tr': 'Turkish',
         'uk': 'Ukrainian',
         'fy': 'Frisian'}
        try:
            return lan[key]
        except:
            return 'Unkown'

    def langdownload(self):
        self.removelist = []
        self.session.openWithCallback(self.fillskins, download.PurePrestigelangdownload)
        self.changed = True

    def selectall(self):
        if len(self.menuList) > 0:
            pass
        else:
            return
        try:
            for k in range(0, len(self.menuList)):
                self['menu'].setIndex(k)
                self.changeSelection()

        except:
            pass

    def changeSelection(self):
        if len(self.menuList) > 0:
            pass
        else:
            return
        png = None
        idx = self['menu'].getIndex()
        name = self.menuList[idx][1]
        flag = self.menuList[idx][3]
        position = self.getlan(name)
        secondkey = self.getsecondkey(name)
        print(name)
        print(secondkey)
        flag = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, '/usr/share/enigma2/countries/' + secondkey + '.png'))
        if name in self.removelist:
            self.menuList[idx] = (position,
             name,
             None,
             flag)
            self.removelist.remove(name)
            if len(self.removelist) > 0:
                self['ButtonBluetext'].show()
            else:
                self['ButtonBluetext'].hide()
            self['menu'].setList(self.menuList)
            try:
                self['menu'].setIndex(idx + 1)
            except:
                pass

            return
        else:
            png = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/images/lock_on.png'))
            position = self.getlan(name)
            self.menuList[idx] = (position,
             name,
             png,
             flag)
            self.removelist.append(name)
            if len(self.removelist) > 0:
                self['menu'].setList(self.menuList)
                self['ButtonBluetext'].show()
            else:
                self['ButtonBluetext'].hide()
            try:
                self['menu'].setIndex(idx + 1)
            except:
                pass

            return

    def fillskins(self):
        list = []
        self.menuList = []
        self['menu'].setList(self.menuList)
        path = '/usr/share/enigma2/po/'
        self.path = path
        i = 0
        for x in os.listdir(path):
            i = i + 1
            filepath = path + x
            if os.path.exists(filepath):
                lan = self.getlan(x)
                secondkey = self.getsecondkey(x)
                flag = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, '/usr/share/enigma2/countries/' + secondkey + '.png'))
                self.menuList.append((lan,
                 x.encode('utf-8'),
                 None,
                 flag))

        self.menuList.sort()
        if len(self.removelist) > 0:
            self['ButtonBluetext'].show()
        else:
            self['ButtonBluetext'].hide()
        self['menu'].setList(self.menuList)
        return

    def exitlan(self):
        if self.changed == True:
            self.session.openWithCallback(self.restartenigma, MessageBox, _('Restart enigma2 to load languages?'), MessageBox.TYPE_YESNO)
            return
        self.close()

    def restartenigma(self, result):
        if result:
            epgpath = '/media/hdd/epg.dat'
            epgbakpath = '/media/hdd/epg.dat.bak'
            if os.path.exists(epgbakpath):
                os.remove(epgbakpath)
            if os.path.exists(epgpath):
                copyfile(epgpath, epgbakpath)
            self.session.open(TryQuitMainloop, 3)
            return
        self.close()

    def prompt(self):
        path = '/usr/share/enigma2/po/'
        for name in self.removelist:
            selectedfolder = name
            folderpathfile = path + selectedfolder + '/LC_MESSAGES/enigma2.mo'
            foldermess = path + selectedfolder + '/LC_MESSAGES/'
            folderpath = path + selectedfolder
            print(folderpathfile)
            print(foldermess)
            print(folderpath)
            if os.path.exists(folderpathfile):
                os.remove(folderpathfile)
            if os.path.exists(foldermess):
                removeDir(foldermess)
            if os.path.exists(folderpath):
                removeDir(folderpath)

        self.removelist = []
        self.changed = True
        self.fillskins()
