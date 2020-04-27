#!/usr/bin/python
# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eTimer, eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, getDesktop, loadPNG, loadPic
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from Screens.MessageBox import MessageBox
import packuninstaller
import skinuninstaller
import folderuninstaller
import os
from Plugins.Extensions.PurePrestige.Console2 import *

Cmenu_list = [_('Uninstall package'),
 _('Remove plugin folder'),
 _('Remove skin'),
 _('Remove crashlogs')]

def CmenuListEntry(name, idx):
    res = [name]
    if idx == 0:
        png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/images/ipkgremove.png')
    if idx == 1:
        png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/images/folderdelete.png')
    elif idx == 2:
        png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/images/removeskin.png')
    elif idx == 3:
        png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/images/deletecrash.png')
    elif idx == 4:
        png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/images/soccernews.png')
    if fileExists(png):
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(100, 100), png=loadPNG(png)))
    res.append(MultiContentEntryText(pos=(120, 40), size=(460, 120), font=0, text=name))
    return res


class CmenuList(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(100)
        self.l.setFont(0, gFont('Regular', 25))


class PurePrestigeMenuscrn(Screen):
    global HD_Res
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    HD_Res = False
    skin = '\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520" transparent="1"/>\t\n\t\t\n                <widget name="menu" position="20,20" size="600,500" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t        \n        </screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        self.session = session
        self['menu'] = CmenuList([])
        self.working = False
        self.selection = 'all'
        self['actions'] = NumberActionMap(['SetupActions', 'ColorActions'], {'ok': self.okClicked,
         'cancel': self.close}, -2)
        self.onLayoutFinish.append(self.updateMenuList)

    def updateMenuList(self):
        self.menu_list = []
        for x in self.menu_list:
            del self.menu_list[0]

        list = []
        idx = 0
        for x in Cmenu_list:
            list.append(CmenuListEntry(x, idx))
            self.menu_list.append(x)
            idx += 1

        self['menu'].setList(list)

    def showabout(self):
        self.session.open(AboutScreen)

    def okClicked(self):
        self.keyNumberGlobal(self['menu'].getSelectedIndex())

    def keyNumberGlobal(self, idx):
        sel = self.menu_list[idx]
        if sel == _('Uninstall package'):
            self.session.open(packuninstaller.PurePrestigeaddonsScreen)
        elif sel == _('Remove plugin folder'):
            self.session.open(folderuninstaller.PurePrestigeaddonsScreen)
        elif sel == _('Remove skin'):
            self.session.open(skinuninstaller.PurePrestigeAddonsScreen)
        elif sel == _('Remove crashlogs'):
            self.clearcrashlog()

    def clearcrashlog(self):
        val = 'Delete_all_Crashlogs'
        script = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/scripts/%s.sh' % val)
        dom = 'all_Crashlogs'
        instr = 'Please wait while  clearing crashlogs'
        endstr = 'Press ok to exit'
        os.chmod(script, 755)
        self.session.open(Console2.PurePrestigeConsole2, _('Removing: %s') % dom, [script], None, False, instr, endstr)
        return
