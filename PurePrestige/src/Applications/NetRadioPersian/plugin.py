from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
import xml.dom.minidom
import os
from Plugins.Extensions.PurePrestige.Console2 import *
from Components.Button import Button
from Tools.Directories import fileExists
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from enigma import eTimer, eListboxPythonMultiContent, getDesktop, gFont, loadPNG
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Screens.MessageBox import MessageBox
from Screens.Console import Console
import urllib
from Components.Label import Label
from Components.ServiceEventTracker import ServiceEventTracker
from enigma import iPlayableService, iServiceInformation, eServiceReference, eListboxPythonMultiContent, getDesktop, gFont, loadPNG
from Tools.LoadPixmap import LoadPixmap
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import config, ConfigDirectory, ConfigSubsection, ConfigSubList, ConfigEnableDisable, ConfigNumber, ConfigText, ConfigSelection, ConfigYesNo, ConfigPassword, getConfigListEntry, configfile

config.plugins.Cradio = ConfigSubsection()
config.plugins.Cradio.stations = ConfigSubList()
config.plugins.Cradio.stations_count = ConfigNumber(default=0)
currversion = '3.0'
currxmlversion = '3.0'

def initProfileConfig():
    s = ConfigSubsection()
    s.name = ConfigText(default='')
    s.code = ConfigText(default='')
    config.plugins.Cradio.stations.append(s)
    return s


def initConfig():
    count = config.plugins.Cradio.stations_count.value
    if count != 0:
        i = 0
        while i < count:
            initProfileConfig()
            i += 1


initConfig()

def CCcamListEntry(name, idx):
    name = ''
    res = [name]
    if idx == 0:
        idx = 'fav'
    elif idx == 1:
        idx = 'station'
    elif idx == 2:
        idx = 'about'
    elif idx == 3:
        idx = 'update'
    png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/Applications//NetRadioPersian/icons/%s.png' % str(idx)
    if fileExists(png):
        res.append(MultiContentEntryPixmapAlphaTest(pos=(65, 0), size=(457, 90), png=loadPNG(png)))
    res.append(MultiContentEntryText(pos=(0, 3), size=(800, 90), font=0, text=name))
    return res


menu_list = [_('Favorites'),
 _('Add station to favorites '),
 _('About'),
 _('Update')]

def lsSelected():
    lst = []
    count = config.plugins.Cradio.stations_count.value
    if count != 0:
        for i in range(0, count):
            name = config.plugins.Cradio.stations[i].name.value
            code = config.plugins.Cradio.stations[i].code.value
            lst.append(name)

    else:
        lst = []
    return lst


def AddOnCategoryComponent(name, png):
    res = [name]
    res.append(MultiContentEntryText(pos=(140, 5), size=(300, 35), font=0, text=name))
    res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 0), size=(100, 60), png=png))
    return res


class CCcamList(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(92)
        self.l.setFont(0, gFont('Regular', 25))


class persiancheckupdateScreen(Screen):
    skin = '\n\t<screen position="center,center" size="550,460" title="Persian Radio update" >\n\t\t<widget name="text" position="10,10" size="530,380" font="Regular;22" />\n\t\t<ePixmap name="yellow" position="200,400" zPosition="4" size="150,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications//NetRadioPersian/buttons/yellow.png" transparent="1" alphatest="on" />\n\t\t<widget name="key_yellow" position="200,400" zPosition="5" size="150,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />                \n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        info = ''
        self['key_yellow'] = Button('Update')
        self['text'] = ScrollLabel(info)
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions', 'ColorActions'], {'ok': self.close,
         'cancel': self.close,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown,
         'left': self['text'].pageUp,
         'right': self['text'].pageDown,
         'yellow': self.runupdate}, -1)
        self.update = False
        self['text'].setText('Checking for updates,please wait')
        self.timer = eTimer()
        self.timer.callback.append(self.checkforupdates)
        self.timer.start(100, 1)

    def checkforupdates(self):
        try:
            fp = urllib.urlopen('http://www.tunisia-dreambox.info/e2-addons-manager/Tunisiasat-plugins/softupdates/PurePrestige/Applications//NetRadioPersian/updates.txt')
            count = 0
            self.labeltext = ''
            s1 = fp.readline()
            s2 = fp.readline()
            s3 = fp.readline()
            s4 = fp.readline()
            s5 = fp.readline()
            s6 = fp.readline()
            s1 = s1.strip()
            s2 = s2.strip()
            s3 = s3.strip()
            s4 = s4.strip()
            s5 = s5.strip()
            s6 = s6.strip()
            self.version = s1
            self.link = s2
            self.note = s3
            self.xmlversion = s4
            self.xmllink = s5
            self.xmlnote = s6
            fp.close()
            updatestr1 = ''
            updatestr2 = ''
            if s1 == currversion:
                self.update = False
                self['key_yellow'].hide()
                updatestr1 = 'Your plugin  is uptodate'
            else:
                updatestr1 = 'New plugin version ' + s1 + ' is  available \n' + s3 + '\n Press yellow button to update'
                self.update = True
            updatestr = updatestr1
            self['text'].setText('sorry no updates available,for support dreamoem.com and persianpros.org')
        except:
            self.update == False
            self['key_yellow'].hide()
            self['text'].setText('unable to check for updates-No internet connection or server down-please check later')

    def runupdate(self):
        return
        if self.update == False:
            return
        com = self.link
        dom = 'Updating plugin to ' + self.version
        instr = 'Please wait while new version is being downloaded...\n restart enigma is required after successful installation'
        endstr = 'Press ok to exit'
        self.session.open(Console2.persianConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.finishupdate, False, instr, endstr)

    def finishupdate(self):
        self['text'].setText('update is finished,please restart enigma to run new version')

    def runxmlupdate(self):
        if self.xmlupdate == False:
            return
        com = self.xmllink
        dom = 'Updating station file to ' + self.xmlversion
        instr = 'Please wait while stations file is being downloaded...\n restart enigma is required after successful installation'
        endstr = 'Press ok to exit'
        self.session.open(Console2.persianConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.finishupdate, True, instr, endstr)


class persianAboutScreen(Screen):
    skin = '\n\t<screen position="center,center" size="550,460" title="Persian Radio " >\n\t\t<widget name="text" position="0,10" size="550,450" font="Regular;24" />\n\t\t\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        info = '\n Persian Radio  version v.3.0-Stations file version 3.0- Programmer-Mahmoud Faraj\n --------------------------- \n  Persian Radio \n enjoy more than top 50 Persian internet radio stations\n Thanks to Persian Prince and dreamoem team for continuous support \n --------------------------- \n                      WWW.DREAMOEM.COM\n https://openvision.tech'
        self['text'] = ScrollLabel(info)
        self['actions'] = ActionMap(['SetupActions'], {'ok': self.close,
         'cancel': self.close}, -1)


class persianMenuscrn(Screen):
    global HD_Res
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    skin = '\n               <screen  position="center,center" size="680,560" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications//NetRadioPersian/icons/framesd.png" position="0,0" size="680,560" transparent="1"/>\t\n\t\t<widget name="menu" position="50,90" size="580,420" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t        \n        </screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.color = '#00ffe875'
        self.transparent = True
        self['menu'] = CCcamList([])
        self.working = False
        self['actions'] = NumberActionMap(['SetupActions', 'ColorActions'], {'ok': self.okClicked,
         'cancel': self.close}, -2)
        self.onLayoutFinish.append(self.updateMenuList)

    def updateMenuList(self):
        self.menu_list = []
        for x in self.menu_list:
            del self.menu_list[0]

        list = []
        idx = 0
        for x in menu_list:
            list.append(CCcamListEntry(x, idx))
            self.menu_list.append(x)
            idx += 1

        self['menu'].setList(list)

    def Showabout(self):
        self.session.open(persianAboutScreen)

    def ShowFavorites(self):
        self.session.open(persianFavoritescrn)

    def Addstation(self):
        self.session.open(persianStationsScreen)

    def okClicked(self):
        self.keyNumberGlobal(self['menu'].getSelectedIndex())

    def keyNumberGlobal(self, idx):
        sel = self.menu_list[idx]
        if sel == _('Favorites'):
            self.session.open(persianFavoritescrn)
        elif sel == _('Add station to favorites '):
            self.session.open(persianStationsScreen)
        elif sel == _('Update'):
            self.session.open(persiancheckupdateScreen)
        elif sel == _('About'):
            self.session.open(persianAboutScreen)


class persianFavoritescrn(Screen):
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    if HD_Res:
        skin = '\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frame.png" position="0,0" size="920,600" transparent="1"/>\t\n                        <ePixmap alphatest="on" name="red" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications//NetRadioPersian/buttons/red.png" position="15,30" size="200,40" transparent="1" zPosition="4"/>\n\t\t\t<ePixmap alphatest="on" name="green" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications//NetRadioPersian/buttons/green.png" position="215,30" size="200,40" transparent="1" zPosition="4"/>\n\t\t\t<ePixmap alphatest="on" name="yellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications//NetRadioPersian/buttons/yellow.png" position="415,30" size="200,40" transparent="1" zPosition="4"/>\n\t\t\t<ePixmap alphatest="on" name="blue" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications//NetRadioPersian/buttons/blue.png" position="615,30" size="215,30" transparent="1" zPosition="4"/>\n\t\t\t<widget font="Regular;21" foregroundColor="white" halign="center" name="key_red" position="15,30" shadowColor="black" shadowOffset="-1,-1" size="150,40" transparent="1" valign="center" zPosition="5"/>\n\t\t\t<widget font="Regular;21" foregroundColor="white" halign="center" name="key_green" position="215,30" shadowColor="black" shadowOffset="-1,-1" size="150,40" transparent="1" valign="center" zPosition="5"/>\n\t\t\t<widget font="Regular;21" foregroundColor="white" halign="center" name="key_yellow" position="415,30" shadowColor="black" shadowOffset="-1,-1" size="150,40" transparent="1" valign="center" zPosition="5"/>\n\t\t\t<widget font="Regular;21" foregroundColor="white" halign="center" name="key_blue" position="615,30" shadowColor="black" shadowOffset="-1,-1" size="150,40" transparent="1" valign="center" zPosition="5"/>\n                        <ePixmap position="15,700" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications/NetRadioPersian/icons/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\t<widget name="favoritemenu" position="15,80" size="890,520"  itemHeight="40" scrollbarMode="showOnDemand" transparent="1" zPosition="4" />\n\t\t\t\n\t\t</screen>'
    else:
        skin = '\n                    <screen  position="center,center" size="580,450" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\t\n\t\t        \n            <ePixmap name="red" position="10,15" zPosition="4" size="150,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications//NetRadioPersian/buttons/red.png" transparent="1" alphatest="on" />\n\n                        <ePixmap name="green" position="160,15" zPosition="4" size="150,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications//NetRadioPersian/buttons/green.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="yellow" position="310,15" zPosition="4" size="150,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications//NetRadioPersian/buttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="blue" position="460,15" zPosition="4" size="150,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications//NetRadioPersian/buttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_red" position="10,15" zPosition="5" size="150,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="key_green" position="160,15" zPosition="5" size="150,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="key_yellow" position="310,15" zPosition="5" size="150,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="key_blue" position="460,15" zPosition="5" size="150,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="favoritemenu" position="20,50" size="600,400" scrollbarMode="showOnDemand" transparent="1" zPosition="4" />\n\t\t\t\n\t\t        \n                </screen>'

    def __init__(self, session):
        self.session = session
        self.skin = persianFavoritescrn.skin
        Screen.__init__(self, session)
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Delete'))
        self['key_yellow'] = Button(_('Add station'))
        self['key_blue'] = Button(_('About'))
        self.CurrentService = self.session.nav.getCurrentlyPlayingServiceReference()
        try:
            self.session.nav.stopService()
        except:
            pass

        self.onClose.append(self.__onClose)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.ok,
         'blue': self.ShowAbout,
         'yellow': self.Addstation,
         'green': self.Delselected,
         'red': self.close,
         'cancel': self.close}, -2)
        self.list = MenuList([])
        self['favoritemenu'] = self.list
        lst = lsSelected()
        self.list.setList(lst)
        if config.plugins.Cradio.stations_count.value == 0:
            self['key_green'].hide()
        else:
            self['key_green'].show()

    def ShowAbout(self):
        self.session.open(persianAboutScreen)

    def Addstation(self):
        self.session.openWithCallback(self.close, persianStationsScreen)

    def Showsettings(self):
        self.close

    def Delselected(self):
        try:
            sel = self['favoritemenu'].getSelectedIndex()
            config.plugins.Cradio.stations_count.value = config.plugins.Cradio.stations_count.value - 1
            config.plugins.Cradio.stations_count.save()
            del config.plugins.Cradio.stations[sel]
            config.plugins.Cradio.stations.save()
            config.plugins.Cradio.save()
            configfile.save()
            lst = []
            lst = lsSelected()
            self['favoritemenu'].setList(lst)
            if config.plugins.Cradio.stations_count.value == 0:
                self['key_green'].hide()
            else:
                self['key_green'].show()
        except:
            pass

    def playServiceStream(self, url):
        try:
            self.session.nav.stopService()
            sref = eServiceReference(4097, 0, url)
            self.session.nav.playService(sref)
            self.currentStreamingURL = url
        except:
            pass

    def ok(self):
        try:
            station = self.list.getSelectionIndex()
            currentindex = station
            cname = config.plugins.Cradio.stations[station].code.value
            tup1 = cname.split(',')
            cstation = tup1[0]
            curl = tup1[1]
            self.currentStreamingURL = ''
            self.currentStreamingStation = ''
            self.session.nav.stopService()
            self.currentStreamingStation = cstation
            self.playServiceStream(curl)
            currentservice = self.CurrentService
            self.session.open(persianplayingscrn, cstation, currentservice, currentindex)
        except:
            pass

    def playServiceStream(self, url):
        try:
            self.session.nav.stopService()
            sref = eServiceReference(4097, 0, url)
            self.session.nav.playService(sref)
            self.currentStreamingURL = url
        except:
            pass

    def __onClose(self):
        self.session.nav.playService(self.CurrentService)


class persianplayingscrn(Screen):
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    HD_Res = True
    if HD_Res:
        skin = '\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520" transparent="1"/>\t\n                        <ePixmap position="580,30" zPosition="4" size="40,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications/NetRadioPersian/icons/arrows.png" transparent="1" alphatest="on" />\n                        <ePixmap position="15,120" zPosition="4" size="610,390" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications/NetRadioPersian/icons/musichd.png" transparent="1" alphatest="on" />\n\t\t        <widget name="station" position="15,20" zPosition="1" size="560,20" font="Regular;20" transparent="1" foregroundColor="yellow" backgroundColor="yellow"/>\n                \t<widget name="titel" position="15,60" zPosition="1" size="555,130" font="Regular;24" transparent="1"  backgroundColor="#00000000"/>\n\t\t        <widget name="leagueNumberWidget" position="570,72" size="60,60" transparent="1" zPosition="4"  halign="left" font="Regular;20" foregroundColor="yellow" backgroundColor="yellow" />\n                </screen>'
    else:
        skin = '\n                     <screen  position="center,center" size="580,450" title="Persian Radio"   >\n\t\n                        <ePixmap position="530,60" zPosition="4" size="60,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications/NetRadioPersian/icons/arrows.png" transparent="1" alphatest="on" />\n\n\t\t\t<widget name="station" position="10,15" zPosition="1" size="600,30" font="Regular;20" transparent="1" foregroundColor="yellow" backgroundColor="yellow"/>\n                        <widget name="titel" position="10,45" zPosition="1" size="530,70" font="Regular;22" transparent="1"  backgroundColor="#00000000"/>\n\t\t        <widget name="leagueNumberWidget" position="520,87" size="50,40" transparent="1" zPosition="4"  halign="center" font="Regular;20" foregroundColor="yellow" backgroundColor="yellow"  />\n                </screen>'

    def __init__(self, session, stitle = None, currentservice = None, currentindex = None):
        self.skin = persianplayingscrn.skin
        Screen.__init__(self, session)
        self['titel'] = Label()
        self['station'] = Label()
        self['leagueNumberWidget'] = Label()
        self.currentindex = currentindex
        self['station'].setText(stitle)
        self.CurrentService = currentservice
        self.currentindex = currentindex
        stationscount = config.plugins.Cradio.stations_count.value
        self.stationscount = stationscount
        self['leagueNumberWidget'].setText('%d/%d' % (self.currentindex, self.stationscount))
        self.onClose.append(self.__onClose)
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evUpdatedInfo: self.__evUpdatedInfo})
        self['actions'] = ActionMap(['PiPSetupActions', 'SetupActions'], {'down': self.previousLeague,
         'up': self.nextLeague,
         'cancel': self.close,
         'size-': self.previousLeague,
         'size+': self.nextLeague}, -2)

    def nextLeague(self):
        self['titel'].setText('')
        currentindex = int(self.currentindex) + 1
        if currentindex == config.plugins.Cradio.stations_count.value:
            currentindex = 0
        self.currentindex = currentindex
        self['leagueNumberWidget'].setText('%d/%d' % (self.currentindex, self.stationscount))
        cname = config.plugins.Cradio.stations[currentindex].code.value
        tup1 = cname.split(',')
        cstation = tup1[0]
        curl = tup1[1]
        self.currentStreamingURL = ''
        self.currentStreamingStation = ''
        self.session.nav.stopService()
        self.currentStreamingStation = cstation
        self.playServiceStream(curl)
        currentservice = self.CurrentService
        self['station'].setText(cstation)

    def previousLeague(self):
        self['titel'].setText('')
        currentindex = int(self.currentindex) - 1
        if currentindex < 0:
            currentindex = config.plugins.Cradio.stations_count.value - 1
        self.currentindex = currentindex
        self['leagueNumberWidget'].setText('%d/%d' % (self.currentindex, self.stationscount))
        cname = config.plugins.Cradio.stations[currentindex].code.value
        tup1 = cname.split(',')
        cstation = tup1[0]
        curl = tup1[1]
        self.currentStreamingURL = ''
        self.currentStreamingStation = ''
        self.session.nav.stopService()
        self.currentStreamingStation = cstation
        self.playServiceStream(curl)
        currentservice = self.CurrentService
        self['station'].setText(cstation)

    def playServiceStream(self, url):
        try:
            self.session.nav.stopService()
            sref = eServiceReference(4097, 0, url)
            self.session.nav.playService(sref)
            self.currentStreamingURL = url
        except:
            pass

    def __evUpdatedInfo(self):
        sTitle = ''
        currPlay = self.session.nav.getCurrentService()
        if currPlay is not None:
            sTitle = currPlay.info().getInfoString(iServiceInformation.sTagTitle)
        self['titel'].setText(sTitle)
        return

    def cancel(self):
        self.close

    def __onClose(self):
        self.session.nav.stopService()


class persianStationsScreen(Screen):
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    if HD_Res:
        skin = '\n\t\t<screen position="center,center" size="920,600" title="Persian Radio" flags="wfNoBorder" >\n\t\t\t  <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frame.png" position="0,0" size="920,600" transparent="1"/>\t\n                          <widget name="info" position="20,0" size="800,40" valign="center" halign="center" zPosition="10" font="Regular;20" transparent="1" foregroundColor="yellow"  />\n                          <widget name="ButtonYellowtext" position="20,0" size="100,60" valign="center" halign="center" zPosition="10" font="Regular;20" transparent="1"  />\t\t\t  \n                          <widget name="ButtonYellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications/NetRadioPersian/buttons/yellow.png" position="20,10" zPosition="10" size="100,60" transparent="1" alphatest="on" />\n                          <widget name="stationmenu" position="15,60" size="890,520"  itemHeight="40" scrollbarMode="showOnDemand" transparent="1" zPosition="4" />\n                          <ePixmap position="15,50" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications/NetRadioPersian/icons/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\t                  \n        \t</screen>\n\t\t'
    else:
        skin = '\n\t\t<screen position="center,center" size="600,500" title="Persian Radio" >\n\n                          <widget name="info" position="20,0" size="600,40" valign="center" halign="center" zPosition="10" font="Regular;20" transparent="1" foregroundColor="yellow"  />\n                          \n                          <widget name="ButtonYellowtext" position="20,10" size="100,40" valign="center" halign="center" zPosition="10" font="Regular;20" transparent="1"  />\n\t\t\t  <widget name="ButtonYellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications/NetRadioPersian/buttons/yellow.png" position="20,10" zPosition="10" size="100,60" transparent="1" alphatest="on" />\n                          <widget name="stationmenu" position="10,40" size="590,425" scrollbarMode="showOnDemand" transparent="1" zPosition="4" />\n\t                  \n        \t</screen>\n\t\t'

    def __init__(self, session):
        self.skin = persianStationsScreen.skin
        Screen.__init__(self, session)
        self.CurrentService = self.session.nav.getCurrentlyPlayingServiceReference()
        self.session.nav.stopService()
        self.onClose.append(self.__onClose)
        list = []
        self['info'] = Label(_('Press OK to add to favorites'))
        self['ButtonYellow'] = Pixmap()
        self['ButtonYellowtext'] = Label(_('Play'))
        myfile = '/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Applications/NetRadioPersian/stations'
        xmlparse = xml.dom.minidom.parse(myfile)
        self.xmlparse = xmlparse
        for stations in self.xmlparse.getElementsByTagName('stations'):
            for station in stations.getElementsByTagName('station'):
                list.append(station.getAttribute('name').encode('utf8'))

        list.sort()
        self['stationmenu'] = MenuList(list)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'yellow': self.selstation,
         'ok': self.saveParameters,
         'cancel': self.close}, -2)

    def selstation(self):
        selection_station = self['stationmenu'].getCurrent()
        for stations in self.xmlparse.getElementsByTagName('stations'):
            for station in stations.getElementsByTagName('station'):
                if station.getAttribute('name').encode('utf8') == selection_station:
                    urlserver = str(station.getElementsByTagName('url')[0].childNodes[0].data)
                    pluginname = station.getAttribute('name').encode('utf8')
                    self.prombt(urlserver, pluginname)

    def prombt(self, com, dom):
        self.currentStreamingURL = ''
        self.currentStreamingStation = ''
        self.session.nav.stopService()
        self.currentStreamingStation = dom
        self.playServiceStream(com)

    def playServiceStream(self, url):
        self.session.nav.stopService()
        sref = eServiceReference(4097, 0, url)
        self.session.nav.playService(sref)
        self.currentStreamingURL = url

    def saveParameters(self):
        selection_station = self['stationmenu'].getCurrent()
        self.station = selection_station
        for stations in self.xmlparse.getElementsByTagName('stations'):
            for station in stations.getElementsByTagName('station'):
                if station.getAttribute('name').encode('utf8') == selection_station:
                    stationname = selection_station
                    url = str(station.getElementsByTagName('url')[0].childNodes[0].data)
                    self.url = url
                    self.station = stationname
                    current = initProfileConfig()
                    current.name.value = stationname
                    current.code.value = stationname + ',' + url
                    current.save()
                    config.plugins.Cradio.stations_count.value += 1
                    config.plugins.Cradio.stations_count.save()
                    config.plugins.Cradio.save()
                    configfile.save()

        self.session.open(MessageBox, _('Saved to Favorites'), MessageBox.TYPE_INFO, 2)

    def __onClose(self):
        self.session.nav.playService(self.CurrentService)


def main(session, **kwargs):
    session.open(persianMenuscrn)


def Plugins(**kwargs):
    return PluginDescriptor(name='Radio Persian', description=_('Listen to your favorites from Persian Radio'), where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], icon='/icons/Pradio.png', fnc=main)
