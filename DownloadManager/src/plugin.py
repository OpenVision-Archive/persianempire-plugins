from Plugins.Plugin import PluginDescriptor
from Components.Sources.List import List
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import quitMainloop, eListboxPythonMultiContent, gFont, getDesktop, getBoxType
from Tools.LoadPixmap import LoadPixmap
from Components.MenuList import MenuList
from Components.Label import Label
from Tools.Directories import fileExists, resolveFilename, SCOPE_SKIN
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap
from twisted.web.client import getPage
import os
from Components.Button import Button
from Screens.Console import Console


class Ipkremove2(Screen):
    skin = """
		<screen position="center,center" size="800,500" title="Installed Packages List" >
			<!--widget name="text" position="0,0" size="550,25" font="Regular;20" /-->
			<widget name="list" position="50,50" size="700,400" scrollbarMode="showOnDemand" />
			<!--widget name="pixmap" position="200,0" size="190,250" /-->
			<!--eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />
			<widget name="info" position="100,230" zPosition="4" size="100,25" font="Regular;18" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" /-->
		</screen>"""
    def __init__(self, session):
		self.skin = Ipkremove2.skin
		Screen.__init__(self, session)
        	self["list"] = MenuList([])
		self["info"] = Label()
                self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
                self.data = []
                self.ict = 0
                self.onLayoutFinish.append(self.startSession)

    def startSession(self):
        if os.path.isfile('/etc/ipkinstalled') is not True:
            cmd = 'opkg list-installed | cut -f1 -d" " > /etc/ipkinstalled'
            os.system(cmd)
        try:
            myfile = open('/etc/ipkinstalled', 'r+')
            for line in myfile:
                n1 = line.find("_", 0)
                line = line[:n1]
                self.data.append(line)
            myfile.close()
            self["list"].setList(self.data)
        except:
            return
    
    def okClicked(self):
	        idx = self["list"].getSelectionIndex()
		ipk = self.data[idx]
		cmd = "opkg remove " + ipk
                title = _("Removing %s" %(ipk))
                self.session.open(Console,_(title),[cmd])


class RSList(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(30)
        self.l.setFont(0, gFont('Regular', 20))


def RSListEntry(download, state):
    res = [download]
    res.append(MultiContentEntryText(pos=(10, 0), size=(500, 30), font=0, text=download))
    if state == 0:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(600, 0), size=(26, 26), png=LoadPixmap(cached=True, desktop=getDesktop(0), path=resolveFilename(SCOPE_SKIN, 'skin_default/buttons/key_red.png'))))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(600, 0), size=(26, 26), png=LoadPixmap(cached=True, desktop=getDesktop(0), path=resolveFilename(SCOPE_SKIN, 'skin_default/buttons/key_green.png'))))
    return res


class Downloads(Screen):
    skin = '\n\t\t<screen position="center,center" size="520,400" title="Open Vision - https://openvision.tech" >\n\t\t\t<!--widget name="text" position="0,0" size="550,25" font="Regular;20" /-->\n\t\t\t<widget name="list" position="10,40" size="500,350" scrollbarMode="showOnDemand" />\n\t\t\t<!--widget name="pixmap" position="200,0" size="190,250" /-->\n\t\t\t<!--eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" /-->\n\t\t\t<widget name="info" position="80,80" zPosition="4" size="350,300" font="Regular;18" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />\n\t\t<ePixmap name="red"    position="20,380"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />\n\t\t<widget name="key_red" position="20,380" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />\n\t\t<ePixmap name="yellow"    position="180,380"   zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />\n\t\t<widget name="key_yellow" position="180,380" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />\n\t\t</screen>'

    def __init__(self, session):
        self.skin = Downloads.skin
        Screen.__init__(self, session)
        self['list'] = MenuList([])
        self['info'] = Label()
        self['actions'] = NumberActionMap(['WizardActions',
         'InputActions',
         'ColorActions',
         'DirectionActions'], {'ok': self.okClicked,
         'back': self.close,
         '1': self.keyNumberGlobal,
         '2': self.keyNumberGlobal,
         '3': self.keyNumberGlobal,
         '4': self.keyNumberGlobal,
         '5': self.keyNumberGlobal,
         '6': self.keyNumberGlobal,
         '7': self.keyNumberGlobal,
         '8': self.keyNumberGlobal,
         '9': self.keyNumberGlobal,
         '0': self.keyNumberGlobal,
         'red': self.uninstall,
         'green': self.okClicked,
         'yellow': self.restartgui}, -1)
        self['key_red'] = Button(_('Uninstall'))
        self['key_green'] = Button(_('Select'))
        self['key_yellow'] = Button(_('Restart GUI'))
        title = 'Download Manager - Categories'
        self['title'] = Button(title)
        self.icount = 0
        self.errcount = 0
        self.onLayoutFinish.append(self.openTest)

    def uninstall(self):
        self.session.open(Ipkremove2)
		
    def restartgui(self):
        quitMainloop(3)

    def openTest(self):
        xurl = 'https://openvision.tech/pedm/mipsel/' + 'index.html'
        getPage(xurl).addCallback(self.gotPage).addErrback(self.getfeedError)

    def gotPage(self, html):
        self.data = []
        icount = 0
        self.data = html.splitlines()
        self.data.append(getBoxType())
        self['info'].setText('')
        self['list'].setList(self.data)

    def getfeedError(self, error = ''):
        error = str(error)

    def okClicked(self):
        if self.errcount == 1:
            self.close()
        else:
            sel = self['list'].getSelectionIndex()
            addon = self.data[sel]
            self.session.open(Getipklist, addon)

    def keyLeft(self):
        self['text'].left()

    def keyRight(self):
        self['text'].right()

    def keyNumberGlobal(self, number):
        self['text'].number(number)


class Getipklist(Screen):
    skin = '\n\t\t<screen position="center,center" size="800,400" title="Open Vision - https://openvision.tech" >\n\t\t\t<widget name="text" position="100,20" size="200,30" font="Regular;20" halign="left" />\n                        <!--widget name="list" position="10,150" size="500,350" scrollbarMode="showOnDemand" /-->\n                        <widget name="list" position="50,80" size="730,300" scrollbarMode="showOnDemand" />\n\n                        <!--eLabel text="Installed" position="100,20" size="100,30" font="Regular;20" halign="left" /-->\n                        <ePixmap name="green"    position="200,20"   zPosition="4" size="26,26" pixmap="skin_default/buttons/key_green.png" transparent="1" alphatest="on" />\t\t\t\t\n\n\t\t\t<!--widget name="pixmap" position="200,0" size="190,250" /-->\n\t\t\t<eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />\n\t\t\t<widget name="info" position="100,230" zPosition="4" size="300,25" font="Regular;18" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t\t</screen>'

    def __init__(self, session, addon):
        self.skin = Getipklist.skin
        Screen.__init__(self, session)
        self.list = []
        self['text'] = Label()
        self['text'].setText(_('Installed'))
        self['list'] = List(self.list)
        self['list'] = RSList([])
        self['info'] = Label()
        self['actions'] = NumberActionMap(['WizardActions',
         'InputActions',
         'ColorActions',
         'DirectionActions'], {'ok': self.okClicked,
         'back': self.cancel,
         '1': self.keyNumberGlobal,
         '2': self.keyNumberGlobal,
         '3': self.keyNumberGlobal,
         '4': self.keyNumberGlobal,
         '5': self.keyNumberGlobal,
         '6': self.keyNumberGlobal,
         '7': self.keyNumberGlobal,
         '8': self.keyNumberGlobal,
         '9': self.keyNumberGlobal,
         '0': self.keyNumberGlobal,
         'red': self.close,
         'green': self.okClicked}, -1)
        self['key_red'] = Button(_('Cancel'))
        self['key_green'] = Button(_('Select'))
        title = addon + ' List'
        self['title'] = Button(title)
        self.addon = addon
        self.icount = 0
        self.names = []
        self.onLayoutFinish.append(self.openTest)
        
    def ipkrem(self):
        self.session.open(Ipkremove)    

    def cancel(self):
        cmd = 'rm -rf /tmp/*.ipk /tmp/.*.txt /etc/ipkinstalled'
        os.system(cmd)
        self.close()

    def openTest(self):
        self['info'].setText('Downloading List ...')
        testno = 1
        xurl = 'https://openvision.tech/pedm/mipsel/' + self.addon + '/index.html'
        getPage(xurl).addCallback(self.gotPage).addErrback(self.getfeedError)

    def gotPage(self, html):
        self.data = []
        icount = 0
        self.data = html.splitlines()
        list = []
        for line in self.data:
            ipkname = self.data[icount]
            ipos = ipkname.find('_')
            remname = ipkname[:ipos]
            state = self.getstate(remname)
            list.append(RSListEntry(remname, state))
            icount = icount + 1
        self['list'].setList(list)
        self['info'].setText('')

    def getfeedError(self, error = ''):
        error = str(error)

    def getstate(self, remname):
        if os.path.isfile('/etc/ipkinstalled') is not True:
            cmd = 'opkg list-installed | cut -f1 -d" " > /etc/ipkinstalled'
            os.system(cmd)
        try:
            myfile = open('/etc/ipkinstalled', 'r+')
            icount = 0
            data = []
            ebuf = []
            for line in myfile:
                data.append(icount)
                data[icount] = line[:-1]
                if data[icount] == remname:
                    state = 1
                    return state
                icount = icount + 1
            myfile.close()
            state = 0
            return state
        except:
            state = 0
            return state

    def okClicked(self):
        sel = self['list'].getSelectionIndex()
        ipk = self.data[sel]
        addon = self.addon
        getipk = Getipk(self.session, ipk, addon)
        getipk.openTest() 

    def keyLeft(self):
        self['text'].left()

    def keyRight(self):
        self['text'].right()

    def keyNumberGlobal(self, number):
        self['text'].number(number)

class Getipk(Screen):
    skin = '\n\t\t<screen position="center,center" size="800,500" title="Open Vision - https://openvision.tech" >\n\t\t\t<!--widget name="text" position="0,0" size="550,25" font="Regular;20" /-->\n\t\t\t<widget name="list" position="10,20" size="750,350" scrollbarMode="showOnDemand" />\n\t\t\t<!--widget name="pixmap" position="200,0" size="190,250" /-->\n\t\t\t<eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />\n\t\t\t<widget name="info" position="50,50" zPosition="4" size="500,400" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="left" valign="top" />\n\t\t        <ePixmap name="red"    position="0,450"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />\n\t                <ePixmap name="green"  position="140,450" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />\n\t                <!--ePixmap name="yellow" position="280,450" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" /> \n\t                <ePixmap name="blue"   position="420,450" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /--> \n\n\t                <widget name="key_red" position="0,450" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> \n\t                <widget name="key_green" position="140,450" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> \n\t                <widget name="key_yellow" position="280,450" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />\n\t                <!--widget name="key_blue" position="420,450" size="140,50" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /-->\n                </screen>'

    def __init__(self, session, ipk, addon):
        Screen.__init__(self, session)
        self.skin = Getipk.skin
        title = 'Addon Install'
        self.setTitle(title)
        self['list'] = MenuList([])
        self['info'] = Label()
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('View Log'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'TimerEditActions'], {'red': self.close,
         'green': self.viewLog,
         'cancel': self.cancel,
         'ok': self.close}, -2)
        self.icount = 0
        self.ipk = ipk
        self.addon = addon
        self.depends = []
        self.idx = 0
        n1 = self.ipk.find ("_", 0)
        self.ipk = self.ipk[:n1]
        self.depends.append(self.ipk)
        self.found = 0
        self.onLayoutFinish.append(self.openTest)
        txt = 'You Have Selected\n\n' + ipk + '\n\nPlease Press Download\n\nAfter Download You Can Choose Install\n\nYou Can Download Again Or Reinstall Something'
        self['info'].setText(txt)
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        ldeps = len(self.depends)
        if ldeps == 0:
                self.viewLog()
        else:
                name1 = self.depends[0]
                missing = name1 + "_"
                slist = 'cams eglibc firmware fonts gstreamer lib mips32el perl plugins python qt4 skins ' + str(getBoxType())
		source = slist.split()
                self.found = 0
		i = 0
		while i<12: 
				   addn = source[i]
				   ftxt = '/tmp/.' + addn + '.txt'
				   if not fileExists(ftxt):
						cmd1 = "wget -O /tmp/." + addn + ".txt 'https://openvision.tech/pedm/mipsel/" + addn + "/index.html'"
						os.system(cmd1)
				   f1 = file(ftxt)
				   flist1 = f1.read()
				   if missing in flist1:
						self.addon = addn
						n4 = flist1.find(missing, 0)
						n5 = flist1.find(".ipk", n4)
						self.ipk = flist1[n4:(n5+4)]        
                                                self.found = 1
						break
				   else:
						i = i+1
                if self.found == 0:
                       txt = name1 + "\nNot Found On The Server !"
                       self.session.open(MessageBox, txt, type=1)
                       self.close
                else:
                       xurl1 = 'https://openvision.tech/pedm/mipsel/' + self.addon + '/'
                       xurl2 = xurl1 + self.ipk
                       self.idx = self.idx + 1
                       cmd2 = 'opkg install --force-reinstall --force-overwrite ' + xurl2 + ' > /tmp/.log' + str(self.idx) + '.txt'
                       title = _("Installing addons %s" %(self.ipk))
                       self.session.openWithCallback(self.newdeps, Console,_(title),[cmd2])

    def newdeps(self):
        dfile = '/tmp/.log' + str(self.idx) + '.txt'
        myfile = file(dfile)
        flog = myfile.read()
        if "Collected errors" not in flog:
            if len(self.depends) > 0:
                   self.depends.pop(0)     
            self.openTest()
        else:
		   n1 = flog.find("Cannot satisfy", 0)
		   n2 = flog.find(":", n1)
		   n3 = flog.find("opkg_install", (n2+1))
		   deps = flog[(n2+1):n3]
		   deps = deps.replace("*", "")
		   ipks = deps.split()
		   ik = len(ipks)
		   i2 = 0
		   while i2 < ik:
		          self.depends.insert(0,ipks[i2])
		          i2 = i2+1
                   self.openTest()

    def viewLog(self):
         cmd = 'rm -rf /tmp/.installed'
         os.system(cmd)
         cmd1 = 'cat /tmp/.log*.txt | grep Configuring | cut -d " " -f2- | cut -d. -f1 > /tmp/.installed'
         os.system(cmd1)
         cmd2 = 'rm -rf /tmp/*.ipk /tmp/.*.txt'
         os.system(cmd2)
         txt = " "
         dfile = '/tmp/.installed'
         myfile = file(dfile)
         txt = myfile.read() + '\nInstalled !'
         self.session.open(MessageBox, txt, type=1)

    def cancel(self):
        self.close()

    def keyLeft(self):
        self['text'].left()

    def keyRight(self):
        self['text'].right()

    def keyNumberGlobal(self, number):
        self['text'].number(number)

def OVLock():
    try:
        from ov import gettitle
        ovtitle = gettitle()
        return ovtitle
    except:
        return False

def main(session, **kwargs):
    if OVLock() == False:
        return
    else:
        session.open(Downloads)

def Plugins(**kwargs):
    return PluginDescriptor(name=_('Download Manager 5.0'), description=_('Special version for Open Vision'), where=[PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU], icon='DownloadManager.png', fnc=main)
