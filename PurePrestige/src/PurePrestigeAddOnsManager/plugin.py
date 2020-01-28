import StringIO
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Screens.ChoiceBox import ChoiceBox
from xml.dom import Node, minidom
import os
from Tools.Directories import fileExists, copyfile, pathExists, createDir, removeDir, resolveFilename, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from enigma import *
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from twisted.web.client import downloadPage, getPage
import urllib
from Components.Label import Label
from Plugins.Extensions.PurePrestige.Console2 import *
from Tools.Notifications import AddPopup
import pplayer
from enigma import eTimer, eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, getDesktop, loadPNG, loadPic
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from SpinnerSelector.plugin import downloadScreen
from urlparse import urlparse
import httplib
import urllib2
from Plugins.Extensions.PurePrestige.soupparse import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import config, ConfigDirectory, ConfigSubsection, ConfigSubList, ConfigEnableDisable, ConfigNumber, ConfigText, ConfigSelection, ConfigYesNo, ConfigPassword, getConfigListEntry, configfile
from Components.Console import Console

def wfile(st):
    fp = open('/tmp/lf.txt', 'a')
    fp.write(st)
    fp.close()


config.plugins.PurePrestige = ConfigSubsection()
config.plugins.PurePrestige.items = ConfigSubList()
config.plugins.PurePrestige.items_count = ConfigNumber(default=0)
config.plugins.PurePrestige.addstr = ConfigText(default='panel', fixed_size=False)
currversion = '6.7'
TMP_IMPORT_PWD = '/tmp/download_tmp'

def gethostname():
    path = '/etc/hostname'
    hostname = 'None'
    if os.path.exists(path):
        f = open(path, 'r')
        hostname = f.read()
        f.close()
        if 'dm800se' in hostname:
            return 'dm800se'
        if 'dm8000' in hostname:
            return 'dm8000'
        if 'dm800' in hostname:
            return 'dm800hd'
        if 'dm500' in hostname:
            return 'dm500hd'
        if 'dm7020' in hostname:
            return 'dm7020hd'
        return 'None'
    return 'None'


hostname = gethostname()

def checkhostname(ipkfile):
    print 'hostname', hostname
    print 'ipkfile', ipkfile
    if 'mips32el' in ipkfile:
        if 'mips32el-nf' in ipkfile:
            if hostname == 'dm800hd':
                return True
            else:
                return False
        elif hostname == 'dm800hd':
            return False
        else:
            return True

    else:
        return True


def getdigitversion(ipkversionstr):
    tstr = ''
    e = list(ipkversionstr)
    for j in e:
        if j.isdigit():
            tstr = tstr + str(j)

    return tstr


def createstatus():
    try:
        fp = os.popen('opkg list')
        opkgdata = fp.readlines()
        statusfile = open('/tmp/status', 'w')
        statusfile.writelines(opkgdata)
        statusfile.close()
    except:
        pass


createstatus()

def getipkversion(ipkfile):
    try:
        ipkfile = str(os.path.basename(ipkfile))
        ipkfile = ipkfile.replace('.ipk', '')
        ipkparts = ipkfile.split('_')
        addon = ipkparts[0]
        statusdata = open('/tmp/status', 'r').readlines()
        print 'addon', addon
        for item in statusdata:
            if addon in item:
                return 'remove'

        return 'install'
    except:
        print 'failed'
        return 'install'


def getipkversion2(ipkfile):
    try:
        ipkfile = str(os.path.basename(ipkfile))
        ipkfile = ipkfile.replace('.ipk', '')
        ipkparts = ipkfile.split('_')
        fp = os.popen('opkg list ' + ipkparts[0])
        data = fp.readlines()
        print 'data0', data[0]
        return 'remove'
    except:
        print 'failed'
        return 'install'


def dirsremove(folder):
    try:
        for root, dirs, files in os.walk(folder):
            for f in files:
                os.remove(os.path.join(root, f))

            for d in dirs:
                removeDir(os.path.join(root, d))

    except:
        pass


def deletefiles(dr):
    for i in range(64):
        if os.path.isfile(dr + '/wait%d.png' % (i + 1)):
            os.remove(dr + '/wait%d.png' % (i + 1))


def copyfiles(src, dst):
    for i in range(64):
        if os.path.isfile(src + '/wait%d.png' % (i + 1)):
            copyfile(src + '/wait%d.png' % (i + 1), dst)


def savespinner_default():
    spinner_path_tmp1 = '/usr/share/enigma2/spinner_tmp'
    spinner_path_tmp = '/usr/share/enigma2/spinner_tmp/spinner'
    spinner_path_default = '/usr/share/enigma2/skin_default/spinner'
    if os.path.isdir(spinner_path_tmp1):
        pass
    else:
        os.mkdir(spinner_path_tmp1)
    if os.path.isdir(spinner_path_tmp):
        pass
    else:
        os.mkdir(spinner_path_tmp)
    try:
        deletefiles(spinner_path_tmp)
        copyfiles(spinner_path_default, spinner_path_tmp)
    except:
        pass


def restorespinner_default():
    spinner_path_tmp1 = '/usr/share/enigma2/spinner_tmp'
    spinner_path_tmp = '/usr/share/enigma2/spinner_tmp/spinner'
    spinner_path_default1 = '/usr/share/enigma2/skin_default'
    spinner_path_default = '/usr/share/enigma2/skin_default/spinner'
    if os.path.isdir(spinner_path_default1):
        pass
    else:
        os.mkdir(spinner_path_default1)
    if os.path.isdir(spinner_path_default):
        pass
    else:
        os.mkdir(spinner_path_default)
    try:
        deletefiles(spinner_path_default)
        copyfiles(spinner_path_tmp, spinner_path_default)
    except:
        pass


def freespace():
    try:
        diskSpace = os.statvfs('/')
        capacity = float(diskSpace.f_bsize * diskSpace.f_blocks)
        available = float(diskSpace.f_bsize * diskSpace.f_bavail)
        fspace = round(float(available / 1048576.0), 2)
        tspace = round(float(capacity / 1048576.0), 1)
        spacestr = 'Free space(' + str(fspace) + 'MB) Total space(' + str(tspace) + 'MB)'
        return spacestr
    except:
        return ''


class AddSearchStrScreen(Screen, ConfigListScreen):
    skin = '\n\t\t<screen name="DreamBuddyAdd" position="center,center" size="560,300" title="Add text to search">\n\t\t\t<widget name="config" position="10,100" size="540,200" scrollbarMode="showOnDemand" />\n\t\t\t<ePixmap name="red"    position="0,10"   zPosition="4" size="140,40" pixmap="buttons/key_red.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="green"  position="140,10" zPosition="4" size="140,40" pixmap="buttons/key_green.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="yellow" position="280,10" zPosition="4" size="140,40" pixmap="buttons/key_yellow.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="blue"   position="420,10" zPosition="4" size="140,40" pixmap="buttons/key_blue.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_red" position="0,5" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="key_green" position="140,5" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="key_yellow" position="280,10" zPosition="5" size="140,40" valign="center" halign="center"  font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="key_blue" position="420,10" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.searchstr = config.plugins.PurePrestige.addstr.value
        self['key_red'] = Button(_('Cancel'))
        self['key_green'] = Button(_('OK'))
        self['key_yellow'] = Button('')
        self['key_blue'] = Button('')
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.save,
         'green': self.save,
         'red': self.Exit,
         'cancel': self.Exit}, -2)
        cfglist = []
        cfglist.append(getConfigListEntry(_('Enter addon name-partial or complete'), config.plugins.PurePrestige.addstr))
        ConfigListScreen.__init__(self, cfglist, session)

    def save(self):
        ConfigListScreen.keySave(self)
        configfile.save()
        self.close()

    def Exit(self):
        config.plugins.PurePrestige.addstr.value = ''
        self.close()


class PurePrestigeaddonsupdatesScreen(Screen):
    global HD_Res
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    if HD_Res == True:
        skin = '\n        \t\n                <screen name="PurePrestigeaddonsupdatesScreen" position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frametop.png" position="0,0" size="920,600"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frameleft.png" position="0,10" size="10,580"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frameright.png" position="910,10" size="10,580"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framebottom.png" position="0,590" size="920,10"/>\t\n                \n\t\t<widget name="text" position="30,30" size="865,555" font="Regular;22"  transparent="1" zPosition="2"  />\n                </screen>'
    else:
        skin = '\n        \t\n                <screen name="PurePrestigeaddonsupdatesScreen" position="center,center" size="580,450" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frametop.png" position="0,0" size="580,450"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frameleft.png" position="0,7" size="6,435"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frameright.png" position="573,7" size="6,435"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framebottom.png" position="0,442" size="580,7"/>\t\n                \n\t\t<widget name="text" position="20,20" size="540,410" font="Regular;22"  transparent="1" zPosition="2"  />\n                </screen>'

    def __init__(self, session, newsurl = None, selectedservername = None):
        self.skin = PurePrestigeaddonsupdatesScreen.skin
        Screen.__init__(self, session)
        info = 'Getting updates,please wait...'
        self.newsurl = newsurl
        self.selectedservername = selectedservername
        self['text'] = ScrollLabel(info)
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'ok': self.close,
         'cancel': self.close,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown,
         'left': self['text'].pageUp,
         'right': self['text'].pageDown}, -1)
        newtitle = self.selectedservername + ' server updates'
        self.setTitle(newtitle)
        self.timer = eTimer()
        self.timer.callback.append(self.downloadupdates)
        self.timer.start(100, 1)

    def downloadupdates(self):
        try:
            fp = urllib.urlopen(self.newsurl)
            count = 0
            self.labeltext = ''
            while 1:
                s = fp.readline()
                count += 1
                self.labeltext += str(s)
                if not s:
                    break

            fp.close()
            self['text'].setText(self.labeltext)
        except:
            self['text'].setText('unable download data')


class LSKServersScreen(Screen):
    skin = '\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\t\n                <widget name="tspace" position="5,10" zPosition="4" size="630,25" font="Regular;22" foregroundColor="yellow" transparent="1" halign="center" valign="center" />\n                <ePixmap position="15,34" size="550,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n  \t\t\n                <widget name="list" position="15,40" size="610,410" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t        \n        </screen>'

    def __init__(self, session):
        self.skin = LSKServersScreen.skin
        Screen.__init__(self, session)
        self.serversnames = []
        self.serversurls = []
        self.serversnames = ['Plugins',
         'Cams',
         'Cams_Configs',
         'Feeds',
         'Skins',
         'Settings',
         'Picons',
         'BootLogo',
         'Multiboot',
         'Drivers']
        self.serversurls = ['Plugins',
         'Cams',
         'Cams_Configs',
         'Feeds',
         'Skins',
         'Settings',
         'Picons',
         'BootLogo',
         'Multiboot',
         'Drivers']
        self['tspace'] = Label('LSK addons groups')
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okClicked,
         'cancel': self.close}, -2)
        self.ListToMulticontent()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.serversnames
        self['list'].l.setItemHeight(35)
        self['list'].l.setFont(0, gFont('Regular', 25))
        for i in range(0, len(self.events)):
            res.append(MultiContentEntryText(pos=(0, 5), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
            res.append(MultiContentEntryText(pos=(60, 5), size=(430, 120), font=0, flags=RT_HALIGN_LEFT, text=self.events[i], color=16777215, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()

    def okClicked(self):
        selectedserverurl = ''
        try:
            selection = self['list'].getCurrent()
            cindex = self['list'].getSelectionIndex()
            selectedserverurl = 'http://www.linux-sat-keys.com/addons/xml/' + str(self.serversurls[cindex]) + '.xml'
            selectedservername = self.serversnames[cindex]
            self.session.open(PurePrestigeServerGroups, selectedserverurl, selectedservername)
        except:
            pass


class FeedsServersScreen(Screen):
    skin = '\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\t\n                <widget name="tspace" position="5,10" zPosition="4" size="630,25" font="Regular;22" foregroundColor="yellow" transparent="1" halign="center" valign="center" />\n                <ePixmap position="15,34" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n  \t\t\n                <widget name="list" position="15,40" size="610,410" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t        \n        </screen>'

    def __init__(self, session):
        self.skin = FeedsServersScreen.skin
        Screen.__init__(self, session)
        self.serversnames = []
        self.serversurls = []
        self.serversnames = ['Oozoon Feeds', 'Newnigma2 Feeds', 'Dreamboxupdate Feeds']
        self.serversurls = ['http://oozoon-dreamboxupdate.de/opendreambox/2.0/experimental/index.html', 'http://feed.newnigma2.to/stable/', 'http://dreamboxupdate.com/opendreambox/2.0.0/']
        self['tspace'] = Label('Dreambox Feeds')
        self.list = []
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okClicked,
         'cancel': self.close}, -2)
        self.ListToMulticontent()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.serversnames
        self['list'].l.setItemHeight(35)
        self['list'].l.setFont(0, gFont('Regular', 25))
        for i in range(0, len(self.events)):
            res.append(MultiContentEntryText(pos=(0, 5), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
            res.append(MultiContentEntryText(pos=(60, 5), size=(430, 120), font=0, flags=RT_HALIGN_LEFT, text=self.events[i], color=16777215, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()

    def okClicked(self):
        selectedserverurl = ''
        try:
            selection = self['list'].getCurrent()
            cindex = self['list'].getSelectionIndex()
            selectedserverurl = 'http://www.linux-sat-keys.com/addons/xml/' + str(self.serversurls[cindex]) + '.xml'
            selectedservername = self.serversnames[cindex]
            self.session.open(FeedsServerGroups, selectedserverurl, selectedservername)
        except:
            pass


class FeedsServerGroups(Screen):
    global HD_Res
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    if HD_Res == True:
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frame.png" position="0,0" size="920,600" transparent="1"/>\t\n                <widget name="tspace" position="20,10" zPosition="2" size="910,45" font="Regular;23" foregroundColor="yellow" transparent="1" halign="center" valign="center" />\n                <ePixmap position="15,60" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\n                <widget name="list" position="20,65" size="880,405" scrollbarMode="showOnDemand" transparent="1" zPosition="4" />\n\t\t<ePixmap position="15,490" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\n                <ePixmap name="green" position="360,510" zPosition="4" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="360,520" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                        \n\t\t\t\n\t\t<eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />\n\t\t<widget name="info" position="50,50" zPosition="4" size="850,300" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t\t<widget name="fspace" position="0,320" zPosition="4" size="600,80" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />\n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="580,450" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\t\n                <widget name="tspace" position="5,10" zPosition="4" size="630,25" font="Regular;20" foregroundColor="yellow" transparent="1" halign="center" valign="center" />\n                <ePixmap position="15,34" size="550,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n  \n                 <widget name="list" position="15,38" size="610,320" scrollbarMode="showOnDemand" transparent="1" zPosition="4" />\n\t\t<ePixmap name="green" position="250,383" zPosition="4" size="113,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="250,395" zPosition="5" size="113,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                        \n\t\t\t\n\t\t<eLabel position="44,75" zPosition="-1" size="63,52" backgroundColor="#222222" />\n\t\t<widget name="info" position="32,38" zPosition="4" size="596,225" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t\t<widget name="fspace" position="0,240" zPosition="4" size="476,60" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />\n                </screen>'

    def __init__(self, session, selectedserverurl = None, selectedservername = None):
        self.skin = FeedsServerGroups.skin
        Screen.__init__(self, session)
        self['tspace'] = Label('')
        self['key_green'] = Button('Search')
        self['info'] = Label()
        self['fspace'] = Label()
        self.selectedservername = selectedservername
        self['tspace'] = Label(self.selectedservername)
        self.selectedserverurl = selectedserverurl
        newsurl = selectedserverurl.replace('.xml', '.txt')
        self.newsurl = newsurl
        self.list = []
        self['list'] = MenuList([])
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        if self.selectedservername == 'Oozoon Feeds':
            self.groups = ['mips32el-nf', 'mips32el']
            self.selectedserverurl = 'http://oozoon-dreamboxupdate.de/opendreambox/2.0/'
            self['info'].setText('')
            self['list'].setList(self.groups)
            self.downloading = True
        elif self.selectedservername == 'Merlin Feeds':
            self.groups = ['DM500HD',
             'DM800',
             'DM800SE',
             'DM7020HD',
             'DM8000']
            self.selectedserverurl = 'http://feed.dreambox-tools.info/'
            self['info'].setText('')
            self['list'].setList(self.groups)
            self.downloading = True
        elif self.selectedservername == 'Newnigma2 Feeds':
            self.groups = ['mips32el', 'mips32el-nf(only dm800)']
            self.selectedserverurl = 'http://feed.newnigma2.to/unstable/4.0/'
            self['info'].setText('')
            self['list'].setList(self.groups)
            self.downloading = True
        elif self.selectedservername == 'Dreamboxupdate Feeds':
            self.groups = ['dm500hd',
             'dm800',
             'dm800se',
             'dm7020hd',
             'dm8000']
            self.selectedserverurl = 'http://www.dreamboxupdate.com/opendreambox/2.0.0/'
            self['info'].setText('')
            self['list'].setList(self.groups)
            self.downloading = True
        elif self.selectedservername == 'OpenPli Feeds':
            self.groups = ['all',
             'dm800',
             'mipsel',
             '3rd-party']
            self.selectedserverurl = 'http://downloads.pli-images.org/feeds/openpli-2.1/dm800/'
            self['info'].setText('')
            self['list'].setList(self.groups)
            self.downloading = True
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okClicked,
         'green': self.addsearchstr,
         'cancel': self.close}, -2)
        self.onShow.append(self.UpdateTitle)

    def UpdateTitle(self):
        self.setTitle(self.selectedservername)

    def addsearchstr(self):
        try:
            from Screens.VirtualKeyBoard import VirtualKeyBoard
            self.session.openWithCallback(self.dosearch, VirtualKeyBoard, title=_('Enter your search term(s)'), text=config.plugins.PurePrestige.addstr.value)
        except:
            self.session.openWithCallback(self.dosearch, AddSearchStrScreen)

    def dosearch(self, result):
        if result:
            config.plugins.PurePrestige.addstr.value = result
            if self.downloading == True:
                try:
                    selection = str(self['list'].getCurrent())
                    searchstr = config.plugins.PurePrestige.addstr.value
                    if searchstr:
                        self.session.open(PurePrestigePackageFeedssearch, selection, self.selectedservername, searchstr)
                        return
                except:
                    pass

    def okClicked(self):
        if self.downloading == True:
            try:
                selection = str(self['list'].getCurrent())
                self.session.open(PurePrestigePackageFeeds, selection, self.selectedservername)
                return
            except:
                pass

        else:
            self.close


class PurePrestigeServersScreen(Screen):
    global HD_Res
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    skin = '\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\t\n                <widget name="tspace" position="5,10" zPosition="4" size="630,25" font="Regular;22" foregroundColor="yellow" transparent="1" halign="center" valign="center" />\n                <ePixmap position="15,34" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n  \t\t\n                <widget name="list" position="15,40" size="610,470" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t        \n        </screen>'

    def __init__(self, session, serversnames, serversurls):
        self.skin = PurePrestigeServersScreen.skin
        Screen.__init__(self, session)
        self.serversnames = serversnames
        self.serversurls = serversurls
        self.list = []
        self['tspace'] = Label('PurePrestige servers')
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okClicked,
         'cancel': self.close}, -2)
        self.ListToMulticontent()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.serversnames
        self['list'].l.setItemHeight(65)
        self['list'].l.setFont(0, gFont('Regular', 25))
        for i in range(0, len(self.events)):
            res.append(MultiContentEntryText(pos=(0, 25), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
            res.append(MultiContentEntryText(pos=(60, 25), size=(430, 120), font=0, flags=RT_HALIGN_LEFT, text=self.events[i], color=16777215, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()

    def okClicked(self):
        selectedserverurl = ''
        try:
            selection = self['list'].getCurrent()
            cindex = self['list'].getSelectionIndex()
            selectedserverurl = self.serversurls[cindex]
            selectedservername = self.serversnames[cindex]
            if 'LSK' in selectedservername:
                self.session.open(LSKServersScreen)
                return
            if 'Dreambox Feeds' in selectedservername:
                self.session.open(FeedsServersScreen)
                return
            self.session.open(PurePrestigeServerGroups, selectedserverurl, selectedservername)
        except:
            pass


class PurePrestigeServerGroups(Screen):
    global HD_Res
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    if HD_Res == True:
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frame.png" position="0,0" size="920,600" transparent="1"/>\t\n                                <widget name="tspace" position="20,10" zPosition="2" size="910,45" font="Regular;23" foregroundColor="yellow" transparent="1" halign="center" valign="center" />\n                                <ePixmap position="15,60" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\n                <widget name="list" position="20,65" size="880,405" scrollbarMode="showOnDemand" transparent="1" zPosition="4" />\n\t\t<ePixmap position="15,490" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\n                <ePixmap name="yellow" position="560,510" zPosition="4" size="180,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_yellow" position="555,520" zPosition="5" size="180,40" valign="center" halign="left" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t\n                <ePixmap name="green" position="200,510" zPosition="4" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="200,520" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                        \n\t\t\t\n\t\t<eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />\n\t\t<widget name="info" position="50,50" zPosition="4" size="850,300" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t\t<widget name="fspace" position="0,320" zPosition="4" size="600,80" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />\n     \n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\t\n                <widget name="tspace" position="5,10" zPosition="4" size="560,25" font="Regular;18" foregroundColor="yellow" transparent="1" halign="center" valign="center" />\n                <ePixmap position="15,34" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n  \n                 <widget name="list" position="15,38" size="610,400" scrollbarMode="showOnDemand" transparent="1" zPosition="4" />\n\t\t<ePixmap name="yellow" position="380,453" zPosition="4" size="113,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_yellow" position="370,465" zPosition="5" size="150,30" valign="center" halign="left" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="green" position="130,453" zPosition="4" size="113,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="125,465" zPosition="5" size="113,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                                           \n\t\t\t\n\t\t<eLabel position="44,75" zPosition="-1" size="63,52" backgroundColor="#222222" />\n\t\t<widget name="info" position="32,38" zPosition="4" size="596,225" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t\t<widget name="fspace" position="0,240" zPosition="4" size="476,60" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />\n                <ePixmap position="15,442" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n                  \n                \n                </screen>'

    def __init__(self, session, selectedserverurl = None, selectedservername = None):
        self.skin = PurePrestigeServerGroups.skin
        Screen.__init__(self, session)
        self['tspace'] = Label('')
        self['key_yellow'] = Button(_('Server updates'))
        self['key_green'] = Button(_('Search'))
        self.selectedservername = selectedservername
        self.selectedserverurl = selectedserverurl
        newsurl = selectedserverurl.replace('.xml', '.txt')
        self.newsurl = newsurl
        self.list = []
        self.getfreespace()
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        self['info'] = Label()
        self['fspace'] = Label()
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['info'].setText('Downloading addons groups,please wait..')
        self.timer = eTimer()
        self.timer.callback.append(self.downloadxmlpage)
        self.timer.start(100, 1)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okClicked,
         'yellow': self.shownews,
         'green': self.addsearchstr,
         'cancel': self.close}, -2)

    def getfreespace(self):
        fspace = freespace()
        self.freespace = fspace
        self['tspace'].setText(fspace)

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.names
        self['list'].l.setItemHeight(40)
        self['list'].l.setFont(0, gFont('Regular', 24))
        for i in range(0, len(self.events)):
            res.append(MultiContentEntryText(pos=(0, 5), size=(2, 30), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
            res.append(MultiContentEntryText(pos=(30, 5), size=(540, 30), font=0, flags=RT_HALIGN_LEFT, text=self.events[i], color=16777215, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()

    def updateable(self):
        try:
            selection = str(self.names[0])
            lwords = selection.split('_')
            lv = lwords[1]
            self.lastversion = lv
            if float(lv) == float(currversion):
                return False
            if float(lv) > float(currversion):
                return True
            return False
        except:
            return False

    def ShowAbout(self):
        self.session.open(AboutScreen)

    def shownews(self):
        if self.selectedservername == 'Dreambox Feeds':
            return
        self.session.open(PurePrestigeaddonsupdatesScreen, self.newsurl, self.selectedservername)

    def downloadxmlpage(self):
        url = self.selectedserverurl
        getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print str(error)
        self['info'].setText('Addons Download Failure,No internet connection or server down !')
        self.downloading = False

    def _gotPageLoad(self, data):
        try:
            newdata = ''
            if self.selectedservername == 'Ferrari_addons_Server':
                newdata = data.replace('FERRARI', '****')
                newdata = newdata.replace('8a8f8', '****')
                self.xml = newdata
            else:
                self.xml = data
        except:
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
            for plugins in xmlstr.getElementsByTagName('plugins'):
                item = plugins.getAttribute('cont').encode('utf8')
                if 'PurePrestige' in item:
                    for plugin in plugins.getElementsByTagName('plugin'):
                        tsitem = plugin.getAttribute('name').encode('utf8')
                        if 'Tspanel_' in tsitem:
                            item = self.getupdateversion(tsitem, item)

                self.names.append(item)

            self.list = list
            self['info'].setText('')
            self.downloading = True
            self.ListToMulticontent()
        except:
            self.downloading = False
            self['info'].setText('Error processing server addons data')

    def getupdateversion(self, tsitem, item):
        newitem = item
        try:
            a = []
            a = tsitem.split('_')
            lastversion = a[1]
            newitem = newitem.replace('_New update', '')
            if str(lastversion) == str(currversion):
                return newitem
            newitem = newitem + '_New update'
            return newitem
        except:
            return newitem

    def addsearchstr(self):
        try:
            from Screens.VirtualKeyBoard import VirtualKeyBoard
            self.session.openWithCallback(self.dosearch, VirtualKeyBoard, title=_('Enter your search term(s)'), text=config.plugins.PurePrestige.addstr.value)
        except:
            self.session.openWithCallback(self.dosearch, AddSearchStrScreen)

    def dosearch(self, result):
        print result
        config.plugins.PurePrestige.addstr.value = result
        if self.downloading == True:
            try:
                selection = str(self['list'].getCurrent())
                searchstr = config.plugins.PurePrestige.addstr.value
                print selection
                if searchstr:
                    self.session.open(Ipkgsearch, self.xmlparse, selection, self.names, searchstr)
                    return
            except:
                pass

    def okClicked(self):
        if self.downloading == True:
            try:
                cindex = self['list'].getSelectionIndex()
                selection = str(self.names[cindex])
                if self.selectedservername == 'Dreambox Feeds':
                    self.session.open(PurePrestigedreamboxupdates, selection)
                    return
                if 'logo' in str.lower(selection):
                    self.session.openWithCallback(self.getfreespace, PurePrestigeIpkgLogos, self.xmlparse, selection)
                elif 'skin' in str.lower(selection):
                    self.session.openWithCallback(self.getfreespace, PurePrestigeIpkgLogos, self.xmlparse, selection)
                elif 'spinner' in str.lower(selection):
                    try:
                        savespinner_default()
                        self.session.openWithCallback(restorespinner_default, PurePrestigeIpkgLogos, self.xmlparse, selection)
                    except:
                        pass

                elif 'tutorial' in str.lower(selection):
                    self.session.openWithCallback(self.getfreespace, IpkgTutorials, self.xmlparse, selection)
                else:
                    self.session.openWithCallback(self.getfreespace, PurePrestigeIpkgPlugins, self.xmlparse, selection)
            except:
                pass

        else:
            self.close


class PurePrestigePackageFeedssearch(Screen):
    if HD_Res == True:
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frame.png" position="0,0" size="920,600"/>\t\n                <widget name="list" position="50,50" size="850,420" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<ePixmap position="15,490" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\n                \n\t        <ePixmap name="green" position="140,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="110,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n        \t<ePixmap name="blue" position="390,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_blue" position="360,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="yellow" position="600,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t\t  \n                <widget name="key_yellow" position="570,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                          \n\t\t\t<widget name="info" position="150,50" zPosition="4" size="300,300" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t\t        <widget name="fspace" position="0,320" zPosition="4" size="600,80" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />\n                <widget name="info2" position="0,550" zPosition="4" size="920,30" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\t\n                <widget name="list" position="32,38" size="586,385" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<ePixmap position="15,440" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\n                \n\t        <ePixmap name="green" position="118,443" zPosition="4" size="101,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="108,470" zPosition="5" size="126,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n        \t<ePixmap name="blue" position="276,443" zPosition="4" size="101,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_blue" position="255,470" zPosition="5" size="126,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="yellow" position="420,443" zPosition="4" size="101,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t\t  \n                <widget name="key_yellow" position="412,470" zPosition="5" size="126,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                          \n\t\t\t<widget name="info" position="150,50" zPosition="4" size="360,300" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t\t        <widget name="fspace" position="0,320" zPosition="4" size="640,80" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />\n                <widget name="info2" position="0,490" zPosition="4" size="640,30" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n                </screen>'

    def __init__(self, session, selectedservername = None, globalservername = None, searchstr = None):
        self.skin = PurePrestigePackageFeedssearch.skin
        Screen.__init__(self, session)
        self.searchstr = searchstr
        self['key_green'] = Button(_('Install'))
        self['key_yellow'] = Button()
        self['key_blue'] = Button()
        self.globalservername = globalservername
        self.selectedservername = selectedservername
        self.newsurl = ''
        self.list = []
        self['list'] = MenuList([])
        self['info'] = Label()
        self['info2'] = Label('Press Menu for Advanced install')
        self['fspace'] = Label()
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        self['list'].onSelectionChanged.append(self.selectionChanged)
        list = []
        self.list = list
        self.status = []
        self.slist = []
        self['info'].setText('Searching,please wait..')
        self.timer = eTimer()
        self.timer.callback.append(self.downloadxmlpage)
        self.timer.start(100, 1)
        self['actions'] = ActionMap(['SetupActions', 'MenuActions', 'ColorActions'], {'ok': self.selclicked,
         'menu': self.advanceinstall,
         'cancel': self.close,
         'green': self.selgreen}, -2)
        self.onShow.append(self.selectionChanged)
        self.getfreespace()
        self.filebaseurl = ''

    def getiteOpenPlimurl(self):
        self.rooturl = 'http://downloads.pli-images.org/feeds/openpli-2.1/dm800/'
        self.groupurl = self.selectedservername + '/'
        self.url = self.rooturl + self.groupurl
        self.filebaseurl = self.rooturl + self.groupurl
        self.truefilebaseurl = self.filebaseurl
        if self.selectedservername == '3rd-party':
            self.url = self.rooturl + self.groupurl + 'Packages.gz'
        else:
            self.url = self.rooturl + self.groupurl + 'Packages'

    def getiteDreamboxupdatesmurl(self):
        self.rooturl = 'http://dreamboxupdate.com/opendreambox/2.0.0/'
        self.groupurl = self.selectedservername + '/'
        self.url = self.rooturl + self.groupurl
        self.filebaseurl = ''
        if self.selectedservername == 'dm800':
            self.truefilebaseurl = self.rooturl + 'mips32el-nf/'
            self.filebaseurl = '/opendreambox/2.0.0/mips32el-nf/'
        else:
            self.truefilebaseurl = self.rooturl + 'mips32el/'
            self.filebaseurl = '/opendreambox/2.0.0/mips32el/'

    def getiteNewnigma2murl(self):
        self.rooturl = 'http://feed.newnigma2.to/unstable/4.0/'
        if self.selectedservername == 'mips32el':
            self.groupurl = self.selectedservername + '/'
        elif 'mips32el-nf' in self.selectedservername:
            self.groupurl = 'mips32el-nf/'
        self.url = self.rooturl + self.groupurl
        self.filebaseurl = ''
        self.truefilebaseurl = self.rooturl + self.groupurl

    def getiteMerlinmurl(self):
        self.rooturl = 'http://feed.dreambox-tools.info/'
        self.groupurl = 'index.php?dir=' + self.selectedservername + '/'
        self.url = self.rooturl + self.groupurl
        self.filebaseurl = '/' + self.groupurl + '&amp;file='
        self.truefilebaseurl = self.rooturl + 'feeds/' + self.selectedservername + '/'

    def getiteOozoonmurl(self):
        self.rooturl = 'http://oozoon-dreamboxupdate.de/opendreambox/2.0/experimental/'
        if self.selectedservername == 'mips32el':
            self.groupurl = 'mips32el/'
            self.url = self.rooturl + self.groupurl + 'index.html'
        elif self.selectedservername == 'mips32el-nf':
            self.groupurl = 'mips32el-nf/'
            self.url = self.rooturl + self.groupurl + 'index.html'
        self.truefilebaseurl = self.rooturl + self.groupurl

    def downloadxmlpage(self):
        if self.globalservername == 'OpenPli Feeds':
            self.getiteOpenPlimurl()
            getPage(self.url).addCallback(self._gotPageLoadOpenPli).addErrback(self.errorLoad)
            return
        if self.globalservername == 'Oozoon Feeds':
            self.getiteOozoonmurl()
        elif self.globalservername == 'Merlin Feeds':
            self.getiteMerlinmurl()
        elif self.globalservername == 'Newnigma2 Feeds':
            self.getiteNewnigma2murl()
        elif self.globalservername == 'Dreamboxupdate Feeds':
            self.getiteDreamboxupdatesmurl()
        else:
            return
        getPage(self.url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print str(error)
        self['info'].setText('Addons Download Failure,No internet connection or server down !')
        self.downloading = False

    def downloadurl(self, data):
        mdata = ''
        try:
            filename = '/tmp/package.gz'
            file = open(filename, 'w')
            file.write(data)
            file.close()
            print 'done'
            self['info'].setText('')
            Console().ePopen('gunzip -c /tmp/package.gz > /tmp/package')
            fp = open('/tmp/package', 'r')
            mdata = fp.read()
            fp.close()
            print mdata
        except:
            self['info'].setText(str('Sorry,error in getting feeds'))
            mdata = ''

        try:
            os.remove('/tmp/package.gz')
            os.remove('/tmp/package')
        except:
            print 'files not removed'

        print 'remove files'
        return mdata

    def _gotPageLoadOpenPli(self, data):
        try:
            mdata = ''
            if 'party' in self.selectedservername:
                mdata = self.downloadurl(data)
                data = mdata
        except:
            self['info'].setText(self.selectedservername)

        self.xml = data
        self['info'].setText('')
        try:
            if self.xml:
                pass
            else:
                self.downloading = False
                self['info'].setText('Addons Download Failure,No internet connection or server down !')
                return
            self.data = []
            icount = 0
            list = []
            links = []
            list = []
            self.list = list
            a = []
            buf = StringIO.StringIO(data)
            a = buf.readlines()
            print a[0]
            print a[1]
            b = []
            ref = ''
            for i in range(0, len(a)):
                if 'Filename:' in a[i]:
                    fname = a[i].replace('Filename:', '')
                    fname = fname.strip()
                    ref = self.filebaseurl + fname
                    print ref
                    ref = ref.replace(self.filebaseurl, '')
                    processmode = getipkversion(ref)
                    if self.searchstr.lower() in ref.lower():
                        links.append(ref)
                        item = ref
                        newitem = item.replace(self.filebaseurl, '')
                        newitem = item.replace('enigma2-', '')
                        newitem = newitem.replace('.ipk', '')
                        newitem = newitem.replace('mipsel/', '')
                        newitem = newitem.replace('_mipsel', '')
                        newitem = newitem.replace('plugin-', '')
                        list.append([str(newitem), processmode])

            self.list = list
            self.links = links
            if len(self.list) == 0:
                self['info'].setText('No addons found')
            else:
                self['info'].setText('')
            self.downloading = True
        except:
            self.downloading = False
            self['info'].setText('Error processing server addons data')
            return

        self.getfreespace()
        self.ListToMulticontent()

    def _gotPageLoad(self, data):
        self.xml = data
        self['info'].setText('')
        try:
            if self.xml:
                pass
            else:
                self.downloading = False
                self['info'].setText('Addons Download Failure,No internet connection or server down !')
                return
            self.data = []
            icount = 0
            list = []
            soup = BeautifulSoup(data)
            links = []
            list = []
            self.list = list
            for tag in soup.findAll('a', href=True):
                ref = tag['href']
                if ref.endswith('.ipk'):
                    ref = ref.replace(self.filebaseurl, '')
                    processmode = getipkversion(ref)
                    if self.searchstr.lower() in ref.lower():
                        links.append(ref)
                        item = ref
                        newitem = item.replace(self.filebaseurl, '')
                        newitem = item.replace('enigma2-', '')
                        newitem = newitem.replace('.ipk', '')
                        newitem = newitem.replace('mipsel/', '')
                        newitem = newitem.replace('_mipsel', '')
                        newitem = newitem.replace('plugin-', '')
                        list.append([str(newitem), processmode])

            self.list = list
            self.links = links
            if len(self.list) == 0:
                self['info'].setText('No addons found')
            else:
                self['info'].setText('')
            self.downloading = True
        except:
            self.downloading = False
            self['info'].setText('Error processing server addons data')
            return

        self.getfreespace()
        self.ListToMulticontent()

    def selectionChanged(self):
        try:
            selection = self['list'].getCurrent()
            cindex = self['list'].getSelectionIndex()
            self.ipkgremove = False
            self.pngtext = self.list[cindex][1]
            if self.pngtext == 'install':
                self['key_green'].setText('Install')
            elif self.pngtext == 'update':
                self['key_green'].setText('Update')
            elif self.pngtext == 'remove':
                self['key_green'].setText('Remove')
        except:
            pass

    def refresh(self):
        if self.ipkgremove == False:
            png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/green.png')
            txt = 'remove'
        else:
            png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/grey.png')
            txt = 'install'
        idx = self['list'].getSelectionIndex()
        self.list[idx][1] = txt
        item = self.list[idx][0]
        res = []
        res.append(MultiContentEntryText(pos=(0, 1), size=(5, 30), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
        res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 1), size=(30, 30), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(30, 1), size=(580, 30), font=0, flags=RT_HALIGN_LEFT, text=item, color=16777215, color_sel=16777215))
        self.theevents[idx] = res
        self['list'].l.setList(self.theevents)
        res = []
        self['list'].show()
        self.getfreespace()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self['list'].l.setItemHeight(35)
        self['list'].l.setFont(0, gFont('Regular', 22))
        self.menulist = []
        for i in range(0, len(self.list)):
            pngtext = str(self.list[i][1])
            item = str(self.list[i][0])
            if pngtext == 'install':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/grey.png')
            elif pngtext == 'update':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/yellow.png')
            elif pngtext == 'remove':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/green.png')
            else:
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/images/green.png')
            res.append(MultiContentEntryText(pos=(0, 1), size=(5, 30), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 1), size=(30, 30), png=loadPNG(png)))
            res.append(MultiContentEntryText(pos=(30, 1), size=(580, 30), font=0, flags=RT_HALIGN_LEFT, text=item, color=16777215, color_sel=16777215))
            theevents.append(res)
            res = []

        self.theevents = []
        self.theevents = theevents
        self['list'].l.setList(theevents)
        self['list'].show()

    def selgreen(self):
        try:
            cindex = self['list'].getSelectionIndex()
            selection = self.list[cindex][0]
        except:
            return

        selectedserverurl = self.links[cindex]
        selectedservername = selection
        selectedserverurl = self.truefilebaseurl + selectedserverurl
        self.prombt(selectedserverurl, selectedservername, 'green')

    def getfreespace(self):
        fspace = freespace()
        self.freespace = fspace
        self.setTitle(self.freespace)

    def selclicked(self):
        try:
            cindex = self['list'].getSelectionIndex()
            selection = self.list[cindex][0]
        except:
            return

        selectedserverurl = str(self.links[cindex])
        selectedservername = selection
        selectedserverurl = self.truefilebaseurl + selectedserverurl
        print selectedserverurl
        self.prombt(selectedserverurl, selectedservername, 'ok')

    def prombt(self, com, dom, action):
        self.com = com
        self.dom = dom
        instr = 'Downloading and installing ' + self.com + '\nPlease wait while addon is being downloaded...\nRestarting enigma2 is required after successful installation'
        endstr = 'Press OK to exit'
        if action == 'ok':
            if com.endswith('.ipk'):
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                self.session.openWithCallback(self.getfreespace, DownLoadgz, self.com, self.dom, instr, endstr)
                self.ipkgremove = False
        elif com.endswith('.ipk'):
            if self.pngtext == 'install' or self.pngtext == 'update':
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                ipkbasefile = str(os.path.basename(com))
                try:
                    ipkname = ''
                    ipkparts = []
                    ipkparts = ipkbasefile.split('_')
                    com = str(ipkparts[0]).strip()
                except:
                    com = str(os.path.basename(com))

                self.session.open(Console2.PurePrestigeConsole2, _('removing: %s') % dom, ['opkg remove  %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = True
        else:
            self.session.openWithCallback(self.getfreespace, DownLoadgz, self.com, self.dom, instr, endstr)
            self.ipkgremove = False

    def getcommandList(self):
        clist = []
        clist.append((_('opkg update'), 'update:update opkg lists and install package'))
        clist.append((_('Install with config values overwrite'), 'install -force-maintainer:install package with overwrite preexisting config values'))
        clist.append((_('Force overwrite'), 'install -force-overwrite:install package with overwrite pre-exist files'))
        clist.append((_('Force depends'), 'install -force-depends:install with package with dependent packages'))
        clist.append((_('Force noaction'), 'install -force-noaction:install for test no action taken'))
        clist.append((_('Force reinstall'), 'install -force-reinstall:force re-install package'))
        clist.append((_('Install without depends'), 'install -nodeps:install without depencency'))
        return clist

    def askForSource(self, command):
        if command:
            self.menuclicked(command)

    def advanceinstall(self):
        self.session.openWithCallback(self.askForSource, ChoiceBox, _('select command'), self.getcommandList())

    def menuclicked(self, command = None):
        try:
            cindex = self['list'].getSelectionIndex()
            selection = self.list[cindex][0]
        except:
            return

        selectedserverurl = str(self.links[cindex])
        selectedservername = selection
        selectedserverurl = self.truefilebaseurl + selectedserverurl
        self.menuprombt(selectedserverurl, selectedservername, 'ok', command)

    def menuprombt(self, com, dom, action, command):
        self.com = command[1] + ' ' + com
        self.dom = dom
        commandlist = command[1].split(':')
        self.commandstr = commandlist[0]
        commandesc = commandlist[1]
        instr = 'Downloading and installing ' + self.com + '\n'
        instr = instr + 'Please wait while addon is being downloaded...\n  Restarting enigma2 is required after successful installation' + '\n' + commandesc
        endstr = 'Press OK to exit'
        if self.commandstr.strip() == 'update':
            self.com = 'install ' + com
            print '3830', 'ok'
            self.session.open(Console2.PurePrestigeConsole2, _('Updating opkg list:'), ['opkg update'], self.refresh, True, instr, '')
        if action == 'ok':
            if com.endswith('.ipk'):
                ccctext = 'opkg ' + self.com
                wfile(ccctext)
                print 'command', 'opkg ' + self.com
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-' + self.commandstr + ':'), ['opkg ' + self.com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                self.session.open(MessageBox, _('No ipk package found'), type=1, timeout=4)
                self.ipkgremove = False


class PurePrestigePackageFeeds(Screen):
    global HD_Res
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    if HD_Res == True:
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frame.png" position="0,0" size="920,600" transparent="1"/>\t\n                               \n                                <ePixmap position="15,60" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\n                <widget name="list" position="20,65" size="880,405" scrollbarMode="showOnDemand" transparent="1" zPosition="4" />\n\t\t<ePixmap position="15,490" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\n\n\t\t\t\n                <ePixmap name="green" position="360,510" zPosition="4" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="360,515" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                        \n\t\t\t\n\t\t<eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />\n\t\t<widget name="info" position="50,50" zPosition="4" size="850,300" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t\t<widget name="info2" position="0,550" zPosition="4" size="920,30" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t\t<widget name="fspace" position="0,320" zPosition="4" size="600,80" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />\n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\t\n\n                <ePixmap position="15,34" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n  \n                 <widget name="list" position="15,38" size="610,320" scrollbarMode="showOnDemand" transparent="1" zPosition="4" />\n\n                <ePixmap name="green" position="130,510" zPosition="4" size="113,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="130,520" zPosition="5" size="150,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                                           \n\t\t\t\n\t\t<eLabel position="44,75" zPosition="-1" size="63,52" backgroundColor="#222222" />\n\t\t<widget name="info" position="32,38" zPosition="4" size="596,225" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t\t<widget name="info2" position="0,420" zPosition="4" size="640,30" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\t\n        \t<widget name="fspace" position="0,240" zPosition="4" size="416,60" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />\n                </screen>'

    def __init__(self, session, selectedservername = None, globalservername = None):
        self.skin = PurePrestigePackageFeeds.skin
        Screen.__init__(self, session)
        self['key_green'] = Button(_('Install'))
        self.globalservername = globalservername
        self.selectedservername = selectedservername
        print self.selectedservername
        self.newsurl = ''
        self.list = []
        self['list'] = MenuList([])
        self['info'] = Label()
        self['info2'] = Label('Press Menu for advanced install')
        self['fspace'] = Label()
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        self['list'].onSelectionChanged.append(self.selectionChanged)
        list = []
        self.list = list
        self.status = []
        self.slist = []
        self['info'].setText('Downloading addons groups,please wait..')
        self.timer = eTimer()
        self.timer.callback.append(self.downloadxmlpage)
        self.timer.start(100, 1)
        self['actions'] = ActionMap(['SetupActions', 'MenuActions', 'ColorActions'], {'ok': self.selclicked,
         'menu': self.advanceinstall,
         'cancel': self.close,
         'green': self.selgreen}, -2)
        self.onShow.append(self.selectionChanged)
        self.getfreespace()
        self.filebaseurl = ''

    def getiteOpenPlimurl(self):
        self.rooturl = 'http://downloads.pli-images.org/feeds/openpli-2.1/dm800/'
        self.groupurl = self.selectedservername + '/'
        self.url = self.rooturl + self.groupurl
        self.filebaseurl = self.rooturl + self.groupurl
        self.truefilebaseurl = self.filebaseurl
        print self.selectedservername
        if self.selectedservername == '3rd-party':
            self.url = self.rooturl + self.groupurl + 'Packages.gz'
        else:
            self.url = self.rooturl + self.groupurl + 'Packages'

    def getiteDreamboxupdatesmurl(self):
        self.rooturl = 'http://dreamboxupdate.com/opendreambox/2.0.0/'
        self.groupurl = self.selectedservername + '/'
        self.url = self.rooturl + self.groupurl
        self.filebaseurl = ''
        if self.selectedservername == 'dm800':
            self.truefilebaseurl = self.rooturl + 'mips32el-nf/'
        else:
            self.truefilebaseurl = self.rooturl + 'mips32el/'

    def getiteNewnigma2murl(self):
        self.rooturl = 'http://feed.newnigma2.to/unstable/4.0/'
        if self.selectedservername == 'mips32el':
            self.groupurl = self.selectedservername + '/'
        elif 'mips32el-nf' in self.selectedservername:
            self.groupurl = 'mips32el-nf/'
        self.url = self.rooturl + self.groupurl
        self.filebaseurl = ''
        self.truefilebaseurl = self.rooturl + self.groupurl

    def getiteMerlinmurl(self):
        self.rooturl = 'http://feed.dreambox-tools.info/'
        self.groupurl = 'index.php?dir=' + self.selectedservername + '/'
        self.url = self.rooturl + self.groupurl
        self.filebaseurl = '/' + self.groupurl + '&amp;file='
        self.truefilebaseurl = self.rooturl + 'feeds/' + self.selectedservername + '/'

    def getiteOozoonmurl(self):
        self.rooturl = 'http://oozoon-dreamboxupdate.de/opendreambox/2.0/experimental/'
        if self.selectedservername == 'mips32el':
            self.groupurl = 'mips32el/'
            self.url = self.rooturl + self.groupurl + 'index.html'
        elif self.selectedservername == 'mips32el-nf':
            self.groupurl = 'mips32el-nf/'
            self.url = self.rooturl + self.groupurl + 'index.html'
        self.truefilebaseurl = self.rooturl + self.groupurl

    def downloadxmlpage(self):
        if self.globalservername == 'Oozoon Feeds':
            self.getiteOozoonmurl()
        elif self.globalservername == 'Merlin Feeds':
            self.getiteMerlinmurl()
        elif self.globalservername == 'Newnigma2 Feeds':
            self.getiteNewnigma2murl()
        elif self.globalservername == 'Dreamboxupdate Feeds':
            self.getiteDreamboxupdatesmurl()
        else:
            if self.globalservername == 'OpenPli Feeds':
                self.getiteOpenPlimurl()
                print self.selectedservername
                getPage(self.url).addCallback(self._gotPageLoadOpenPli).addErrback(self.errorLoad)
                return
            return
        getPage(self.url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    def downloadurl(self, data):
        mdata = ''
        try:
            filename = '/tmp/package.gz'
            file = open(filename, 'w')
            file.write(data)
            file.close()
            print 'done'
            self['info'].setText('')
            Console().ePopen('gunzip -c /tmp/package.gz > /tmp/package')
            fp = open('/tmp/package', 'r')
            mdata = fp.read()
            fp.close()
            print mdata
        except:
            self['info'].setText(str('Sorry,error in getting feeds'))
            mdata = ''

        try:
            os.remove('/tmp/package.gz')
            os.remove('/tmp/package')
        except:
            print 'files not removed'

        print 'remove files'
        return mdata

    def errorLoad(self, error):
        print str(error)
        self['info'].setText('Addons Download Failure,No internet connection or server down !')
        self.downloading = False

    def _gotPageLoadOpenPli(self, data):
        try:
            mdata = ''
            if 'party' in self.selectedservername:
                mdata = self.downloadurl(data)
                data = mdata
        except:
            pass

        self.xml = data
        self['info'].setText('')
        try:
            if self.xml:
                pass
            else:
                self.downloading = False
                self['info'].setText('Addons Download Failure,No internet connection or server down !')
                return
            self.data = []
            icount = 0
            list = []
            links = []
            list = []
            self.list = list
            a = []
            buf = StringIO.StringIO(data)
            a = buf.readlines()
            print a[0]
            print a[1]
            b = []
            ref = ''
            for i in range(0, len(a)):
                if 'Filename:' in a[i]:
                    fname = a[i].replace('Filename:', '')
                    fname = fname.strip()
                    ref = self.filebaseurl + fname
                    print ref
                    ref = ref.replace(self.filebaseurl, '')
                    processmode = getipkversion(ref)
                    links.append(ref)
                    item = ref
                    newitem = item.replace(self.filebaseurl, '')
                    newitem = item.replace('enigma2-', '')
                    newitem = newitem.replace('.ipk', '')
                    newitem = newitem.replace('mipsel/', '')
                    newitem = newitem.replace('_mipsel', '')
                    newitem = newitem.replace('plugin-', '')
                    list.append([str(newitem), processmode])

            self.list = list
            self.links = links
            if len(self.list) == 0:
                self['info'].setText('No addons found')
            else:
                self['info'].setText('')
            self.downloading = True
        except:
            self.downloading = False
            self['info'].setText('Error processing server addons data')
            return

        self.getfreespace()
        self.ListToMulticontent()

    def _gotPageLoad(self, data):
        self.xml = data
        try:
            if self.xml:
                pass
            else:
                self.downloading = False
                self['info'].setText('Addons Download Failure,No internet connection or server down !')
                return
            self.data = []
            icount = 0
            list = []
            soup = BeautifulSoup(data)
            links = []
            list = []
            self.list = list
            for tag in soup.findAll('a', href=True):
                ref = tag['href']
                if ref.endswith('.ipk'):
                    ref = ref.replace(self.filebaseurl, '')
                    processmode = getipkversion(ref)
                    links.append(ref)
                    item = ref
                    item = os.path.basename(item)
                    newitem = item.replace(self.filebaseurl, '')
                    newitem = item.replace('enigma2-', '')
                    newitem = newitem.replace('.ipk', '')
                    newitem = newitem.replace('mipsel/', '')
                    newitem = newitem.replace('_mipsel', '')
                    newitem = newitem.replace('plugin-', '')
                    list.append([str(newitem), processmode])

            self.list = list
            self.links = links
            self['info'].setText('')
            self.downloading = True
        except:
            self.downloading = False
            self['info'].setText('Error processing server addons data')
            return

        self.getfreespace()
        self.ListToMulticontent()

    def selectionChanged(self):
        try:
            selection = self['list'].getCurrent()
            cindex = self['list'].getSelectionIndex()
            self.ipkgremove = False
            self.pngtext = self.list[cindex][1]
            if self.pngtext == 'install':
                self['key_green'].setText('Install')
            elif self.pngtext == 'update':
                self['key_green'].setText('Update')
            elif self.pngtext == 'remove':
                self['key_green'].setText('Remove')
        except:
            pass

    def refresh(self):
        if self.ipkgremove == False:
            png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/green.png')
            txt = 'remove'
        else:
            png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/grey.png')
            txt = 'install'
        idx = self['list'].getSelectionIndex()
        self.list[idx][1] = txt
        item = self.list[idx][0]
        res = []
        res.append(MultiContentEntryText(pos=(0, 1), size=(5, 30), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
        res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 1), size=(30, 30), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(30, 1), size=(580, 30), font=0, flags=RT_HALIGN_LEFT, text=item, color=16777215, color_sel=16777215))
        self.theevents[idx] = res
        self['list'].l.setList(self.theevents)
        res = []
        self['list'].show()
        self.getfreespace()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self['list'].l.setItemHeight(35)
        self['list'].l.setFont(0, gFont('Regular', 22))
        self.menulist = []
        for i in range(0, len(self.list)):
            pngtext = str(self.list[i][1])
            item = str(self.list[i][0])
            if pngtext == 'install':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/grey.png')
            elif pngtext == 'update':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/yellow.png')
            elif pngtext == 'remove':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/green.png')
            else:
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/images/green.png')
            res.append(MultiContentEntryText(pos=(0, 1), size=(5, 30), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 1), size=(30, 30), png=loadPNG(png)))
            res.append(MultiContentEntryText(pos=(30, 1), size=(580, 30), font=0, flags=RT_HALIGN_LEFT, text=item, color=16777215, color_sel=16777215))
            theevents.append(res)
            res = []

        self.theevents = []
        self.theevents = theevents
        self['list'].l.setList(theevents)
        self['list'].show()

    def selgreen(self):
        try:
            cindex = self['list'].getSelectionIndex()
            selection = self.list[cindex][0]
        except:
            return

        selectedserverurl = self.links[cindex]
        selectedservername = selection
        selectedserverurl = self.truefilebaseurl + selectedserverurl
        self.prombt(selectedserverurl, selectedservername, 'green')

    def getfreespace(self):
        fspace = freespace()
        self.freespace = fspace
        self.setTitle(self.freespace)

    def selclicked(self):
        try:
            cindex = self['list'].getSelectionIndex()
            selection = self.list[cindex][0]
        except:
            return

        try:
            selectedserverurl = os.path.base(str(self.links[cindex]))
        except:
            selectedserverurl = str(self.links[cindex])

        selectedservername = selection
        selectedserverurl = self.truefilebaseurl + selectedserverurl
        print selectedserverurl
        self.prombt(selectedserverurl, selectedservername, 'ok')

    def prombt(self, com, dom, action):
        self.com = com
        self.dom = dom
        instr = 'Downloading and installing ' + self.com + '\n'
        instr = instr + 'Please wait while addon is being downloaded...\n  Restarting enigma2 is required after successful installation'
        endstr = 'Press OK to exit'
        if action == 'ok':
            if com.endswith('.ipk'):
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                self.session.openWithCallback(self.getfreespace, DownLoadgz, self.com, self.dom, instr, endstr)
                self.ipkgremove = False
        elif com.endswith('.ipk'):
            if self.pngtext == 'install' or self.pngtext == 'update':
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                ipkbasefile = str(os.path.basename(com))
                try:
                    ipkname = ''
                    ipkparts = []
                    ipkparts = ipkbasefile.split('_')
                    com = str(ipkparts[0]).strip()
                except:
                    com = str(os.path.basename(com))

                self.session.open(Console2.PurePrestigeConsole2, _('removing: %s') % dom, ['opkg remove  %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = True
        else:
            self.session.openWithCallback(self.getfreespace, DownLoadgz, self.com, self.dom, instr, endstr)
            self.ipkgremove = False

    def getcommandList(self):
        clist = []
        clist.append((_('opkg update'), 'update:update opkg lists and install package'))
        clist.append((_('Install with config values overwrite'), 'install -force-maintainer:install package with overwrite preexisting config values'))
        clist.append((_('Force overwrite'), 'install -force-overwrite:install package with overwrite pre-exist files'))
        clist.append((_('Force depends'), 'install -force-depends:install with package with dependent packages'))
        clist.append((_('Force noaction'), 'install -force-noaction:install for test no action taken'))
        clist.append((_('Force reinstall'), 'install -force-reinstall:force re-install package'))
        clist.append((_('Install without depends'), 'install -nodeps:install without depencency'))
        return clist

    def askForSource(self, command):
        if command:
            self.menuclicked(command)

    def advanceinstall(self):
        self.session.openWithCallback(self.askForSource, ChoiceBox, _('select command'), self.getcommandList())

    def menuclicked(self, command = None):
        try:
            cindex = self['list'].getSelectionIndex()
            selection = self.list[cindex][0]
        except:
            return

        selectedserverurl = str(self.links[cindex])
        selectedservername = selection
        selectedserverurl = self.truefilebaseurl + selectedserverurl
        print selectedserverurl
        self.menuprombt(selectedserverurl, selectedserverurl, 'ok', command)

    def menuprombt(self, com, dom, action, command):
        self.com = command[1] + ' ' + com
        self.dom = dom
        commandlist = command[1].split(':')
        self.commandstr = commandlist[0]
        commandesc = commandlist[1]
        instr = 'Please wait while addon is being downloaded...\n  Restarting enigma2 is required after successful installation' + '\n' + commandesc
        endstr = 'Press OK to exit'
        if self.commandstr.strip() == 'update':
            self.com = 'install ' + com
            print '3830', 'ok'
            self.session.open(Console2.PurePrestigeConsole2, _('Updating opkg list:'), ['opkg update'], self.refresh, True, instr, '')
        if action == 'ok':
            if com.endswith('.ipk'):
                ccctext = 'opkg ' + self.com
                wfile(ccctext)
                print 'command', 'opkg ' + self.com
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-' + self.commandstr + ':'), ['opkg ' + self.com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                self.session.open(MessageBox, _('No ipk package found'), type=1, timeout=4)
                self.ipkgremove = False


class Ipkgsearch(Screen):
    if HD_Res == True:
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frame.png" position="0,0" size="920,600"/>\t\n                <widget name="menu" position="50,50" size="850,420" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<ePixmap position="15,490" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\n                \n\t        <ePixmap name="green" position="140,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="110,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n        \t<ePixmap name="blue" position="390,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_blue" position="360,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="yellow" position="600,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t\t  \n                <widget name="key_yellow" position="570,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                                <widget name="info2" position="0,0" zPosition="4" size="920,600" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />                    \n                <widget name="info" position="0,550" zPosition="4" size="920,30" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\t\n                <widget name="menu" position="32,38" size="596,290" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<ePixmap position="15,350" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\n                \n\t        <ePixmap name="green" position="118,383" zPosition="4" size="101,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="108,390" zPosition="5" size="126,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n        \t<ePixmap name="blue" position="276,383" zPosition="4" size="101,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_blue" position="265,390" zPosition="5" size="126,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="yellow" position="430,383" zPosition="4" size="101,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t\t  \n                <widget name="key_yellow" position="412,390" zPosition="5" size="126,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <widget name="info2" position="0,0" zPosition="4" size="920,520" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />          \n                <widget name="info" position="0,412" zPosition="4" size="640,30" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n                </screen>'

    def __init__(self, session, xmlparse, selection, groups, searchstr):
        self.skin = Ipkgsearch.skin
        Screen.__init__(self, session)
        self.searchstr = searchstr
        self.xmlparse = xmlparse
        self.selection = selection
        self['key_yellow'] = Button(_('Preview'))
        self['key_blue'] = Button(_('Description'))
        self['key_green'] = Button(_('Install'))
        self['info'] = Label(_('Press Menu for advanced install'))
        self['info2'] = Label(_(''))
        self['menu'] = MenuList([], True, eListboxPythonMultiContent)
        list = []
        self.list = list
        self.status = []
        self.slist = []
        slist = []
        self.groups = []
        ishotname = False
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            for plugin in plugins.getElementsByTagName('plugin'):
                group = str(plugins.getAttribute('cont').encode('utf8'))
                item = str(plugin.getAttribute('name').encode('utf8'))
                urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                proper_url = checkhostname(urlserver)
                if self.searchstr in item:
                    if proper_url == True:
                        processmode = getipkversion(urlserver)
                        if self.selection == 'Cams' and item == 'list':
                            pass
                        else:
                            list.append([item, processmode, group])
                            self.groups.append(group)

        nlist = []
        for k in list:
            x = k[0].strip()
            endstr = x[-2:]
            item = x
            slist.append(endstr)
            if x[-2:] == '-p':
                item = x[:-2]
            elif x[-2:] == '-d':
                item = x[:-2]
            elif x[-2:] == '-b':
                item = x[:-2]
            nlist.append(item)

        self.slist = slist
        self['menu'].onSelectionChanged.append(self.selectionChanged)
        self['actions'] = ActionMap(['SetupActions', 'MenuActions', 'ColorActions'], {'ok': self.selclicked,
         'cancel': self.close,
         'blue': self.desc,
         'yellow': self.preview,
         'menu': self.advanceinstall,
         'green': self.selgreen}, -2)
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.itempreview = False
        self.getfreespace()
        if len(list) == 0:
            self['info2'].setText('No addons found')
            self['key_green'].hide()
            return
        self['info2'].setText('')
        self.onShow.append(self.selectionChanged)
        self.ListToMulticontent()

    def refresh(self):
        if self.ipkgremove == False:
            png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/green.png')
            txt = 'remove'
        else:
            png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/grey.png')
            txt = 'install'
        idx = self['menu'].getSelectionIndex()
        self.list[idx][1] = txt
        item = str(self.list[idx][0])
        group = str(self.list[idx][2])
        item = item + '/' + group
        res = []
        res.append(MultiContentEntryText(pos=(0, 1), size=(5, 30), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
        res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 1), size=(30, 30), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(30, 1), size=(580, 30), font=0, flags=RT_HALIGN_LEFT, text=item, color=16777215, color_sel=16777215))
        self.theevents[idx] = res
        self['menu'].l.setList(self.theevents)
        res = []
        self['menu'].show()
        self.getfreespace()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self['menu'].l.setItemHeight(35)
        self['menu'].l.setFont(0, gFont('Regular', 22))
        self.menulist = []
        for i in range(0, len(self.list)):
            pngtext = str(self.list[i][1])
            self.status.append(pngtext)
            item = str(self.list[i][0])
            x = item.strip()
            endstr = x[-2:]
            self.slist.append(endstr)
            if x[-2:] == '-p':
                item = x[:-2]
            elif x[-2:] == '-d':
                item = x[:-2]
            elif x[-2:] == '-b':
                item = x[:-2]
            group = str(self.list[i][2])
            item = item + '/' + group
            if pngtext == 'install':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/grey.png')
            elif pngtext == 'update':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/yellow.png')
            elif pngtext == 'remove':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/green.png')
            else:
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/images/button_green.png')
                png = LoadPixmap(png)
            res.append(MultiContentEntryText(pos=(0, 1), size=(5, 30), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 1), size=(30, 30), png=loadPNG(png)))
            res.append(MultiContentEntryText(pos=(30, 1), size=(870, 30), font=0, flags=RT_HALIGN_LEFT, text=item, color=16777215, color_sel=16777215))
            theevents.append(res)
            res = []

        self.theevents = []
        self.theevents = theevents
        self['menu'].l.setList(theevents)
        self['menu'].show()

    def desc(self):
        if self.itemdes:
            pass
        else:
            return
        try:
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex][0]
            group = str(self.groups[cindex])
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == group:
                for plugin in plugins.getElementsByTagName('plugin'):
                    urlserver = ''
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.urlserver = ''
                        if urlserver.endswith('.ipk'):
                            self.urlserver = urlserver.replace('.ipk', '.txt')
                        elif urlserver.endswith('.tar.gz'):
                            self.urlserver = urlserver.replace('.tar.gz', '.txt')
                        elif urlserver.endswith('.tar.bz2'):
                            self.urlserver = urlserver.replace('.tar.bz2', '.txt')
                        elif urlserver.endswith('.tbz2'):
                            self.urlserver = urlserver.replace('.tbz2', '.txt')
                        elif urlserver.endswith('.tbz'):
                            self.urlserver = urlserver.replace('.tbz', '.txt')
                        if self.urlserver:
                            self.session.open(DescScreen, self.urlserver)

    def preview(self):
        if self.itempreview:
            pass
        else:
            return
        try:
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex][0]
            group = str(self.groups[cindex])
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == group:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        if urlserver.endswith('.ipk'):
                            self.urlserver = urlserver.replace('.ipk', '.jpg')
                        elif urlserver.endswith('.tar.gz'):
                            self.urlserver = urlserver.replace('.tar.gz', '.jpg')
                        elif urlserver.endswith('.tar.bz2'):
                            self.urlserver = urlserver.replace('.tar.bz2', '.jpg')
                        elif urlserver.endswith('.tbz2'):
                            self.urlserver = urlserver.replace('.tbz2', '.jpg')
                        elif urlserver.endswith('.tbz'):
                            self.urlserver = urlserver.replace('.tbz', '.jpg')
                        self.session.open(pplayer.PurePrestigePictureScreen, self.urlserver)

    def selectionChanged(self):
        try:
            selection = self['menu'].getCurrent()
            cindex = self['menu'].getSelectionIndex()
            self.ipkgremove = False
            endstr = self.slist[cindex]
            self.pngtext = self.list[cindex][1]
            if self.pngtext == 'install':
                self['key_green'].setText('Install')
            elif self.pngtext == 'update':
                self['key_green'].setText('Update')
            elif self.pngtext == 'remove':
                self['key_green'].setText('Remove')
            if endstr == '-p':
                self['key_yellow'].show()
                self['key_blue'].hide()
                self.itempreview = True
                self.itemdes = False
            elif endstr == '-d':
                self['key_yellow'].hide()
                self['key_blue'].show()
                self.itempreview = False
                self.itemdes = True
            elif endstr == '-b':
                self['key_yellow'].show()
                self['key_blue'].show()
                self.itempreview = True
                self.itemdes = True
            else:
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.itempreview = False
                self.itemdes = False
        except:
            pass

    def getfreespace(self):
        fspace = freespace()
        self.freespace = fspace
        self.setTitle(self.freespace)

    def selgreen(self):
        print 'mah1'
        try:
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex][0]
            print selection_country
            print self.selection
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            for plugin in plugins.getElementsByTagName('plugin'):
                if plugin.getAttribute('name').encode('utf8') == selection_country:
                    urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                    pluginname = plugin.getAttribute('name').encode('utf8')
                    print urlserver, pluginname
                    self.prombt(urlserver, pluginname, 'green')

    def selclicked(self):
        try:
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex][0]
            group = self.groups[cindex]
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            for plugin in plugins.getElementsByTagName('plugin'):
                if plugin.getAttribute('name').encode('utf8') == selection_country:
                    urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                    pluginname = plugin.getAttribute('name').encode('utf8')
                    self.prombt(urlserver, pluginname, 'ok')

    def prombt(self, com, dom, action):
        self.com = com
        self.dom = dom
        instr = 'Downloading and installing ' + self.com + '\n'
        instr = instr + 'Please wait while addon is being downloaded...\n  Restarting enigma2 is required after successful installation'
        endstr = 'Press OK to exit'
        if action == 'ok':
            if com.endswith('.ipk'):
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                self.session.openWithCallback(self.getfreespace, DownLoadgz, self.com, self.dom, instr, endstr)
                self.ipkgremove = False
        elif com.endswith('.ipk'):
            if self.pngtext == 'install' or self.pngtext == 'update':
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                ipkbasefile = str(os.path.basename(com))
                try:
                    ipkname = ''
                    ipkparts = []
                    ipkparts = ipkbasefile.split('_')
                    com = str(ipkparts[0]).strip()
                except:
                    com = str(os.path.basename(com))

                self.session.open(Console2.PurePrestigeConsole2, _('removing: %s') % dom, ['opkg remove  %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = True
        else:
            self.session.openWithCallback(self.getfreespace, DownLoadgz, self.com, self.dom, instr, endstr)
            self.ipkgremove = False

    def getcommandList(self):
        clist = []
        clist.append((_('opkg update'), 'update:update opkg lists and install package'))
        clist.append((_('Install with config values overwrite'), 'install -force-maintainer:install package with overwrite preexisting config values'))
        clist.append((_('Force overwrite'), 'install -force-overwrite:install package with overwrite pre-exist files'))
        clist.append((_('Force depends'), 'install -force-depends:install with package with dependent packages'))
        clist.append((_('Force noaction'), 'install -force-noaction:install for test no action taken'))
        clist.append((_('Force reinstall'), 'install -force-reinstall:force re-install package'))
        clist.append((_('Install without depends'), 'install -nodeps:install without depencency'))
        return clist

    def askForSource(self, command):
        if command:
            self.menuclicked(command)

    def advanceinstall(self):
        self.session.openWithCallback(self.askForSource, ChoiceBox, _('select command'), self.getcommandList())

    def menuclicked(self, command = None):
        try:
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex][0]
        except:
            return

        self.url = ''
        self.pluginname = ''
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.menuprombt(urlserver, pluginname, 'ok', command)

    def menuprombt(self, com, dom, action, command):
        self.com = command[1] + ' ' + com
        self.dom = dom
        commandlist = command[1].split(':')
        self.commandstr = commandlist[0]
        commandesc = commandlist[1]
        instr = 'Downloading and installing ' + self.com + '\n'
        instr = instr + 'Please wait while addon is being downloaded...\n  Restarting enigma2 is required after successful installation' + '\n' + commandesc
        endstr = 'Press OK to exit'
        if self.commandstr.strip() == 'update':
            self.com = 'install ' + com
            print '3830', 'ok'
            self.session.open(Console2.PurePrestigeConsole2, _('Updating opkg list:'), ['opkg update'], self.refresh, True, instr, '')
        if action == 'ok':
            if com.endswith('.ipk'):
                ccctext = 'opkg ' + self.com
                wfile(ccctext)
                print 'command', 'opkg ' + self.com
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-' + self.commandstr + ':'), ['opkg ' + self.com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                self.session.open(MessageBox, _('No ipk package found'), type=1, timeout=4)
                self.ipkgremove = False


class PurePrestigeIpkgLogos(Screen):
    if HD_Res == True:
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frame.png" position="0,0" size="920,600"/>\t\n                <widget name="menu" position="50,50" size="850,420" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<ePixmap position="15,490" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\n                \n\t        <ePixmap name="green" position="140,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="110,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n        \t<ePixmap name="blue" position="390,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_blue" position="360,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="yellow" position="600,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t\t  \n                <widget name="key_yellow" position="570,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                          \n                <widget name="info" position="0,550" zPosition="4" size="920,30" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\t\n                <widget name="menu" position="32,38" size="596,315" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<ePixmap position="15,368" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\n                \n\t        <ePixmap name="green" position="108,383" zPosition="4" size="101,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="106,390" zPosition="5" size="126,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n        \t<ePixmap name="blue" position="276,383" zPosition="4" size="101,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_blue" position="263,390" zPosition="5" size="126,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="yellow" position="420,383" zPosition="4" size="101,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t\t  \n                <widget name="key_yellow" position="412,390" zPosition="5" size="126,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                          \n                <widget name="info" position="0,412" zPosition="4" size="640,30" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n                </screen>'

    def __init__(self, session, xmlparse, selection):
        self.skin = PurePrestigeIpkgLogos.skin
        Screen.__init__(self, session)
        self.xmlparse = xmlparse
        self.selection = selection
        self['key_yellow'] = Button(_('Preview'))
        self['key_blue'] = Button(_('Description'))
        self['key_green'] = Button(_('Install'))
        self['info'] = Label(_('Press Menu for advanced install'))
        self['menu'] = MenuList([], True, eListboxPythonMultiContent)
        list = []
        self.list = list
        self.status = []
        self.slist = []
        ishotname = False
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    item = plugin.getAttribute('name').encode('utf8')
                    urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                    proper_url = checkhostname(urlserver)
                    if proper_url == True:
                        processmode = getipkversion(urlserver)
                        list.append([item, processmode])

        list.sort()
        self['menu'].onSelectionChanged.append(self.selectionChanged)
        self['actions'] = ActionMap(['SetupActions', 'MenuActions', 'ColorActions'], {'ok': self.selclicked,
         'cancel': self.close,
         'yellow': self.preview,
         'menu': self.advanceinstall,
         'green': self.selgreen}, -2)
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.itempreview = False
        self.itemdes = False
        self.onShow.append(self.selectionChanged)
        self.getfreespace()
        self.ListToMulticontent()

    def refresh(self):
        if self.ipkgremove == False:
            png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/green.png')
            txt = 'remove'
        else:
            png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/grey.png')
            txt = 'install'
        idx = self['menu'].getSelectionIndex()
        self.list[idx][1] = txt
        item = self.list[idx][0]
        res = []
        res.append(MultiContentEntryText(pos=(0, 1), size=(5, 30), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
        res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 1), size=(30, 30), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(30, 1), size=(580, 30), font=0, flags=RT_HALIGN_LEFT, text=item, color=16777215, color_sel=16777215))
        self.theevents[idx] = res
        self['menu'].l.setList(self.theevents)
        res = []
        self['menu'].show()
        self.getfreespace()
        if 'spinner' in str.lower(self.selection):
            savespinner_default

    def ListToMulticontent(self):
        res = []
        theevents = []
        self['menu'].l.setItemHeight(35)
        self['menu'].l.setFont(0, gFont('Regular', 22))
        self.menulist = []
        for i in range(0, len(self.list)):
            pngtext = str(self.list[i][1])
            self.status.append(pngtext)
            item = str(self.list[i][0])
            x = item.strip()
            endstr = x[-2:]
            self.slist.append(endstr)
            if x[-2:] == '-p':
                item = x[:-2]
            elif x[-2:] == '-d':
                item = x[:-2]
            elif x[-2:] == '-b':
                item = x[:-2]
            if pngtext == 'install':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/grey.png')
            elif pngtext == 'update':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/yellow.png')
            elif pngtext == 'remove':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/green.png')
            else:
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/images/button_green.png')
                png = LoadPixmap(png)
            res.append(MultiContentEntryText(pos=(0, 1), size=(5, 30), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 1), size=(30, 30), png=loadPNG(png)))
            res.append(MultiContentEntryText(pos=(30, 1), size=(870, 30), font=0, flags=RT_HALIGN_LEFT, text=item, color=16777215, color_sel=16777215))
            theevents.append(res)
            res = []

        self.theevents = []
        self.theevents = theevents
        self['menu'].l.setList(theevents)
        self['menu'].show()

    def preview(self):
        if self.itempreview:
            pass
        else:
            return
        try:
            selection_country = self['menu'].getCurrent()
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex][0]
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.urlserver = urlserver
                        strsel = self.selection.lower()
                        if 'spinner' in strsel:
                            self.session.open(downloadScreen, self.urlserver)
                        else:
                            if urlserver.endswith('.ipk'):
                                self.urlserver = urlserver.replace('.ipk', '.jpg')
                            elif urlserver.endswith('.tar.gz'):
                                self.urlserver = urlserver.replace('.tar.gz', '.jpg')
                            elif urlserver.endswith('.tar.bz2'):
                                self.urlserver = urlserver.replace('.tar.bz2', '.jpg')
                            elif urlserver.endswith('.tbz2'):
                                self.urlserver = urlserver.replace('.tbz2', '.jpg')
                            elif urlserver.endswith('.tbz'):
                                self.urlserver = urlserver.replace('.tbz', '.jpg')
                            self.session.open(pplayer.PurePrestigePictureScreen, self.urlserver)

    def selectionChanged(self):
        try:
            selection = self['menu'].getCurrent()
            cindex = self['menu'].getSelectionIndex()
            self.ipkgremove = False
            endstr = self.slist[cindex]
            self.pngtext = self.list[cindex][1]
            if self.pngtext == 'install':
                self['key_green'].setText('Install')
            elif self.pngtext == 'update':
                self['key_green'].setText('Update')
            elif self.pngtext == 'remove':
                self['key_green'].setText('Remove')
            if endstr == '-p':
                self['key_yellow'].show()
                self['key_blue'].hide()
                self.itempreview = True
                self.itemdes = False
            elif endstr == '-d':
                self['key_yellow'].hide()
                self['key_blue'].show()
                self.itempreview = False
                self.itemdes = True
            elif endstr == '-b':
                self['key_yellow'].show()
                self['key_blue'].show()
                self.itempreview = True
                self.itemdes = True
            else:
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.itempreview = False
                self.itemdes = False
            if 'spinner' in str.lower(self.selection):
                self['key_yellow'].show()
                self.itempreview = True
                return
        except:
            pass

    def getfreespace(self):
        fspace = freespace()
        self.freespace = fspace
        self.setTitle(self.freespace)

    def selgreen(self):
        try:
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex][0]
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.prombt(urlserver, pluginname, 'green')

    def selclicked(self):
        try:
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex][0]
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.prombt(urlserver, pluginname, 'ok')

    def deletespinnerfiles(self):
        path = '/usr/share/enigma2/skin_default/spinner/'
        self.path = path
        skins = []
        try:
            for x in os.listdir(path):
                if os.path.isfile(path + x):
                    skins.append(path + x)

            for k in skins:
                os.remove(k)

        except:
            pass

    def prombt(self, com, dom, action):
        self.com = com
        self.dom = dom
        self.ipkgremove = False
        self.action = action
        if 'skin' in str.lower(self.selection) and action == 'ok':
            self.session.openWithCallback(self.callMyMsg, MessageBox, _('Do not install any skin unless you are sure it is compatible with your image.Are you sure?'), MessageBox.TYPE_YESNO)
            return
        instr = 'Downloading and installing ' + self.com + '\n'
        instr = instr + 'Please wait while addon is being downloaded...\n  Restarting enigma2 is required after successful installation'
        endstr = 'Press OK to exit'
        if 'logo' in str.lower(self.selection):
            instr = 'Please wait while logo is being downloaded...\n Logos only for internal flash image\n  Restarting enigma2 is required after successful installation'
        elif 'spinner' in str.lower(self.selection):
            instr = 'Please wait while spinner is being downloaded...\n  Restarting enigma2 is required after successful installation'
            endstr = 'Press OK to exit'
            self.deletespinnerfiles()
        else:
            instr = 'Please wait while addon is being downloaded...\n  Restarting enigma2 is required after successful installation'
            endstr = 'Press OK to exit'
        if action == 'ok':
            if com.endswith('.ipk'):
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                self.session.openWithCallback(self.getfreespace, DownLoadgz, self.com, self.dom, instr, endstr)
                self.ipkgremove = False
        elif com.endswith('.ipk'):
            if self.pngtext == 'install' or self.pngtext == 'update':
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                ipkbasefile = str(os.path.basename(com))
                try:
                    ipkname = ''
                    ipkparts = []
                    ipkparts = ipkbasefile.split('_')
                    com = str(ipkparts[0]).strip()
                except:
                    com = str(os.path.basename(com))

                self.session.open(Console2.PurePrestigeConsole2, _('removing: %s') % dom, ['opkg remove  %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = True
        else:
            self.session.openWithCallback(self.getfreespace, DownLoadgz, self.com, self.dom, instr, endstr)
            self.ipkgremove = False

    def callMyMsg(self, result):
        if result:
            dom = self.dom
            com = self.com
            instr = 'Please wait while skin is being downloaded...\n  Restarting enigma2 is required after successful installation'
            endstr = 'Press OK to exit or GREEN to apply skin'
            if self.action == 'ok':
                if com.endswith('.ipk'):
                    self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.refresh, False, instr, endstr)
                    self.ipkgremove = False
                else:
                    self.session.openWithCallback(self.getfreespace, DownLoadgz, self.com, self.dom, instr, endstr)
                    self.ipkgremove = False
            elif com.endswith('.ipk'):
                if self.pngtext == 'install' or self.pngtext == 'update':
                    self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.refresh, False, instr, endstr)
                    self.ipkgremove = False
                else:
                    ipkbasefile = str(os.path.basename(com))
                    try:
                        ipkname = ''
                        ipkparts = []
                        ipkparts = ipkbasefile.split('_')
                        com = str(ipkparts[0]).strip()
                    except:
                        com = str(os.path.basename(com))

                    self.session.open(Console2.PurePrestigeConsole2, _('removing: %s') % dom, ['opkg remove  %s' % com], self.refresh, False, instr, endstr)
                    self.ipkgremove = True
            else:
                self.session.openWithCallback(self.getfreespace, DownLoadgz, self.com, self.dom, instr, endstr)
                self.ipkgremove = False

    def getcommandList(self):
        clist = []
        clist.append((_('opkg update'), 'update:update opkg lists and install package'))
        clist.append((_('Install with config values overwrite'), 'install -force-maintainer:install package with overwrite preexisting config values'))
        clist.append((_('Force overwrite'), 'install -force-overwrite:install package with overwrite pre-exist files'))
        clist.append((_('Force depends'), 'install -force-depends:install with package with dependent packages'))
        clist.append((_('Force noaction'), 'install -force-noaction:install for test no action taken'))
        clist.append((_('Force reinstall'), 'install -force-reinstall:force re-install package'))
        clist.append((_('Install without depends'), 'install -nodeps:install without depencency'))
        return clist

    def askForSource(self, command):
        if command:
            self.menuclicked(command)

    def advanceinstall(self):
        self.session.openWithCallback(self.askForSource, ChoiceBox, _('select command'), self.getcommandList())

    def menuclicked(self, command = None):
        try:
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex][0]
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.menuprombt(urlserver, pluginname, 'ok', command)

    def menuprombt(self, com, dom, action, command):
        self.com = command[1] + ' ' + com
        self.dom = dom
        print 'command', command
        print command[1]
        commandlist = command[1].split(':')
        self.commandstr = commandlist[0]
        commandesc = commandlist[1]
        instr = 'Downloading and installing ' + self.com + '\n'
        instr = instr + 'Please wait while addon is being downloaded...\n  Restarting enigma2 is required after successful installation' + '\n' + commandesc
        endstr = 'Press OK to exit'
        if self.commandstr.strip() == 'update':
            self.com = 'install ' + com
            print '3830', 'ok'
            self.session.open(Console2.PurePrestigeConsole2, _('Updating opkg list:'), ['opkg update'], self.refresh, True, instr, '')
        if action == 'ok':
            if com.endswith('.ipk'):
                ccctext = 'opkg ' + self.com
                wfile(ccctext)
                print 'command', 'opkg ' + self.com
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-' + self.commandstr + ':'), ['opkg ' + self.com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                self.session.open(MessageBox, _('No ipk package found'), type=1, timeout=4)
                self.ipkgremove = False


class PurePrestigeIpkgPlugins(Screen):
    if HD_Res == True:
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frame.png" position="0,0" size="920,600"/>\t\n                <widget name="menu" position="50,50" size="850,420" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<ePixmap position="15,490" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\n                \n\t        <ePixmap name="green" position="140,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="110,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n        \t<ePixmap name="blue" position="390,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_blue" position="360,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="yellow" position="600,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t\t  \n                <widget name="key_yellow" position="570,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                          \n                <widget name="info" position="0,550" zPosition="4" size="920,30" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\t\n                <widget name="menu" position="32,38" size="596,315" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<ePixmap position="15,368" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\n                \n\t        <ePixmap name="green" position="118,383" zPosition="4" size="101,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="108,390" zPosition="5" size="126,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n        \t<ePixmap name="blue" position="276,383" zPosition="4" size="101,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_blue" position="275,390" zPosition="5" size="126,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="yellow" position="420,383" zPosition="4" size="101,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t\t  \n                <widget name="key_yellow" position="412,390" zPosition="5" size="126,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                          \n                <widget name="info" position="0,412" zPosition="4" size="640,30" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n                </screen>'

    def __init__(self, session, xmlparse, selection):
        self.skin = PurePrestigeIpkgPlugins.skin
        Screen.__init__(self, session)
        self.xmlparse = xmlparse
        self.selection = selection
        self['key_yellow'] = Button(_('Preview'))
        self['key_blue'] = Button(_('Description'))
        self['key_green'] = Button(_('Install'))
        self['info'] = Label(_('Press menu for advanced options'))
        self['menu'] = MenuList([], True, eListboxPythonMultiContent)
        list = []
        self.list = list
        self.status = []
        self.slist = []
        ishotname = False
        if '_New update' in self.selection:
            self.selection = self.selection.replace('_New update', '')
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    item = plugin.getAttribute('name').encode('utf8')
                    urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                    proper_url = checkhostname(urlserver)
                    if proper_url == True:
                        processmode = getipkversion(urlserver)
                        if self.selection == 'Cams' and item == 'list':
                            pass
                        else:
                            list.append([item, processmode])

        list.sort()
        self['menu'].onSelectionChanged.append(self.selectionChanged)
        self['actions'] = ActionMap(['SetupActions', 'MenuActions', 'ColorActions'], {'ok': self.selclicked,
         'cancel': self.close,
         'blue': self.desc,
         'yellow': self.preview,
         'green': self.selgreen,
         'menu': self.advanceinstall}, -2)
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.itempreview = False
        self.onShow.append(self.selectionChanged)
        self.getfreespace()
        self.ListToMulticontent()

    def refresh(self):
        if self.ipkgremove == False:
            png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/green.png')
            txt = 'remove'
        else:
            png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/grey.png')
            txt = 'install'
        idx = self['menu'].getSelectionIndex()
        self.list[idx][1] = txt
        item = self.list[idx][0]
        res = []
        res.append(MultiContentEntryText(pos=(0, 1), size=(5, 30), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
        res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 1), size=(30, 30), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(30, 1), size=(580, 30), font=0, flags=RT_HALIGN_LEFT, text=item, color=16777215, color_sel=16777215))
        self.theevents[idx] = res
        self['menu'].l.setList(self.theevents)
        res = []
        self['menu'].show()
        self.getfreespace()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self['menu'].l.setItemHeight(35)
        self['menu'].l.setFont(0, gFont('Regular', 22))
        self.menulist = []
        for i in range(0, len(self.list)):
            pngtext = str(self.list[i][1])
            self.status.append(pngtext)
            item = str(self.list[i][0])
            x = item.strip()
            endstr = x[-2:]
            self.slist.append(endstr)
            if x[-2:] == '-p':
                item = x[:-2]
            elif x[-2:] == '-d':
                item = x[:-2]
            elif x[-2:] == '-b':
                item = x[:-2]
            if pngtext == 'install':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/grey.png')
            elif pngtext == 'update':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/yellow.png')
            elif pngtext == 'remove':
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/nbuttons/green.png')
            else:
                png = resolveFilename(SCOPE_PLUGINS, 'Extensions/PurePrestige/images/button_green.png')
                png = LoadPixmap(png)
            res.append(MultiContentEntryText(pos=(0, 1), size=(5, 30), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 1), size=(30, 30), png=loadPNG(png)))
            res.append(MultiContentEntryText(pos=(30, 1), size=(870, 30), font=0, flags=RT_HALIGN_LEFT, text=item, color=16777215, color_sel=16777215))
            theevents.append(res)
            res = []

        self.theevents = []
        self.theevents = theevents
        self['menu'].l.setList(theevents)
        self['menu'].show()

    def desc(self):
        if self.itemdes:
            pass
        else:
            return
        try:
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex][0]
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    urlserver = ''
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.urlserver = ''
                        if urlserver.endswith('.ipk'):
                            self.urlserver = urlserver.replace('.ipk', '.txt')
                        elif urlserver.endswith('.tar.gz'):
                            self.urlserver = urlserver.replace('.tar.gz', '.txt')
                        elif urlserver.endswith('.tar.bz2'):
                            self.urlserver = urlserver.replace('.tar.bz2', '.txt')
                        elif urlserver.endswith('.tbz2'):
                            self.urlserver = urlserver.replace('.tbz2', '.txt')
                        elif urlserver.endswith('.tbz'):
                            self.urlserver = urlserver.replace('.tbz', '.txt')
                        if self.urlserver:
                            self.session.open(DescScreen, self.urlserver)

    def preview(self):
        if self.itempreview:
            pass
        else:
            return
        try:
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex][0]
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        if urlserver.endswith('.ipk'):
                            self.urlserver = urlserver.replace('.ipk', '.jpg')
                        elif urlserver.endswith('.tar.gz'):
                            self.urlserver = urlserver.replace('.tar.gz', '.jpg')
                        elif urlserver.endswith('.tar.bz2'):
                            self.urlserver = urlserver.replace('.tar.bz2', '.jpg')
                        elif urlserver.endswith('.tbz2'):
                            self.urlserver = urlserver.replace('.tbz2', '.jpg')
                        elif urlserver.endswith('.tbz'):
                            self.urlserver = urlserver.replace('.tbz', '.jpg')
                        self.session.open(pplayer.PurePrestigePictureScreen, self.urlserver)

    def selectionChanged(self):
        try:
            selection = self['menu'].getCurrent()
            cindex = self['menu'].getSelectionIndex()
            self.ipkgremove = False
            endstr = self.slist[cindex]
            self.pngtext = self.list[cindex][1]
            if self.pngtext == 'install':
                self['key_green'].setText('Install')
            elif self.pngtext == 'update':
                self['key_green'].setText('Update')
            elif self.pngtext == 'remove':
                self['key_green'].setText('Remove')
            if endstr == '-p':
                self['key_yellow'].show()
                self['key_blue'].hide()
                self.itempreview = True
                self.itemdes = False
            elif endstr == '-d':
                self['key_yellow'].hide()
                self['key_blue'].show()
                self.itempreview = False
                self.itemdes = True
            elif endstr == '-b':
                self['key_yellow'].show()
                self['key_blue'].show()
                self.itempreview = True
                self.itemdes = True
            else:
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.itempreview = False
                self.itemdes = False
        except:
            pass

    def getfreespace(self):
        fspace = freespace()
        self.freespace = fspace
        self.setTitle(self.freespace)

    def selgreen(self):
        try:
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex][0]
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.prombt(urlserver, pluginname, 'green')

    def selclicked(self):
        try:
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex][0]
        except:
            return

        self.url = ''
        self.pluginname = ''
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.prombt(urlserver, pluginname, 'ok')

    def prombt(self, com, dom, action):
        self.com = com
        self.dom = dom
        instr = 'Downloading and installing ' + self.com + '\n'
        instr = instr + 'Please wait while addon is being downloaded...\n  Restarting enigma2 is required after successful installation'
        endstr = 'Press OK to exit'
        if action == 'ok':
            if com.endswith('.ipk'):
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                self.session.openWithCallback(self.getfreespace, DownLoadgz, self.com, self.dom, instr, endstr)
                self.ipkgremove = False
        elif com.endswith('.ipk'):
            if self.pngtext == 'install' or self.pngtext == 'update':
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                ipkbasefile = str(os.path.basename(com))
                try:
                    ipkname = ''
                    ipkparts = []
                    ipkparts = ipkbasefile.split('_')
                    com = str(ipkparts[0]).strip()
                except:
                    com = str(os.path.basename(com))

                self.session.open(Console2.PurePrestigeConsole2, _('removing: %s') % dom, ['opkg remove  %s' % com], self.refresh, False, instr, endstr)
                self.ipkgremove = True
        else:
            self.session.openWithCallback(self.getfreespace, DownLoadgz, self.com, self.dom, instr, endstr)
            self.ipkgremove = False

    def getcommandList(self):
        clist = []
        clist.append((_('opkg update'), 'update:update opkg lists and install package'))
        clist.append((_('Install with config values overwrite'), 'install -force-maintainer:install package with overwrite preexisting config values'))
        clist.append((_('Force overwrite'), 'install -force-overwrite:install package with overwrite pre-exist files'))
        clist.append((_('Force depends'), 'install -force-depends:install with package with dependent packages'))
        clist.append((_('Force noaction'), 'install -force-noaction:install for test no action taken'))
        clist.append((_('Force reinstall'), 'install -force-reinstall:force re-install package'))
        clist.append((_('Install without depends'), 'install -nodeps:install without depencency'))
        return clist

    def askForSource(self, command):
        if command:
            self.menuclicked(command)

    def advanceinstall(self):
        self.session.openWithCallback(self.askForSource, ChoiceBox, _('select command'), self.getcommandList())

    def menuclicked(self, command = None):
        try:
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex][0]
        except:
            return

        self.url = ''
        self.pluginname = ''
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.menuprombt(urlserver, pluginname, 'ok', command)

    def menuprombt(self, com, dom, action, command):
        self.com = command[1] + ' ' + com
        self.dom = dom
        commandlist = command[1].split(':')
        self.commandstr = commandlist[0]
        commandesc = commandlist[1]
        instr = 'Downloading and installing ' + self.com + '\n'
        instr = instr + 'Please wait while addon is being downloaded...\n  Restarting enigma2 is required after successful installation' + '\n' + commandesc
        endstr = 'Press OK to exit'
        print 'mahmoud3828', self.com
        print '3829', self.commandstr
        if self.commandstr.strip() == 'update':
            self.com = 'install ' + com
            print '3830', 'ok'
            self.session.open(Console2.PurePrestigeConsole2, _('Updating opkg list:'), ['opkg update'], self.refresh, True, instr, '')
        if action == 'ok':
            if com.endswith('.ipk'):
                ccctext = 'opkg ' + self.com
                wfile(ccctext)
                print 'command', 'opkg ' + self.com
                self.session.open(Console2.PurePrestigeConsole2, _('downloading-' + self.commandstr + ':'), ['opkg ' + self.com], self.refresh, False, instr, endstr)
                self.ipkgremove = False
            else:
                self.session.open(MessageBox, _('No ipk package found'), type=1, timeout=4)
                self.ipkgremove = False


class DescScreen(Screen):
    if HD_Res == True:
        skin = '\n        \t\n                <screen name="DescScree" position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frametop.png" position="0,0" size="920,600"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frameleft.png" position="0,10" size="10,580"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frameright.png" position="910,10" size="10,580"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framebottom.png" position="0,590" size="920,10"/>\t\n                \n\t\t<widget name="text" position="30,30" size="865,570" font="Regular;22"  transparent="1" zPosition="2"  />\n                </screen>'
    else:
        skin = '\n        \t\n                <screen name="DescScree" position="center,center" size="640,520" title="Addon description"  >\n                \n\t\t<widget name="text" position="20,20" size="600,410" font="Regular;22"  transparent="1" zPosition="2"  />\n                </screen>'

    def __init__(self, session, url = None):
        self.skin = DescScreen.skin
        Screen.__init__(self, session)
        info = 'Gettings addon description,please wait...'
        self['text'] = ScrollLabel(info)
        self.url = url
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'ok': self.close,
         'cancel': self.close,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown,
         'left': self['text'].pageUp,
         'right': self['text'].pageDown}, -1)
        self.timer = eTimer()
        self.timer.callback.append(self.getpage())
        self.timer.start(100, 1)

    def getpage(self):
        try:
            if self.url == None:
                self['text'].setText('No description available,sorry ')
                return
            fp = urllib.urlopen(self.url)
            count = 0
            self.labeltext = ''
            while 1:
                s = fp.readline()
                count += 1
                self.labeltext += str(s)
                if not s:
                    break

            fp.close()
            self['text'].setText(self.labeltext)
        except:
            self['text'].setText('unable to download ')

        return


class DownLoadgz(Screen):
    skin = '\n\t\t<screen position="center,center" size="500,230" title="PurePrestige-Addons download" >\n\t\t\t\n                        \t\t\t\t\t\n\t\t\t\n\t\t\t<widget name="info" position="10,10" zPosition="4" size="490,220" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t\t        \n                </screen>'

    def __init__(self, session, url = None, dom = None, instr = None, endstr = None):
        self.skin = DownLoadgz.skin
        Screen.__init__(self, session)
        self.url = url
        self.dom = dom
        self.instr = instr
        self.endstr = endstr
        self['info'] = Label()
        self.downloading = False
        self['info'].setText('Downloading ' + self.dom + ',please wait..')
        self.timer = eTimer()
        self.timer.callback.append(self.download)
        self.timer.start(100, 1)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'cancel': self.close}, -2)

    def installaddon(self, testfilename):
        self.filename = testfilename
        self.commando = ''
        self['info'].setText('Installing ' + self.dom + '... please wait')
        try:
            if self.filename.endswith('.tar.gz'):
                self.commando = ['tar -xzvf ' + self.filename + ' -C /']
                self.SysExecution()
            elif self.filename.endswith('.tar.bz2') or self.filename.endswith('.tbz2') or self.filename.endswith('.tbz'):
                self.commando = ['tar -xjvf ' + self.filename + ' -C /']
                self.SysExecution()
            else:
                self['info'].setText('Failed installing ' + self.dom + '... Format not supported')
                return
        except:
            self['info'].setText('Failed to install  ' + self.dom)

    def SysExecution(self):
        self.instr = 'Installing ' + self.dom + '...please wait\n restart enigma2 after successful installation'
        self.endstr = 'press OK to exit'
        self.session.open(Console2.PurePrestigeConsole2, _('Installing: %s') % self.dom, self.commando, self.dexit, False, self.instr, self.endstr)

    def dexit(self):
        try:
            dirsremove(TMP_IMPORT_PWD)
        except:
            pass

        self.close()

    def download(self):
        try:
            dirsremove(TMP_IMPORT_PWD)
        except:
            pass

        try:
            os.mkdir(TMP_IMPORT_PWD)
        except:
            pass

        url = urlparse(self.url)
        try:
            conn = httplib.HTTPConnection(url.netloc)
            conn.request('GET', url.path)
            httpres = conn.getresponse()
            if httpres.status == 200:
                tmp = url.path.split('/')
                filename = TMP_IMPORT_PWD + '/' + tmp[len(tmp) - 1]
                out = open(filename, 'w')
                out.write(httpres.read())
                out.close()
                self['info'].setText('Installing ' + self.dom + '... please wait')
                self.installaddon(filename)
            else:
                self['info'].setText('Failed downloading ' + self.dom + '... No internet connection or server down')
                return
        except Exception as e:
            print e
            self['info'].setText('Failed downloading ' + self.dom + '... No internet connection or server down')
            return


class PurePrestigeIpkgTutorials(Screen):
    skin = '\n\t\t<screen position="center,center" size="600,430" title="PurePrestige-Addons" >\n\t\t\t  <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/bg2.png" position="0,0" size="620,450"/>\n                          <widget name="menu" position="10,0" size="590,373" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t                  <ePixmap position="15,377" size="570,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n                                   \n                </screen>\n\t\t'

    def __init__(self, session, xmlparse, selection):
        self.skin = Extensions / PurePrestige.skin
        Screen.__init__(self, session)
        self.xmlparse = xmlparse
        self.selection = selection
        list = []
        self.list = list
        slist = []
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    item = plugin.getAttribute('name').encode('utf8')
                    list.append(item)

        list.sort()
        self['menu'] = MenuList(list)
        self['actions'] = ActionMap(['SetupActions'], {'ok': self.selclicked,
         'cancel': self.close}, -2)
        self.itempreview = False
        self.getfreespace()

    def getfreespace(self):
        fspace = freespace()
        self.freespace = fspace
        self.setTitle(self.freespace)

    def selclicked(self):
        try:
            cindex = self['menu'].getSelectionIndex()
            selection_country = self.list[cindex]
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
        self.session.open(TutorialsScreen, com)


class TutorialsScreen(Screen):
    skin = '\n\t<screen position="center,center" size="550,460" title="Tutorials" >\n\t\t\n                \n\t\t<widget name="text" position="10,10" size="530,440" font="Regular;22" />\n\t\t\n\t</screen>'

    def __init__(self, session, url = None):
        self.skin = TutorialsScreen.skin
        Screen.__init__(self, session)
        info = 'Getting tutorial,please wait...'
        self.url = url
        self['text'] = ScrollLabel(info)
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'ok': self.close,
         'cancel': self.close,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown,
         'left': self['text'].pageUp,
         'right': self['text'].pageDown}, -1)
        self.timer = eTimer()
        self.timer.callback.append(self.downloadupdates)
        self.timer.start(100, 1)

    def downloadupdates(self):
        try:
            fp = urllib.urlopen(self.url)
            count = 0
            self.labeltext = ''
            while 1:
                s = fp.readline()
                count += 1
                self.labeltext += str(s)
                if not s:
                    break

            fp.close()
            self['text'].setText(self.labeltext)
        except:
            self['text'].setText('unable to download tutorial')
