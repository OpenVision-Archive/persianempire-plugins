# -*- coding: utf-8 -*-
from __init__ import _
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.config import NoSave, ConfigEnableDisable, ConfigSelection, ConfigIP, ConfigDirectory, getConfigListEntry
from Components.Sources.List import List
from dirSelect import dirSelectDlg
from enigma import eConsoleAppContainer
import os
from os import path

def isRunning(pname):
	for f in os.listdir('/proc'):
		try:
			cmdline = open(path.join('/', 'proc', f, 'status'), 'r')
			if pname in cmdline.read():
				cmdline.close()
				return True
		except IOError:
			pass
	return False

class editExportEntry(Screen, ConfigListScreen):
	skin = """	
		<screen name="editExportEntry" position="center,center" size="560,350" title="edit Export Entry">
			<widget name="config" position="10,10" size="540,150" scrollbarMode="showOnDemand" />
			<widget name="ButtonGreentext" position="50,270" size="460,21" halign="left" zPosition="10" font="Regular;21" transparent="1" />
			<widget name="ButtonGreen" pixmap="buttons/button_green.png" position="30,273" zPosition="10" size="15,16" transparent="1" alphatest="on" />
			<widget name="ButtonRedtext" position="50,300" size="460,21" halign="left" zPosition="10" font="Regular;21" transparent="1" />
			<widget name="ButtonRed" pixmap="buttons/button_red.png" position="30,303" zPosition="10" size="15,16" transparent="1" alphatest="on" />
			<ePixmap pixmap="bottombar.png" position="10,250" size="540,120" zPosition="1" transparent="1" alphatest="on" />
		</screen>"""

	def __init__(self, session, exportDir, client, options):
		self.skin = editExportEntry.skin		
		self.session = session
		Screen.__init__(self, session)

		nfsoptions = [\
		"ro,sync",
		"rw,sync",
		"ro,async",
		"rw,async",
		"ro,no_root_squash",
		"rw,no_root_squash",
		"ro,no_subtree_check",
		"rw,no_subtree_check",
		"ro,insecure",
		"rw,insecure",
		"ro,insecure,no_subtree_check",
		"rw,insecure,no_subtree_check",
		"ro,sync,no_subtree_check",
		"rw,sync,no_subtree_check",
		"ro,async,no_subtree_check",
		"rw,async,no_subtree_check",
		"ro,no_root_squash,no_subtree_check",
		"rw,no_root_squash,no_subtree_check",
		"ro,no_root_squash,sync",
		"rw,no_root_squash,sync",
		"ro,no_root_squash,sync,no_subtree_check",
		"rw,no_root_squash,sync,no_subtree_check",
		"ro,no_root_squash,async",
		"rw,no_root_squash,async",
		"ro,no_root_squash,async,no_subtree_check",
		"rw,no_root_squash,async,no_subtree_check"]

		optionsEntrys = {}
		for x in nfsoptions:
			optionsEntrys[x] = x

		clientIP = [192, 168, 0, 0]
		self.netmask = ''

		tmp = client.split('/')
		if len(tmp) > 1:
			client = tmp[0]
			self.netmask = tmp[1]

		if client == '*':
			everyIP = True
		else:
			everyIP = False
			theIP = client.split('.')
			clientIP = []
			for x in theIP:
				clientIP.append(int(x))

		self.exportDirConfigEntry = NoSave(ConfigDirectory(exportDir))
		self.everyIPConfigEntry = NoSave(ConfigEnableDisable(default = everyIP))
		self.clientConfigEntry = NoSave(ConfigIP(clientIP))
		self.optionsConfigEntry = NoSave(ConfigSelection(optionsEntrys, options))

		ConfigListScreen.__init__(self, [])
		self.createSetup()
		self.everyIPConfigEntry.addNotifier(self.toggleEveryIP)

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.cancel,
			"red"   : self.cancel,
			"green" : self.green,
			"ok"    : self.ok
		}, -2)

		self["ButtonGreen"] = Pixmap()
		self["ButtonGreentext"] = Label(_("Save and Close"))
		self["ButtonRed"] = Pixmap()
		self["ButtonRedtext"] = Label(_("Close"))

	def createSetup(self):
		self.list = []
		self.list.append(getConfigListEntry(_("export directory"), self.exportDirConfigEntry))
		self.list.append(getConfigListEntry(_("every ip"), self.everyIPConfigEntry))
		if not self.everyIPConfigEntry.value:
			self.list.append(getConfigListEntry(_("client ip"), self.clientConfigEntry))
		self.list.append(getConfigListEntry(_("options"), self.optionsConfigEntry))
		self["config"].setList(self.list)

	def toggleEveryIP(self, configElement):
		self.createSetup()

	def cancel(self):
		self.close(False)

	def ok(self):
		if self["config"].getCurrent()[1] == self.exportDirConfigEntry:
			self.session.openWithCallback(self.dirSelectDlgClosed, dirSelectDlg, self.exportDirConfigEntry.value+'/')

	def dirSelectDlgClosed(self, path):
		if path != False:
			if path.endswith('/'):
				path = path[:-1]
			self.exportDirConfigEntry.setValue(path)

	def green(self):
		data = []
		data.append(self.exportDirConfigEntry.value)
		if self.everyIPConfigEntry.value:
			ipdata = '*'
		else:
			ipdata = "%d.%d.%d.%d" % tuple(self.clientConfigEntry.value)
		if len(self.netmask) > 0:
			ipdata = ipdata + "/" + self.netmask
		data.append(ipdata)
		data.append(self.optionsConfigEntry.value)
		self.close(data)

class setupNfs(Screen, ConfigListScreen):
	skin = """
		<screen name="setupNfs" position="center,center" size="560,350" title="setup NFS-Server">
			<widget name="config" position="10,10" size="540,30" scrollbarMode="showOnDemand" />
			<widget source="exportlist" render="Listbox" position="10,50" size="540,100" scrollbarMode="showOnDemand">
				<convert type="TemplatedMultiContent">
					{"template": [
						MultiContentEntryText(pos = (0, 13), size = (200, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 0 is the exportdir
						MultiContentEntryText(pos = (210, 3), size = (330, 18), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 1 is the client
						MultiContentEntryText(pos = (210, 28), size = (330, 18), font=1, flags = RT_HALIGN_LEFT, text = 2), # index 2 is the options
					],
					"fonts": [gFont("Regular", 20),gFont("Regular", 14)],
					"itemHeight": 50
					}
				</convert>
			</widget>
			<widget name="nfsdLabel" position="20,170" size="520,30" font="Regular;21"/>
			<widget name="portmapLabel" position="20,200" size="520,30" font="Regular;21"/>
			<widget name="ButtonGreentext" position="50,270" size="460,21" halign="left" zPosition="10" font="Regular;20" transparent="1" />
			<widget name="ButtonGreen" pixmap="buttons/button_green.png" position="30,273" zPosition="10" size="15,16" transparent="1" alphatest="on" />
			<widget name="ButtonRedtext" position="50,300" size="145,21" halign="left" zPosition="10" font="Regular;20" transparent="1" />
			<widget name="ButtonRed" pixmap="buttons/button_red.png" position="30,303" zPosition="10" size="15,16" transparent="1" alphatest="on" />
			<widget name="ButtonYellowtext" position="220,300" size="145,21" halign="left" zPosition="10" font="Regular;20" transparent="1" />
			<widget name="ButtonYellow" pixmap="buttons/button_yellow.png" position="200,303" zPosition="10" size="15,16" transparent="1" alphatest="on" />
			<widget name="ButtonBluetext" position="390,300" size="145,21" halign="left" zPosition="10" font="Regular;20" transparent="1" />
			<widget name="ButtonBlue" pixmap="buttons/button_blue.png" position="370,303" zPosition="10" size="15,16" transparent="1" alphatest="on" />
			<ePixmap pixmap="bottombar.png" position="10,250" size="540,120" zPosition="1" transparent="1" alphatest="on" />
		</screen>"""

	def __init__(self, session, iface ,plugin_path):
		self.skin = setupNfs.skin		
		self.session = session
		Screen.__init__(self, session)

		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)

		if isRunning('portmap') and isRunning('nfsd'):
			isEnabled = True
		else:
			isEnabled = False

		self.activeConfigEntry = NoSave(ConfigEnableDisable(default = isEnabled))

		self["nfsdLabel"] = Label()
		self["portmapLabel"] = Label()
		self["ButtonGreen"] = Pixmap()
		self["ButtonGreentext"] = Button(_("save and start/restart NFS-Server"))
		self["ButtonRed"] = Pixmap()
		self["ButtonRedtext"] = Label(_("Close"))
		self["ButtonYellow"] = Pixmap()
		self["ButtonYellowtext"] = Label(_("New Entry"))
		self["ButtonBlue"] = Pixmap()
		self["ButtonBluetext"] = Label(_("Remove Entry"))

		self.startingUp = False
		self.goingDown = False
		self.cmdlist = []
		self.run = 0

		self.exportlist = []
		data = self.readExports()
		if data is not None:
			for line in data:
				exportDir = line[0]
				client = line[1]
				options = line[2]
				options = options.replace('(', '')
				options = options.replace(')', '')
				self.exportlist.append((exportDir, client, options))
		else:
			self.exportlist.append(('/media/hdd', '*', 'rw,no_root_squash,sync'))

		self["exportlist"] = List(self.exportlist)
		self.hideList = self["exportlist"].list

		self.createSetup()
		ConfigListScreen.__init__(self, self.list, session = session)
		self.activeConfigEntry.addNotifier(self.toggleServer)

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel" : self.cancel,
			"ok"     : self.editExportEntry,
			"green"  : self.green,
			"red"	 : self.cancel,
			"yellow" : self.newExportEntry,
			"blue"   : self.deleteExportEntry
		}, -2)

	def readExports(self):
		try:
			exportfile = open('/etc/exports', 'r')
			lines = []
			for line in exportfile:
				if line[0] != '#' and line != '\n':
					tmp = []
					line = line.replace('\t', ' ')
					val = line.strip().split(' ')
					exportdir = val[0].strip()
					tmp.append(exportdir)
					line = line[len(exportdir):].strip()
					val = line.strip().split('(')
					client = val[0].strip()
					tmp.append(client)
					options = line[len(client):].strip()
					tmp.append(options)
					lines.append(tmp)
			return lines
		except IOError:
			pass
			return None
	
	def writeExports(self, data):
		exportfile = open('/etc/exports', 'w')
		for line in data:
			exportfile.write(line[0] + ' ' + line[1] + '(' + line[2] + ')' + '\n')
		exportfile.close()

	def createSetup(self):
		self.list = []
		self.list.append(getConfigListEntry(_("Enable/Disable NFS-Server"), self.activeConfigEntry))
		if self.activeConfigEntry.value:
			self.exportlistShow()
			self["nfsdLabel"].show()
			self["portmapLabel"].show()
			self["ButtonGreentext"].show()
			self["ButtonGreen"].show()
			self["ButtonYellow"].show()
			self["ButtonYellowtext"].show()
			self["ButtonBlue"].show()
			self["ButtonBluetext"].show()
			if self.goingDown or self.startingUp:
				if self.goingDown:
					self["nfsdLabel"].setText(_("Status nfsd: going down..."))
					self["portmapLabel"].setText(_("Status portmap: going down..."))
				if self.startingUp:
					self["nfsdLabel"].setText(_("Status nfsd: starting up..."))
					self["portmapLabel"].setText(_("Status portmap: starting up..."))
			else:
				self.nfsdLabelSet()
				self.portmapLabelSet()
		else:
			self.exportlistHide()
			self["nfsdLabel"].hide()
			self["portmapLabel"].hide()
			self["ButtonGreentext"].hide()
			self["ButtonGreen"].hide()
			self["ButtonYellow"].hide()
			self["ButtonYellowtext"].hide()
			self["ButtonBlue"].hide()
			self["ButtonBluetext"].hide()

	def toggleServer(self, configElement):
		self.createSetup()
		self["config"].l.setList(self.list)
		if not configElement.value:
			if not self.goingDown or not self.startingUp:
				if isRunning('portmap') and isRunning('nfsd'):
					self.nfsServerDown()

	def exportlistShow(self):
		self.exportlist = []
		for line in self.hideList:
			self.exportlist.append((line[0], line[1], line[2]))
		self["exportlist"].setList(self.exportlist)

	def exportlistHide(self):
		if len(self["exportlist"].list) == 0:
			return
		self.hideList = self["exportlist"].list
		self.exportlist = []
		self["exportlist"].setList(self.exportlist)

	def cancel(self):
		if self.run == len(self.cmdlist):
			self.close()
			self.container.appClosed.remove(self.runFinished)

	def editExportEntry(self):
		if self.activeConfigEntry.value:
			sel = self["exportlist"].getCurrent()
			if sel:
				self.tmpList = self["exportlist"].list
				self.session.openWithCallback(self.editExportEntryClosed, editExportEntry, sel[0], sel[1], sel[2])

	def editExportEntryClosed(self, data):
		if data:
			self.tmpList[self["exportlist"].getIndex()] = data
			self.exportlist = []
			for line in self.tmpList:
				self.exportlist.append((line[0], line[1], line[2]))
			self["exportlist"].setList(self.exportlist)

	def newExportEntry(self):
		if self.activeConfigEntry.value:
			self.tmpList = self["exportlist"].list
			self.session.openWithCallback(self.newExportEntryClosed, editExportEntry, '/media/hdd', '*', 'rw,no_root_squash,sync')

	def newExportEntryClosed(self, data):
		if data:
			self.tmpList.append(data)
			self.exportlist = []
			for line in self.tmpList:
				self.exportlist.append((line[0], line[1], line[2]))
			self["exportlist"].setList(self.exportlist)

	def deleteExportEntry(self):
		if self.activeConfigEntry.value:
			if len(self["exportlist"].list) < 2:
				return
			self.tmpList = self["exportlist"].list
			mbox = self.session.openWithCallback(self.deleteExportEntryClosed, MessageBox,_("Really delete this entry?"), MessageBox.TYPE_YESNO)
			mbox.setTitle(_("delete entry"))

	def deleteExportEntryClosed(self, answer):
		if answer is True:
			itemIndex = self["exportlist"].getIndex()
			self.exportlist = []
			for cnt, line in enumerate(self.tmpList):
				if cnt != itemIndex:
					self.exportlist.append((line[0], line[1], line[2]))
			self["exportlist"].setList(self.exportlist)			

	def green(self):
		if self.activeConfigEntry.value:
			self.nfsServerDown()
			self.writeExports(self["exportlist"].list)
			self.nfsServerUp()

	def nfsdLabelSet(self):
		if isRunning('nfsd'):
			self["nfsdLabel"].setText(_("Status nfsd: started"))
		else:
			self["nfsdLabel"].setText(_("Status nfsd: stopped"))

	def portmapLabelSet(self):
		if isRunning('portmap'):
			self["portmapLabel"].setText(_("Status portmap: started"))
		else:
			self["portmapLabel"].setText(_("Status portmap: stopped"))

	def dataAvail(self, str):
		print(str,)

	def runFinished(self, retval):
		self.run += 1
		if self.run != len(self.cmdlist):
			self.container.execute(self.cmdlist[self.run])
		else:
			self.run = 0
			self.cmdlist = []
			self.startingUp = False
			self.goingDown = False
			self.nfsdLabelSet()
			self.portmapLabelSet()

	def nfsServerUp(self):
		self["nfsdLabel"].setText(_("Status nfsd: starting up..."))
		self["portmapLabel"].setText(_("Status portmap: starting up..."))
		self.cmdlist.append("update-rc.d -s portmap start 43 S . start 32 0 6 . stop 81 1 .")
		self.cmdlist.append("/etc/init.d/portmap start")
		self.cmdlist.append("update-rc.d -s nfsserver defaults")
		self.startingUp = True
		self.container.execute(self.cmdlist[self.run])

	def nfsServerDown(self):
		self["nfsdLabel"].setText(_("Status nfsd: going down..."))
		self["portmapLabel"].setText(_("Status portmap: going down..."))
		self.cmdlist.append("/etc/init.d/portmap stop")
		self.cmdlist.append("/etc/init.d/nfsserver stop")
		self.cmdlist.append("update-rc.d -f portmap remove")
		self.cmdlist.append("update-rc.d -f nfsserver remove")
		self.cmdlist.append("killall portmap mountd")
		self.goingDown = True
		self.container.execute(self.cmdlist[self.run])
