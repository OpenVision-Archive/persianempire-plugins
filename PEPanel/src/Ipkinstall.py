from Components.MenuList import MenuList
from Components.Label import Label
from Screens.Screen import Screen
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap
import os
import gettext

def _(txt):
    t = gettext.dgettext('PEPanel', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


class Ipkinstall(Screen):
    skin = '\n\t\t<screen position="center,center" size="550,400" title=" " >\n\t\t\t<!--widget name="text" position="0,0" size="550,25" font="Regular;20" /-->\n\t\t\t<widget name="list" position="10,0" size="500,350" scrollbarMode="showOnDemand" />\n\t\t\t<!--widget name="pixmap" position="200,0" size="190,250" /-->\n\t\t\t<eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />\n\t\t\t<widget name="info" position="100,230" zPosition="4" size="300,25" font="Regular;18" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t\t</screen>'

    def __init__(self, session):
        self.skin = Ipkinstall.skin
        Screen.__init__(self, session)
        self['list'] = MenuList([])
        self['info'] = Label()
        self['actions'] = ActionMap(['OkCancelActions'], {'ok': self.okClicked,
         'cancel': self.close}, -1)
        self.icount = 0
        title = _('Available for install')
        self.setTitle(title)
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        self.ipks = []
        path = '/tmp/'
        for root, dirs, files in os.walk(path):
            for name in files:
                if name[-4:] == '.ipk':
                    self.icount = self.icount + 1
                    fname = '/tmp/' + name
                    self.ipks.append(fname)
        path2 = '/media/usb/'
        for root, dirs, files in os.walk(path2):
            for name in files:
                if name[-4:] == '.ipk':
                    self.icount = self.icount + 1
                    fname = '/tmp/' + name
                    self.ipks.append(fname)
        path3 = '/media/hdd/'
        for root, dirs, files in os.walk(path3):
            for name in files:
                if name[-4:] == '.ipk':
                    self.icount = self.icount + 1
                    fname = '/tmp/' + name
                    self.ipks.append(fname)
        self['list'].setList(self.ipks)

    def okClicked(self):
        if self.icount > 0:
            sel = self['list'].getSelectionIndex()
            ipk = self.ipks[sel]
            self.session.open(Getipk, ipk)
            self.close()

    def keyLeft(self):
        self['text'].left()

    def keyRight(self):
        self['text'].right()

    def keyNumberGlobal(self, number):
        self['text'].number(number)


class Getipk(Screen):
    skin = '\n\t\t<screen position="80,70" size="600,470" title="Install status" >\n\t\t\t<!--widget name="text" position="0,0" size="550,25" font="Regular;20" /-->\n\t\t\t<widget name="list" position="10,0" size="590,400" scrollbarMode="showOnDemand" />\n\t\t\t<!--widget name="pixmap" position="200,0" size="190,250" /-->\n\t\t\t<eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />\n\t\t\t<widget name="info" position="100,420" zPosition="4" size="300,25" font="Regular;18" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n\t\t</screen>'

    def __init__(self, session, ipk):
        self.skin = Getipk.skin
        Screen.__init__(self, session)
        self['list'] = MenuList([])
        self['info'] = Label()
        self['actions'] = ActionMap(['OkCancelActions'], {'ok': self.okClicked,
         'cancel': self.close}, -1)
        self.icount = 0
        self.ipk = ipk
        self['info'].setText('Installing ipkg......')
        title = _('Install status')
        self.setTitle(title)
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        cmd = 'opkg install --force-reinstall --force-overwrite ' + self.ipk + ' > /tmp/ipk.log'
        os.system(cmd)
        self.viewLog()

    def keyLeft(self):
        self['text'].left()

    def keyRight(self):
        self['text'].right()

    def keyNumberGlobal(self, number):
        self['text'].number(number)

    def viewLog(self):
        self['info'].setText('Press OK to continue...')
        myfile = file('/tmp/ipk.log')
        icount = 0
        data = []
        ebuf = []
        for line in myfile.readlines():
			data.append(icount)
			num = len(line)
			if num < 55:
				data[icount] = line[:-1]
				ebuf.append(data[icount])
			else:
				dataFull = line
				data1 = dataFull[:55]
				data[icount] = data1
				ebuf.append(data[icount])
				data2 = '               ' + dataFull[55:]
				data[icount] = data2
				ebuf.append(data[icount])
			icount = icount + 1
			self['list'].setList(data)
			self.endinstall()

    def endinstall(self):
        ipkname = self.ipk
        if ipkname != 0:
            cmd = 'rm -rf /tmp/' + ipkname
            os.system(cmd)

    def okClicked(self):
        self.close()