from enigma import eTimer, eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, getDesktop, loadPNG, loadPic
from Components.Label import Label
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Label import Label
from Components.Button import Button
from Components.Pixmap import Pixmap
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
from Plugins.Plugin import PluginDescriptor
import os
from time import *
import time
import datetime

c7color = 11403055
c2color = 16753920
c1color = 16776960
c3color = 15657130
c5color = 16711680
c4color = 16729344
c6color = 65407
c8color = 13047173
c9color = 13789470

cronmanager_path = '/etc/cron'
cronmanager_script = '/etc/cron/cronmanager.sh'
cronsyntax_path = '/etc/cron/cronsyntax.txt'
cronmanager_pluginversion = '1.0'

def main(session, **kwargs):
    try:
        session.open(PurePrestigecrondsscreen)
    except:
        print '[CRONMANAGER] Pluginexecution failed'


def autostart(reason, **kwargs):
    if reason == 0:
        print '[CRONMANAGER] no autostart'


def Plugins(**kwargs):
    return PluginDescriptor(name=_('Crondmanager'), description=_('plugin to do manage cron daemon'), where=PluginDescriptor.WHERE_PLUGINMENU, icon='crondmanager.png', fnc=main)


class crondscriptsscrn(Screen):
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    if HD_Res:
        skin = '\n\t\t<screen position="center,center" size="800,520" title="Add cron " >\n\t\n                <widget source="global.CurrentTime" render="Label" position="520, 460" zPosition="1" size="100, 20" font="Regular; 20" halign="center" transparent="1" >\n                       <convert type="ClockToText"/>\n                </widget>\n \n        \t\t  <widget name="ButtonBluetext" position="20,0" size="200,40" valign="center" halign="left" zPosition="10" font="Regular;22" transparent="1" />\n\t\t\t  <widget name="ButtonBlue" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/button_blue.png" position="0,10" zPosition="10" size="100,100" transparent="1" alphatest="on" />\n\t\t\t  <widget name="ButtonYellowtext" position="250,0" size="200,40" valign="center" halign="left" zPosition="10" font="Regular;22" transparent="1" />\n\t\t\t  <widget name="ButtonYellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/button_yellow.png" position="230,10" zPosition="10" size="200,100" transparent="1" alphatest="on" />\n\t                  <widget name="ButtonGreentext" position="450,0" size="200,40" valign="center" halign="left" zPosition="10" font="Regular;22" transparent="1" />\n\t\t\t  <widget name="ButtonGreen" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/button_green.png" position="430,10" zPosition="10" size="200,100" transparent="1" alphatest="on" />\n      \n  \n                          <widget name="info" position="620,460" zPosition="4" size="180,45" font="Regular;20" foregroundColor="yellow" transparent="1" halign="left"  />\n                          <widget name="menu" position="10,60" size="780,325" scrollbarMode="showOnDemand" />\n                         <widget name="info2" position="20,390" zPosition="4" size="760,70" font="Regular;20" foregroundColor="yellow" transparent="1" halign="center" valign="center" />\t                  \n        \t</screen>\n\t\t'
    else:
        skin = '\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520" transparent="1"/>\t\n              <!-- Clock -->\n        \n        <widget source="global.CurrentTime" render="Label" position="420,470" zPosition="1" size="50, 20" font="Regular; 20" halign="right">\n            <convert type="ClockToText"/>\n        </widget>\n       \n\n                <ePixmap position="15,50" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\t\t\t  \n\t\t\t  <widget name="ButtonBluetext" position="40,10" size="160,40" valign="center" halign="left" zPosition="10" font="Regular;22" transparent="1" />\n                          <widget name="ButtonBlue" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/button_blue.png" position="20,20" zPosition="10" size="100,100" transparent="1" alphatest="on" />\n\t\t\t  <widget name="ButtonYellowtext" position="250,10" size="200,40" valign="center" halign="left" zPosition="10" font="Regular;22" transparent="1" />\n\t\t\t  <widget name="ButtonYellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/button_yellow.png" position="230,20" zPosition="10" size="200,100" transparent="1" alphatest="on" />\n\t                  <widget name="ButtonGreentext" position="460,10" size="200,40" valign="center" halign="left" zPosition="10" font="Regular;22" transparent="1" />\n\t\t\t  <widget name="ButtonGreen" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/button_green.png" position="440,20" zPosition="10" size="200,100" transparent="1" alphatest="on" />\n                                  \n                          \n                          <widget name="info" position="480,460" zPosition="4" size="440,45" font="Regular;20" foregroundColor="yellow" transparent="1" halign="left" valign="center" />\n                          <widget name="menu" position="25,60" size="590,325" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n                        <widget name="info2" position="20,390" zPosition="4" size="600,70" font="Regular;20" foregroundColor="yellow" transparent="1" halign="center" valign="center" />\t                  \n        \t</screen>\n\t\t'

    def __init__(self, session):
        self.skin = crondscriptsscrn.skin
        Screen.__init__(self, session)
        list = []
        self['menu'] = MenuList(list)
        self['ButtonBlue'] = Pixmap()
        self['ButtonGreen'] = Pixmap()
        self['ButtonBluetext'] = Label(_('Add with time'))
        self['ButtonYellow'] = Pixmap()
        self['ButtonYellowtext'] = Label(_('Add after time'))
        self['ButtonGreentext'] = Label(_('Advanced'))
        now = datetime.datetime.now()
        ntime = now.strftime('%Y-%m-%d')
        self['info'] = Label(ntime)
        self['info2'] = Label('FTP your script to etc/cron/scripts or select script from the list')
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'yellow': self.addcronaftertime,
         'blue': self.addcron,
         'ok': self.addcron,
         'green': self.advanced,
         'cancel': self.close}, -2)
        self.fillskins()

    def fillskins(self):
        list = []
        scripts = []
        self['menu'].setList(scripts)
        path = '/etc/cron/scripts'
        self.path = path
        try:
            for x in os.listdir(path):
                x = x.replace('.sh', '')
                if not x == 'cam' or not x == 'script':
                    scripts.append(x)

            scripts.sort()
            if len(scripts) > 0:
                self['menu'].setList(scripts)
                self['ButtonBluetext'].show()
                self['ButtonYellowtext'].show()
                self['ButtonGreentext'].show()
            else:
                self['ButtonBluetext'].hide()
                self['ButtonYellowtext'].hide()
                self['ButtonGreentext'].hide()
        except:
            pass

    def advanced(self):
        path = '/etc/cron/scripts/'
        try:
            selectedfolder = self['menu'].getCurrent()
            scriptpath = path + selectedfolder + '.sh'
            instr = 'Please wait while script is being  executed...'
            endstr = 'Press Ok to exit'
            dom = ' script'
            os.chmod(scriptpath, 755)
            AddCommandadvanced(self.session, selectedfolder, scriptpath)
        except:
            pass

    def addcron(self):
        path = '/etc/cron/scripts/'
        try:
            selectedfolder = self['menu'].getCurrent()
            scriptpath = path + selectedfolder + '.sh'
            instr = 'Please wait while script is being  executed...'
            endstr = 'Press Ok to exit'
            dom = ' script'
            os.chmod(scriptpath, 755)
            AddCommandWizzard(self.session, selectedfolder, scriptpath)
        except:
            pass

    def addcronaftertime(self):
        path = '/etc/cron/scripts/'
        try:
            selectedfolder = self['menu'].getCurrent()
            scriptpath = path + selectedfolder + '.sh'
            instr = 'Please wait while script is being  executed...'
            endstr = 'Press Ok to exit'
            dom = ' script'
            os.chmod(scriptpath, 755)
            LaterCommandWizzard(self.session, selectedfolder, scriptpath)
        except:
            pass


class PurePrestigecronsscreen(Screen):
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
        skin = '\n        \t\n                <screen  position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frame.png" position="0,0" size="920,600"/>\t\n                <widget name="croninfo" position="700,40" zPosition="4" size="200,30" font="Regular;20" foregroundColor="yellow" transparent="1" halign="left" valign="center" />                                   \n                <widget name="tdate" position="70,20" zPosition="4" size="200,80" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />                \n                <widget name="tscript" position="270,20" zPosition="4" size="600,80" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />                                \n                <widget name="list" position="50,100" size="850,300" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<ePixmap position="15,490" size="890,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n                <widget source="global.CurrentTime" render="Label" position="340, 553" zPosition="1" size="100, 20" font="Regular; 20" halign="right" transparent="1" >\n                       <convert type="ClockToText"/>\n                </widget>\t\t\n                \n\t        <ePixmap name="red" position="30,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/red.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_red" position="0,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="yellow" position="260,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t\t  \n                <widget name="key_yellow" position="230,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="green" position="470,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="440,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="blue" position="680,510" zPosition="4" size="160,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_blue" position="650,520" zPosition="5" size="200,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <widget name="infolabel" position="20,550" zPosition="4" size="350,30" font="Regular;18" foregroundColor="yellow" transparent="1" halign="left" valign="center" />                                              \n                <widget name="info" position="450,550" zPosition="4" size="200,30" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />\n                </screen>'
    else:
        skin = '\n        \t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\t\n        <widget name="croninfo" position="500,20" zPosition="4" size="120,30" font="Regular;18" foregroundColor="yellow" transparent="1" halign="left" valign="center" />                  \n    <widget name="tdate" position="70,20" zPosition="4" size="200,80" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />                \n                <widget name="tscript" position="270,20" zPosition="4" size="600,80" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />                                   \n                <widget name="list" position="32,100" size="596,240" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<ePixmap position="15,368" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n                <widget source="global.CurrentTime" render="Label" position="340, 487" zPosition="1" size="100, 20" font="Regular; 20" halign="right">\n                 <convert type="ClockToText"/>\n                </widget>\t\t\n\t        <ePixmap name="red" position="30,380" zPosition="4" size="100,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/red.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_red" position="0,390" zPosition="5" size="150,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="yellow" position="160,380" zPosition="4" size="110,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t\t  \n                <widget name="key_yellow" position="130,390" zPosition="5" size="150,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="green" position="300,380" zPosition="4" size="110,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_green" position="280,390" zPosition="5" size="150,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <ePixmap name="blue" position="430,380" zPosition="4" size="110,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_blue" position="410,390" zPosition="5" size="150,30" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n                <widget name="infolabel" position="20,480" zPosition="4" size="300,30" font="Regular;18" foregroundColor="yellow" transparent="1" halign="left" valign="center" />                          \n                <widget name="info" position="450,480" zPosition="4" size="640,30" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />\n                </screen>'

    def __init__(self, session):
        self.skin = PurePrestigecronsscreen.skin
        Screen.__init__(self, session)
        self['key_yellow'] = Button(_('Add'))
        self['key_green'] = Button(_('Run cron'))
        self['key_blue'] = Button(_('Stop cron'))
        self['croninfo'] = Label(_('info'))
        self['key_red'] = Button(_('Remove'))
        title = 'CronManager'
        self['infolabel'] = Label(title)
        now = datetime.datetime.now()
        ntime = now.strftime('%Y-%m-%d')
        self['info'] = Label(ntime)
        self['tdate'] = Label('minute/hr/date')
        self['tscript'] = Label('script name')
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        list = []
        self.list = list
        self['actions'] = ActionMap(['ColorActions', 'SetupActions'], {'red': self.deletecrontab,
         'ok': self.close,
         'cancel': self.close,
         'yellow': self.addcron,
         'green': self.startcron,
         'blue': self.stopcron}, -2)
        self.cronfilepath = '/etc/cron/crontabs/root'
        self.mydatalist = []
        if not os.path.exists(self.cronfilepath):
            self.mydatalist = []
            return
        openfile = open(self.cronfilepath, 'r')
        self.mydatalist = openfile.readlines()
        openfile.close()
        self.onShow.append(self.ListToMulticontent)
        self.ListToMulticontent()
        self.getcroninfo()

    def restartcron(self):
        self.stopcron()
        self.startcron()

    def startcron(self):
        cmd = '%s start' % cronmanager_script
        os.system(cmd)
        self.getcroninfo()

    def stopcron(self):
        cmd = '%s stop' % cronmanager_script
        os.system(cmd)
        self.getcroninfo()

    def readstatus(self):
        cronstatusfile = '/etc/cron/cronstatus.txt'
        openfile = open(cronstatusfile, 'r')
        a = openfile.readlines()
        for i in range(0, len(a)):
            item = a[i]
            if 'sbin' in item:
                self['croninfo'].setText('cron is running')
                self['key_green'].hide()
                self['key_blue'].show()
                return

        self['croninfo'].setText('cron is stopped')
        self['key_green'].show()
        self['key_blue'].hide()

    def getcroninfo(self):
        cmd = '%s info >/etc/cron/cronstatus.txt' % cronmanager_script
        os.system(cmd)
        self.readstatus()

    def addcron(self):
        self.session.openWithCallback(self.refresh, crondscriptsscrn)

    def deletecrontab(self):
        try:
            cindex = self['list'].getSelectionIndex()
            self.mydatalist.pop(cindex)
            openfile = open(self.cronfilepath, 'w')
            openfile.write(''.join(self.mydatalist))
            openfile.close()
            self.ListToMulticontent()
            self.restartcron()
        except:
            pass

    def refresh(self):
        self.mydatalist = []
        if not os.path.exists(self.cronfilepath):
            self.mydatalist = []
            return
        openfile = open(self.cronfilepath, 'r')
        self.mydatalist = openfile.readlines()
        openfile.close()
        self.ListToMulticontent()
        self.getcroninfo()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.mydatalist
        self['list'].l.setItemHeight(60)
        self['list'].l.setFont(0, gFont('Regular', 25))
        for i in range(0, len(self.events)):
            item = self.events[i]
            parts = item.split('/etc/')
            ntime = parts[0]
            astcount = ntime.count('*')
            if astcount == 3:
                repstr = 'Daily'
            elif astcount == 0:
                repstr = 'Once'
            else:
                repstr = 'custom'
            scriptpath = parts[1]
            scr = scriptpath.split('/')
            if repstr == 'custom':
                pass
            else:
                ntime = ntime.replace('*', '')
            script = scr[2]
            script = script.replace('.sh', '')
            res.append(MultiContentEntryText(pos=(0, 25), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=c2color, color_sel=16777215))
            res.append(MultiContentEntryText(pos=(30, 25), size=(200, 120), font=0, flags=RT_HALIGN_LEFT, text=ntime, color=c2color, color_sel=c2color))
            res.append(MultiContentEntryText(pos=(230, 25), size=(500, 120), font=0, flags=RT_HALIGN_LEFT, text=script, color=16777215, color_sel=16777215))
            res.append(MultiContentEntryText(pos=(730, 25), size=(200, 120), font=0, flags=RT_HALIGN_LEFT, text=repstr, color=16777215, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()


class AddCommandadvanced(Screen):

    def __init__(self, session, scripttitle, scriptpath):
        self.scriptpath = scriptpath
        self.scripttitle = scripttitle
        self.session = session
        self.askForCommand()

    def restartcron(self):
        cmd = '%s stop' % cronmanager_script
        os.system(cmd)
        cmd = '%s start' % cronmanager_script
        os.system(cmd)

    def askForCommand(self):
        now = datetime.datetime.now()
        nhour = str(now.hour)
        nminute = str(now.minute)
        if len(nminute) == 1:
            nminute = '0' + nminute
        ntime = nminute + ' ' + nhour + ' *' + ' *' + ' *' + ' *'
        ntime = '* * * * * *'
        thelp = 'you can generate your crontab syntax from \nhttp://www.corntab.com/pages/crontab-gui\n and copy the syntax to the file /etc/cron/cronsyntax.txt'
        fp = open(cronsyntax_path)
        line = fp.readline()
        fp.close()
        if line == '':
            line = '* * * * *'
        self.session.openWithCallback(self.processingCommand, InputBox, title=_('Enter cron syntax to execute script ' + self.scripttitle + '\n' + thelp), text=line, maxSize=True, type=Input.TEXT)

    def processingCommand(self, targetname):
        if targetname is None:
            pass
        else:
            self.targetname = targetname.strip() + ' ' + self.scriptpath.strip()
            self.session.openWithCallback(self.DoCommand, MessageBox, _('are you sure to add this script to crontab: %s ?' % self.targetname), MessageBox.TYPE_YESNO)
        return

    def DoCommand(self, answer):
        if answer is None:
            self.skipCommand(_('answer is None'))
        if answer is False:
            self.skipCommand(_('you were not confirming'))
        else:
            title = _('adding script %s to crontab with time') % self.targetname
            cmd = '%s add %s >/tmp/action.txt' % (cronmanager_script, self.targetname)
            cronroot = '/etc/cron/crontabs/root'
            f = open(cronroot, 'a')
            f.write(self.targetname + '\n')
            f.close()
            self.restartcron()
            self.session.open(MessageBox, _('Cron added successfully'), MessageBox.TYPE_WARNING, 3)
            return
            os.system(cmd)
            actionpath = '/tmp/action.txt'
            if os.path.getsize(actionpath) < 200:
                self.session.open(MessageBox, _('adding cron failed'), MessageBox.TYPE_WARNING, 3)
            else:
                self.session.open(MessageBox, _('Cron added successfully'), MessageBox.TYPE_WARNING, 3)
        return

    def skipCommand(self, reason):
        pass


class AddCommandWizzard(Screen):

    def __init__(self, session, scripttitle, scriptpath):
        self.scriptpath = scriptpath
        self.scripttitle = scripttitle
        self.session = session
        self.askForCommand()

    def restartcron(self):
        cmd = '%s stop' % cronmanager_script
        os.system(cmd)
        cmd = '%s start' % cronmanager_script
        os.system(cmd)

    def askForCommand(self):
        now = datetime.datetime.now()
        nhour = str(now.hour)
        nminute = str(now.minute)
        if len(nminute) == 1:
            nminute = '0' + nminute
        ntime = nminute + ' ' + nhour
        self.session.openWithCallback(self.processingCommand, InputBox, title=_('Enter time to execute script ' + self.scripttitle), text=ntime, maxSize=False, type=Input.TEXT)

    def processingCommand(self, targetname):
        if targetname is None:
            pass
        else:
            self.targetname = self.scriptpath + ' ' + targetname
            self.session.openWithCallback(self.DoCommand, MessageBox, _('are you sure to add this script to crontab: %s ?' % self.targetname), MessageBox.TYPE_YESNO)
        return

    def DoCommand(self, answer):
        if answer is None:
            self.skipCommand(_('answer is None'))
        if answer is False:
            self.skipCommand(_('you were not confirming'))
        else:
            title = _('adding script %s to crontab with time') % self.targetname
            cmd = '%s add %s >/tmp/action.txt' % (cronmanager_script, self.targetname)
            os.system(cmd)
            self.restartcron()
            actionpath = '/tmp/action.txt'
            if os.path.getsize(actionpath) < 200:
                self.session.open(MessageBox, _('adding cron failed'), MessageBox.TYPE_WARNING, 3)
            else:
                self.session.open(MessageBox, _('Cron added successfully'), MessageBox.TYPE_WARNING, 3)
        return

    def skipCommand(self, reason):
        pass


class LaterCommandWizzard(Screen):

    def __init__(self, session, scripttitle, scriptpath):
        self.scriptpath = scriptpath
        self.scripttitle = scripttitle
        self.session = session
        self.askForLaterCommand()

    def restartcron(self):
        cmd = '%s stop' % cronmanager_script
        os.system(cmd)
        cmd = '%s start' % cronmanager_script
        os.system(cmd)

    def askForLaterCommand(self):
        self.session.openWithCallback(self.processingLaterCommand, InputBox, title=_('Enter time to execute script ' + self.scripttitle), text='60', maxSize=False, type=Input.TEXT)

    def processingLaterCommand(self, targetname):
        if targetname is None:
            pass
        else:
            self.targetname = self.scriptpath + ' ' + targetname
            self.session.openWithCallback(self.DoLaterCommand, MessageBox, _('are you sure to add this script to crontab: %s ?' % self.targetname), MessageBox.TYPE_YESNO)
        return

    def DoLaterCommand(self, answer):
        if answer is None:
            self.skipLaterCommand(_('answer is None'))
        if answer is False:
            self.skipLaterCommand(_('you were not confirming'))
        else:
            title = _('adding script %s to crontab after time') % self.targetname
            cmd = '%s delay %s >/tmp/action.txt' % (cronmanager_script, self.targetname)
            os.system(cmd)
            self.restartcron()
            actionpath = '/tmp/action.txt'
            if os.path.getsize(actionpath) < 200:
                self.session.open(MessageBox, _('adding cron failed'), MessageBox.TYPE_WARNING, 3)
            else:
                self.session.open(MessageBox, _('Cron added successfully'), MessageBox.TYPE_WARNING, 3)
        return

    def skipLaterCommand(self, reason):
        self.session.open(MessageBox, _('delay script to crontab was canceled, because %s') % reason, MessageBox.TYPE_WARNING)


class RestartWizzard(Screen):

    def __init__(self, session):
        self.session = session
        self.askForRestart()

    def askForRestart(self):
        self.session.openWithCallback(self.askForCommand, ChoiceBox, _('select restart command to be executed'), self.getCommandList())

    def askForCommand(self, source):
        if source is None:
            self.skipRestart(_('no command passed, skipping restart'))
        else:
            self.source = source[1]
            self.session.openWithCallback(self.restartCommand, MessageBox, _('are you sure to %s') % self.source, MessageBox.TYPE_YESNO)
        return

    def restartCommand(self, answer):
        if answer is None:
            self.skipRestart(_('answer is None'))
        if answer is False:
            self.skipRestart(_('you were not confirming'))
        else:
            title = _('executing command on Dreambox')
            cmd = '%s %s' % (cronmanager_script, self.source)
            os.system([cmd])
        return

    def skipRestart(self, reason):
        pass

    def getCommandList(self):
        images = []
        images.append((_('info if cron daemon is running'), 'info'))
        images.append((_('start cron daemon'), 'start'))
        images.append((_('stop cron daemon'), 'stop'))
        images.append((_('restart cron daemon'), 'restart'))
        images.append((_('reboot Dreambox'), 'reboot'))
        images.append((_('halt Dreambox'), 'halt'))
        images.append((_('restart Enigma on Dreambox'), 'kill'))
        return images


class ChangeTimeWizzard(Screen):

    def __init__(self, session):
        self.session = session
        jetzt = time.time()
        timezone = datetime.datetime.utcnow()
        delta = jetzt - time.mktime(timezone.timetuple())
        print 'delta: %i' % delta
        print 'oldtime: %i' % jetzt
        self.oldtime = strftime('%Y:%m:%d %H:%M', localtime())
        self.session.openWithCallback(self.askForNewTime, InputBox, title=_('Enter new Systemtime - OK will restart enigma2 !'), text='%s' % self.oldtime, maxSize=16, type=Input.NUMBER)

    def askForNewTime(self, newclock):
        try:
            length = len(newclock)
        except:
            length = 0

        if newclock is None:
            self.skipChangeTime(_('no new time'))
        elif (length == 16) is False:
            self.skipChangeTime(_('new time string too short'))
        elif (newclock.count(' ') < 1) is True:
            self.skipChangeTime(_('invalid format'))
        elif (newclock.count(':') < 3) is True:
            self.skipChangeTime(_('invalid format'))
        else:
            full = []
            full = newclock.split(' ', 1)
            newdate = full[0]
            newtime = full[1]
            print 'newdate %s newtime %s' % (newdate, newtime)
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
                self.skipChangeTime(_('invalid year %s') % newyear)
            elif int(newmonth) < 0 or int(newmonth) > 12 or (len(newmonth) < 2) is True:
                self.skipChangeTime(_('invalid month %s') % newmonth)
            elif int(newday) < 1 or int(newday) > maxmonth or (len(newday) < 2) is True:
                self.skipChangeTime(_('invalid day %s') % newday)
            elif int(newhour) < 0 or int(newhour) > 23 or (len(newhour) < 2) is True:
                self.skipChangeTime(_('invalid hour %s') % newhour)
            elif int(newmin) < 0 or int(newmin) > 59 or (len(newmin) < 2) is True:
                self.skipChangeTime(_('invalid minute %s') % newmin)
            else:
                self.newtime = '%s%s%s%s%s' % (newmonth,
                 newday,
                 newhour,
                 newmin,
                 newyear)
                print 'date %s' % self.newtime
                self.session.openWithCallback(self.DoChangeTimeRestart, MessageBox, _('Enigma2 will restart to change Systemtime - OK ?'), MessageBox.TYPE_YESNO)
        return

    def DoChangeTimeRestart(self, answer):
        if answer is None:
            self.skipChangeTime(_('answer is None'))
        if answer is False:
            self.skipChangeTime(_('you were not confirming'))
        else:
            os.system('date %s' % self.newtime)
            quitMainloop(3)
        return

    def skipChangeTime(self, reason):
        self.session.open(MessageBox, _('Change Systemtime was canceled, because %s') % reason, MessageBox.TYPE_WARNING)
