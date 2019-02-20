from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from Screens.Console import Console
from Components.Label import Label
from Components.MenuList import MenuList
from Plugins.Plugin import PluginDescriptor
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ
import os
import gettext

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("PackageManager", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/PackageManager/locale/"))

def _(txt):
	t = gettext.dgettext("PackageManager", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t
	
class PackageManagerScreen(Screen):
	skin = """
	<screen name="ipktoolsscreen" position="center,160" size="750,400" title="Package Manager for Open Vision">
	<ePixmap position="20,385" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/red.png" transparent="1" alphatest="on" />
	<ePixmap position="190,385" zPosition="1" size="230,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/green.png" transparent="1" alphatest="on" />
	<ePixmap position="420,385" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/yellow.png" transparent="1" alphatest="on" />	
	<widget source = "key_red" render="Label" position="20,358" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget source = "key_green" render="Label" position="190,358" zPosition="2" size="230,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget source = "key_yellow" render="Label" position="420,358" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget source="menu" render="Listbox" position="15,10" size="710,330" >
	<convert type="TemplatedMultiContent">
	{"template": [
		MultiContentEntryText(pos = (120, 2), size = (580, 28), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
		MultiContentEntryText(pos = (120, 32), size = (580, 18), font=1, flags = RT_HALIGN_LEFT, text = 2), # index 3 is the Description
		MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (100, 100), png = 3), # index 4 is the pixmap
			],
	"fonts": [gFont("Regular", 23),gFont("Regular", 16)],
	"itemHeight": 110
	}
			</convert>
		</widget>
	</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions", "EPGSelectActions"],

		{
			"ok": self.OK,
			"cancel": self.exit,
			"back": self.exit,
			"red": self.exit,
			"green": self.restartGUI,
			"yellow": self.reboot,
		})
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Restart enigma"))
		self["key_yellow"] = StaticText(_("Restart"))
		self.list = []
		self["menu"] = List(self.list)
		self.mList()

	def mList(self):
		self.list = []
		onepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/PackageManager/images/tar.png"))
		twopng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/PackageManager/images/ipk1.png"))
		treepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/PackageManager/images/ipk.png"))
		fivepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/PackageManager/images/clear.png"))
		sevenpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/PackageManager/images/zip.png"))
		eightpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/PackageManager/images/rar.png"))
		self.list.append((_("ipk Installer"),"two", _("Install ipk Files From /tmp /media/usb /media/hdd /media/cf"), twopng ))
		self.list.append((_("Advanced ipk Installer"),"tree", _("--force-reinstall --force-overwrite"), twopng ))
		self.list.append((_("Online Installer"),"six", _("Install Packages From feeds (Requires Internet)"), twopng ))
		self.list.append((_("ipk Remover"),"four", _("Remove Installed ipk Packages"), treepng ))
		self.list.append((_("tar.gz , bh.tgz , nab.tgz Installer"),"one", _("Install Above Formats From /tmp /media/usb /media/hdd /media/cf"), onepng ))		
		self.list.append((_("zip Installer"),"seven", _("Install zip Files From /tmp /media/usb /media/hdd /media/cf"), sevenpng))	
		self.list.append((_("rar Installer"),"eight", _("Install rar Files From /tmp /media/usb /media/hdd /media/cf"), eightpng))
		self.list.append((_("TMP USB HDD Cleaner"),"five", _("Remove ipk , tar.gz , bh.tgz , nab.tgz , zip , rar Files"), fivepng))
		self["menu"].setList(self.list)
		
	def infoKey (self):
		self.session.openWithCallback(self.mList,info)
		
	def exit(self):
		self.close()
		
	def restartGUI(self):
		os.system("killall -9 enigma2")
		
	def reboot(self):
		os.system("reboot")		
	
	def OK(self):
		item = self["menu"].getCurrent()[1]
		if item is "one":
			self.session.openWithCallback(self.mList,InstallTarGZ)
		elif item is "two":
			self.session.openWithCallback(self.mList,InstallIpk)
		elif item is "tree":
			self.session.openWithCallback(self.mList,AdvInstallIpk)
		elif item is "seven":
			self.session.openWithCallback(self.mList,InstallZip)
		elif item is "eight":
			self.session.openWithCallback(self.mList,InstallRar)			
		elif item is "four":
			self.session.openWithCallback(self.mList,RemoveIPK)
		elif item is "five":
			os.system("rm -rf /tmp/*.ipk /tmp/*.gz /tmp/*.tgz /tmp/*.zip /tmp/*.rar /media/usb/*.ipk /media/usb/*.gz /media/usb/*.tgz /media/usb/*.zip /media/usb/*.rar /media/hdd/*.ipk /media/hdd/*.gz /media/hdd/*.tgz /media/hdd/*.zip /media/hdd/*.rar /media/cf/*.ipk /media/cf/*.gz /media/cf/*.tgz /media/cf/*.zip /media/cf/*.rar")
			self.mbox = self.session.open(MessageBox,_("All ipk , tar.gz , bh.tgz , nab.tgz , zip , rar Files Removed From /tmp /media/usb /media/hdd /media/cf"), MessageBox.TYPE_INFO, timeout = 3 )
		elif item is "six":
			self.session.openWithCallback(self.mList,downfeed)

class InstallTarGZ(Screen):
	skin = """
<screen name="install tar.gz" position="center,160" size="750,370" title="Select tar.gz , bh.tgz , nab.tgz Files">
<widget source="menu" render="Listbox" position="15,10" size="720,300" scrollbarMode="showOnDemand">
	<convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryText(pos = (70, 2), size = (630, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
			MultiContentEntryText(pos = (80, 29), size = (630, 18), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
			MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (50, 50), png = 2), # index 4 is the pixmap
				],
	"fonts": [gFont("Regular", 23),gFont("Regular", 16)],
	"itemHeight": 60
	}
	</convert>
	</widget>
	<ePixmap position="20,358" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/red.png" transparent="1" alphatest="on" />
	<ePixmap position="190,358" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/green.png" transparent="1" alphatest="on" />
	<widget source="key_red" render="Label" position="20,328" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget source="key_green" render="Label" position="190,328" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<ePixmap position="360,358" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/yellow.png" transparent="1" alphatest="on" />
	<widget source="key_yellow" render="Label" position="360,328" zPosition="2" size="200,30" valign="center" halign="center" font="Regular;22" transparent="1" />
</screen>"""
	  
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.session = session
		self.list = []
		self["menu"] = List(self.list)
		self.nList()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.okInst,
				"green": self.okInst,
				"red": self.cancel,
				"yellow": self.okInstAll,
			},-1)
		self.list = [ ]
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Install"))
		self["key_yellow"] = StaticText(_("Install All"))
		
	def nList(self):
		self.list = []
		ipklist = os.popen("ls -lh  /tmp/*.tar.gz /tmp/*.bh.tgz /tmp/*.nab.tgz /media/usb/*.tar.gz /media/usb/*.bh.tgz /media/usb/*.nab.tgz /media/hdd/*.tar.gz /media/hdd/*.bh.tgz /media/hdd/*.nab.tgz /media/cf/*.tar.gz /media/cf/*.bh.tgz /media/cf/*.nab.tgz")
		ipkminipng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/PackageManager/images/tarmini.png"))
		for line in ipklist.readlines():
			dstring = line.split("/")
			try:
				if dstring[1] == "tmp":
					endstr = len(dstring[0] + dstring[1]) + 2
				else:
					endstr = len(dstring[0] + dstring[1] + dstring[2]) + 3
				self.list.append((line[endstr:], dstring[0], ipkminipng))
			except:
				pass
		self["menu"].setList(self.list)
		
	def okInst(self):
		try:
			item = self["menu"].getCurrent()
			name = item[0]
			pecommand1 = ("tar -C/ -xzpvf /tmp/%s" % name)
			pecommand2 = ("tar -C/ -xzpvf /media/usb/%s" % name)
			pecommand3 = ("tar -C/ -xzpvf /media/hdd/%s" % name)
			pecommand4 = ("tar -C/ -xzpvf /media/cf/%s" % name)
			self.session.open(Console,title = _("Install tar.gz , bh.tgz , nab.tgz"), cmdlist = [pecommand1, pecommand2, pecommand3, pecommand4])
		except:
			pass
			
	def okInstAll(self):
			ipklist = os.popen("ls -1  /tmp/*.tar.gz /tmp/*.bh.tgz /tmp/*.nab.tgz /media/usb/*.tar.gz /media/usb/*.bh.tgz /media/usb/*.nab.tgz /media/hdd/*.tar.gz /media/hdd/*.bh.tgz /media/hdd/*.nab.tgz /media/cf/*.tar.gz /media/cf/*.bh.tgz /media/cf/*.nab.tgz")
			self.session.open(Console,title = _("Install tar.gz , bh.tgz , nab.tgz"), cmdlist = ["tar -C/ -xzpvf /tmp/*.tar.gz", "tar -C/ -xzpvf /tmp/*.bh.tgz", "tar -C/ -xzpvf /tmp/*.nab.tgz", "tar -C/ -xzpvf /media/usb/*.tar.gz", "tar -C/ -xzpvf /media/usb/*.bh.tgz", "tar -C/ -xzpvf /media/usb/*.nab.tgz", "tar -C/ -xzpvf /media/hdd/*.tar.gz", "tar -C/ -xzpvf /media/hdd/*.bh.tgz", "tar -C/ -xzpvf /media/hdd/*.nab.tgz", "tar -C/ -xzpvf /media/cf/*.tar.gz", "tar -C/ -xzpvf /media/cf/*.bh.tgz", "tar -C/ -xzpvf /media/cf/*.nab.tgz"])

	def cancel(self):
		self.close()

class InstallIpk(Screen):
	skin = """
<screen name="install ipk" position="center,160" size="750,370" title="Select ipk Files">
<widget source="menu" render="Listbox" position="15,10" size="720,300" scrollbarMode="showOnDemand">
	<convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryText(pos = (70, 2), size = (630, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
			MultiContentEntryText(pos = (80, 29), size = (630, 18), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
			MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (50, 50), png = 2), # index 4 is the pixmap
				],
	"fonts": [gFont("Regular", 23),gFont("Regular", 16)],
	"itemHeight": 60
	}
	</convert>
	</widget>
	<ePixmap position="20,358" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/red.png" transparent="1" alphatest="on" />
	<ePixmap position="190,358" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/green.png" transparent="1" alphatest="on" />
	<widget source="key_red"  render="Label" position="20,328" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget source="key_green"  render="Label" position="190,328" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<ePixmap position="360,358" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/yellow.png" transparent="1" alphatest="on" />
	<widget source="key_yellow"  render="Label" position="360,328" zPosition="2" size="200,30" valign="center" halign="center" font="Regular;22" transparent="1" />
</screen>"""
	  
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.session = session
		self.list = []
		self["menu"] = List(self.list)
		self.nList()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.okInst,
				"green": self.okInst,
				"red": self.cancel,
				"yellow": self.okInstAll,
			},-1)
		self.list = [ ]
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Install"))
		self["key_yellow"] = StaticText(_("Install All"))
		
	def nList(self):
		self.list = []
		ipklist = os.popen("ls -lh  /tmp/*.ipk /media/usb/*.ipk /media/hdd/*.ipk /media/cf/*.ipk")
		ipkminipng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/PackageManager/images/ipkmini.png"))
		for line in ipklist.readlines():
			dstring = line.split("/")
			try:
				if dstring[1] == "tmp":
					endstr = len(dstring[0] + dstring[1]) + 2
				else:
					endstr = len(dstring[0] + dstring[1] + dstring[2]) + 3
				self.list.append((line[endstr:], dstring[0], ipkminipng))
			except:
				pass
		self["menu"].setList(self.list)
		
	def okInst(self):
		try:
			item = self["menu"].getCurrent()
			name = item[0]
			pecommand1 = ("opkg install /tmp/%s" % name)
			pecommand2 = ("opkg install /media/usb/%s" % name)
			pecommand3 = ("opkg install /media/hdd/%s" % name)
			pecommand4 = ("opkg install /media/cf/%s" % name)
			self.session.open(Console,title = "Install ipk Packages", cmdlist = [pecommand1, pecommand2, pecommand3, pecommand4])
		except:
			pass
			
	def okInstAll(self):
		name = "*.ipk"
		pecommand1 = ("opkg install /tmp/%s" % name)
		pecommand2 = ("opkg install /media/usb/%s" % name)
		pecommand3 = ("opkg install /media/hdd/%s" % name)
		pecommand4 = ("opkg install /media/cf/%s" % name)
		self.session.open(Console,title = "Install ipk Packages", cmdlist = [pecommand1, pecommand2, pecommand3, pecommand4])
		
	def cancel(self):
		self.close()

class InstallZip(Screen):
	skin = """
<screen name="install zip" position="center,160" size="750,370" title="Select zip Files">
<widget source="menu" render="Listbox" position="15,10" size="720,300" scrollbarMode="showOnDemand">
	<convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryText(pos = (70, 2), size = (630, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
			MultiContentEntryText(pos = (80, 29), size = (630, 18), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
			MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (50, 50), png = 2), # index 4 is the pixmap
				],
	"fonts": [gFont("Regular", 23),gFont("Regular", 16)],
	"itemHeight": 60
	}
	</convert>
	</widget>
	<ePixmap position="20,358" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/red.png" transparent="1" alphatest="on" />
	<ePixmap position="190,358" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/green.png" transparent="1" alphatest="on" />
	<widget source="key_red" render="Label" position="20,328" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget source="key_green" render="Label" position="190,328" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<ePixmap position="360,358" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/yellow.png" transparent="1" alphatest="on" />
	<widget source="key_yellow" render="Label" position="360,328" zPosition="2" size="200,30" valign="center" halign="center" font="Regular;22" transparent="1" />
</screen>"""
	  
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.session = session
		self.list = []
		self["menu"] = List(self.list)
		self.nList()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.okInst,
				"green": self.okInst,
				"red": self.cancel,
				"yellow": self.okInstAll,
			},-1)
		self.list = [ ]
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Install"))
		self["key_yellow"] = StaticText(_("Install All"))
		
	def nList(self):
		self.list = []
		ipklist = os.popen("ls -lh  /tmp/*.zip /media/usb/*.zip /media/hdd/*.zip /media/cf/*.zip")
		ipkminipng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/PackageManager/images/zipmini.png"))
		for line in ipklist.readlines():
			dstring = line.split("/")
			try:
				if dstring[1] == "tmp":
					endstr = len(dstring[0] + dstring[1]) + 2
				else:
					endstr = len(dstring[0] + dstring[1] + dstring[2]) + 3
				self.list.append((line[endstr:], dstring[0], ipkminipng))
			except:
				pass
		self["menu"].setList(self.list)
		
	def okInst(self):
		try:
			item = self["menu"].getCurrent()
			name = item[0]
			pecommand1 = ("unzip -o -d / /tmp/%s" % name)
			pecommand2 = ("unzip -o -d / /media/usb/%s" % name)
			pecommand3 = ("unzip -o -d / /media/hdd/%s" % name)
			pecommand4 = ("unzip -o -d / /media/cf/%s" % name)
			self.session.open(Console,title = _("Install zip"), cmdlist = [pecommand1, pecommand2, pecommand3, pecommand4])
		except:
			pass
			
	def okInstAll(self):
			ipklist = os.popen("ls -1  /tmp/*.zip /media/usb/*.zip /media/hdd/*.zip /media/cf/*.zip")
			self.session.open(Console,title = _("Install zip"), cmdlist = ["unzip -o -d / /tmp/*.zip", "unzip -o -d / /media/usb/*.zip", "unzip -o -d / /media/hdd/*.zip", "unzip -o -d / /media/cf/*.zip"])

	def cancel(self):
		self.close()

class AdvInstallIpk(Screen):
	skin = """
<screen name="Advanced install ipk" position="center,160" size="750,370" title="Select ipk Files">
<widget source="menu" render="Listbox" position="15,10" size="720,300" scrollbarMode="showOnDemand">
	<convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryText(pos = (70, 2), size = (630, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
			MultiContentEntryText(pos = (80, 29), size = (630, 18), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
			MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (50, 50), png = 2), # index 4 is the pixmap
				],
	"fonts": [gFont("Regular", 23),gFont("Regular", 16)],
	"itemHeight": 60
	}
	</convert>
	</widget>
	<ePixmap position="20,358" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/red.png" transparent="1" alphatest="on" />
	<ePixmap position="190,358" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/green.png" transparent="1" alphatest="on" />
	<widget source ="key_red"  render="Label" position="20,328" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget source="key_green"  render="Label" position="190,328" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<ePixmap position="360,358" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/yellow.png" transparent="1" alphatest="on" />
	<widget source ="key_yellow"  render="Label" position="360,328" zPosition="2" size="200,30" valign="center" halign="center" font="Regular;22" transparent="1" />
</screen>"""
	  
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.session = session
		self.list = []
		self["menu"] = List(self.list)
		self.nList()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.okInst,
				"green": self.okInst,
				"red": self.cancel,
				"yellow": self.okInstAll,
			},-1)
		self.list = [ ]
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Install"))
		self["key_yellow"] = StaticText(_("Install All"))
		
	def nList(self):
		self.list = []
		ipklist = os.popen("ls -lh  /tmp/*.ipk /media/usb/*.ipk /media/hdd/*.ipk /media/cf/*.ipk")
		ipkminipng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/PackageManager/images/ipkmini.png"))
		for line in ipklist.readlines():
			dstring = line.split("/")
			try:
				if dstring[1] == "tmp":
					endstr = len(dstring[0] + dstring[1]) + 2
				else:
					endstr = len(dstring[0] + dstring[1] + dstring[2]) + 3
				self.list.append((line[endstr:], dstring[0], ipkminipng))
			except:
				pass
		self["menu"].setList(self.list)
		
	def okInst(self):
		try:
			item = self["menu"].getCurrent()
			name = item[0]
			pecommand1 = ("opkg install --force-reinstall --force-overwrite /tmp/%s" % name)
			pecommand2 = ("opkg install --force-reinstall --force-overwrite /media/usb/%s" % name)
			pecommand3 = ("opkg install --force-reinstall --force-overwrite /media/hdd/%s" % name)
			pecommand4 = ("opkg install --force-reinstall --force-overwrite /media/cf/%s" % name)
			self.session.open(Console,title = "Install ipk Packages", cmdlist = [pecommand1, pecommand2, pecommand3, pecommand4])			
		except:
			pass
		
	def okInstAll(self):
		name = "*.ipk"
		pecommand1 = ("opkg install --force-reinstall --force-overwrite /tmp/%s" % name)
		pecommand2 = ("opkg install --force-reinstall --force-overwrite /media/usb/%s" % name)
		pecommand3 = ("opkg install --force-reinstall --force-overwrite /media/hdd/%s" % name)
		pecommand4 = ("opkg install --force-reinstall --force-overwrite /media/cf/%s" % name)
		self.session.open(Console,title = _("Install ipk Packages"), cmdlist = [pecommand1, pecommand2, pecommand3, pecommand4])
		
	def cancel(self):
		self.close()

class InstallRar(Screen):
	skin = """
<screen name="install rar" position="center,160" size="750,370" title="Select rar Files">
<widget source="menu" render="Listbox" position="15,10" size="720,300" scrollbarMode="showOnDemand">
	<convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryText(pos = (70, 2), size = (630, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
			MultiContentEntryText(pos = (80, 29), size = (630, 18), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
			MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (50, 50), png = 2), # index 4 is the pixmap
				],
	"fonts": [gFont("Regular", 23),gFont("Regular", 16)],
	"itemHeight": 60
	}
	</convert>
	</widget>
	<ePixmap position="20,358" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/red.png" transparent="1" alphatest="on" />
	<ePixmap position="190,358" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/green.png" transparent="1" alphatest="on" />
	<widget source="key_red" render="Label" position="20,328" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget source="key_green" render="Label" position="190,328" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<ePixmap position="360,358" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/yellow.png" transparent="1" alphatest="on" />
	<widget source="key_yellow" render="Label" position="360,328" zPosition="2" size="200,30" valign="center" halign="center" font="Regular;22" transparent="1" />
</screen>"""
	  
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.session = session
		self.list = []
		self["menu"] = List(self.list)
		self.nList()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.okInst,
				"green": self.okInst,
				"red": self.cancel,
				"yellow": self.okInstAll,
			},-1)
		self.list = [ ]
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Install"))
		self["key_yellow"] = StaticText(_("Install All"))
		
	def nList(self):
		self.list = []
		ipklist = os.popen("ls -lh  /tmp/*.rar /media/usb/*.rar /media/hdd/*.rar /media/cf/*.rar")
		ipkminipng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/PackageManager/images/rarmini.png"))
		for line in ipklist.readlines():
			dstring = line.split("/")
			try:
				if dstring[1] == "tmp":
					endstr = len(dstring[0] + dstring[1]) + 2
				else:
					endstr = len(dstring[0] + dstring[1] + dstring[2]) + 3
				self.list.append((line[endstr:], dstring[0], ipkminipng))
			except:
				pass
		self["menu"].setList(self.list)
		
	def okInst(self):
		try:
			item = self["menu"].getCurrent()
			name = item[0]
			pecommand1 = ("unrar x -u /tmp/%s /" % name)
			pecommand2 = ("unrar x -u /media/usb/%s /" % name)
			pecommand3 = ("unrar x -u /media/hdd/%s /" % name)
			pecommand4 = ("unrar x -u /media/cf/%s /" % name)
			self.session.open(Console,title = _("Install rar"), cmdlist = [pecommand1, pecommand2, pecommand3, pecommand4])
		except:
			pass
			
	def okInstAll(self):
			ipklist = os.popen("ls -1  /tmp/*.rar /media/usb/*.rar /media/hdd/*.rar /media/cf/*.rar")
			self.session.open(Console,title = _("Install rar"), cmdlist = ["unrar x -u /tmp/*.rar /", "unrar x -u /media/usb/*.rar /", "unrar x -u /media/hdd/*.rar /", "unrar x -u /media/cf/*.rar /"])

	def cancel(self):
		self.close()		

class RemoveIPK(Screen):
	skin = """
<screen name="RemoveIpk" position="center,100" size="750,570" title="ipk Remover">
<widget source="menu" position="15,10" render="Listbox" size="720,500">
	<convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryText(pos = (70, 2), size = (630, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
			MultiContentEntryText(pos = (80, 29), size = (630, 18), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
			MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (50, 50), png = 2), # index 4 is the pixmap
				],
	"fonts": [gFont("Regular", 23),gFont("Regular", 16)],
	"itemHeight": 60
	}
	</convert>
	</widget>
	<ePixmap position="20,558" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/red.png" transparent="1" alphatest="on" />
	<ePixmap position="190,558" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/green.png" transparent="1" alphatest="on" />
	<ePixmap position="360,558" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/yellow.png" transparent="1" alphatest="on" />
	<widget source="key_red" render="Label" position="20,528" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget source="key_green" render="Label" position="190,528" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget source="key_yellow" render="Label" position="360,528" zPosition="2" size="200,30" valign="center" halign="center" font="Regular;22" transparent="1" />
</screen>"""
	  
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.session = session
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("UnInstall"))
		self["key_yellow"] = StaticText(_("Pro UnInstall"))
		self.list = []
		self["menu"] = List(self.list)
		self.nList()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.Remove,
				"green": self.Remove,
				"red": self.cancel,
				"yellow": self.ARemove,
			},-1)
		
	def nList(self):
		self.list = []
		ipklist = os.popen("opkg list-installed")
		ipkminipng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/PackageManager/images/ipkmini.png"))
		for line in ipklist.readlines():
			dstring = line.split(" ")
			try:
				endstr = len(dstring[0]) + 2
				self.list.append((dstring[0], line[endstr:], ipkminipng))
			except:
				pass
		self["menu"].setList(self.list)
		
	def cancel(self):
		self.close()
		
	def Remove(self):
		item = self["menu"].getCurrent()
		name = item[0]
		os.system("opkg remove %s" % item[0])
		self.mbox = self.session.open(MessageBox, _("%s UnInstalled" % item[0]), MessageBox.TYPE_INFO, timeout = 3 )
		self.nList()

	def ARemove(self):
		item = self["menu"].getCurrent()
		os.system("opkg remove --force-depends %s" % item[0])
		self.mbox = self.session.open(MessageBox,_("%s UnInstalled" % item[0]), MessageBox.TYPE_INFO, timeout = 3 )
		self.nList()

class downfeed(Screen):
	skin = """
<screen name="downdown" position="center,100" size="750,570" title="Install Packages From feeds">
<widget source="menu" render="Listbox" position="15,10" size="720,500" scrollbarMode="showOnDemand">
	<convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryText(pos = (70, 2), size = (630, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
			MultiContentEntryText(pos = (80, 29), size = (630, 18), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
			MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (50, 50), png = 2), # index 4 is the pixmap
				],
	"fonts": [gFont("Regular", 23),gFont("Regular", 16)],
	"itemHeight": 60
	}
	</convert>
	</widget>
	<ePixmap position="20,558" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/red.png" transparent="1" alphatest="on" />
	<ePixmap position="190,558" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PackageManager/images/green.png" transparent="1" alphatest="on" />
	<widget source="key_red" render="Label" position="20,528" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget source="key_green" render="Label" position="190,528" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
</screen>"""
	  
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.session = session
		self.list = []
		self["menu"] = List(self.list)
		self.nList()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.setup,
				"green": self.setup,
				"red": self.cancel,
			},-1)
		self.list = [ ]
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Install"))
		
	def nList(self):
		self.list = []
		os.system("opkg update")
		try:
			ipklist = os.popen("opkg list")
		except:
			pass
		png = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/PackageManager/images/ipkmini.png"))
		for line in ipklist.readlines():
			dstring = line.split(" ")
			try:
				endstr = len(dstring[0] + dstring[1]+ dstring[2]+dstring[3]) + 4

				self.list.append((dstring[0]  + " " + dstring[1] + " " + dstring[2], line[endstr:], png))
			except:
				pass
		self["menu"].setList(self.list)
		
	def cancel(self):
		self.close()
		
	def setup(self):
		item = self["menu"].getCurrent()
		name = item[0]
		os.system("opkg install %s" % name)
		msg  = _("%s Installed" % name)
		self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, timeout = 3 )

def PELock():
    try:
        from pe import gettitle
        petitle = gettitle()
        return petitle
    except:
        return False	

def main(session, **kwargs):
	if PELock()==False:
		return
	else:
		session.open(PackageManagerScreen)

def Plugins(**kwargs):
	return PluginDescriptor(
			name = _("Package Manager"),
			description = _("Special version for Open Vision"),
			where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
			icon="PackageManager.png",
			fnc=main)
