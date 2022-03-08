#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from .__init__ import _
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.config import NoSave, ConfigEnableDisable, ConfigText, getConfigListEntry
from enigma import eConsoleAppContainer
import os
from os import path
from Components.Console import Console


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


def getAttribute(filename, section, attribute):
	try:
		inifile = open(filename, 'r')
		flag = False
		for line in inifile:
			if line[0] == '#' or line[0] == ';':
				continue
			if line[0] == '[' and flag:
				flag = False
			if '[' + section + ']' in line:
				flag = True
			if attribute in line and flag:
				value = line.strip().split('=')
				inifile.close()
				return value[1].strip()
	except IOError:
		pass

	return None


def writeAttribute(filename, section, attribute, value):
	try:
		inifile = open(filename, 'r')
		buf = []
		flag = False
		for line in inifile:
			if line[0] == '[' and flag:
				flag = False
			if '[' + section + ']' in line:
				flag = True
			if attribute in line and flag:
				attrib = line.strip().split('=')
				newline = "   " + attrib[0].strip() + ' = ' + value
				buf.append(newline)
				retval = 1
			else:
				buf.append(line.replace('\n', ''))
		inifile.close()

	except IOError:
		pass
		return -1

	if retval:
		inifile = open(filename, 'w')
		for line in buf:
			inifile.write(line + '\n')
		inifile.close()
		return retval
	else:
		return 0


class setupSamba(Screen, ConfigListScreen):
	skin = """
		<screen name="setupSamba" position="center,center" size="560,350" title="setup Samba-Server">
			<widget name="config" position="10,10" size="540,150" scrollbarMode="showOnDemand" />
			<widget name="smbdLabel" position="20,160" size="520,30" font="Regular;21"/>
			<widget name="nmbdLabel" position="20,190" size="520,30" font="Regular;21"/>
			<widget name="ButtonGreentext" position="50,270" size="460,21" halign="left" zPosition="10" font="Regular;21" transparent="1" />
			<widget name="ButtonGreen" pixmap="buttons/button_green.png" position="30,273" zPosition="10" size="15,16" transparent="1" alphatest="on" />
			<widget name="ButtonRedtext" position="50,300" size="460,21" halign="left" zPosition="10" font="Regular;21" transparent="1" />
			<widget name="ButtonRed" pixmap="buttons/button_red.png" position="30,303" zPosition="10" size="15,16" transparent="1" alphatest="on" />
			<ePixmap pixmap="bottombar.png" position="10,250" size="540,120" zPosition="1" transparent="1" alphatest="on" />
		</screen>"""

	def __init__(self, session, iface, plugin_path):
		self.skin = setupSamba.skin
		self.session = session
		Screen.__init__(self, session)

		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)

		if isRunning('smbd') and isRunning('nmbd'):
			isEnabled = True
		else:
			isEnabled = False

		confError = False
		tmp = getAttribute('/etc/samba/smb.conf', 'global', 'server string')
		if tmp != None:
			serverString = tmp
		else:
			serverString = 'READERROR server string'
			confError = True

		tmp = getAttribute('/etc/samba/smb.conf', 'global', 'netbios name')
		if tmp != None:
			netbiosName = tmp
		else:
			netbiosName = 'READERROR netbios name'
			confError = True

		tmp = getAttribute('/etc/samba/smb.conf', 'global', 'workgroup')
		if tmp != None:
			workgroup = tmp
		else:
			workgroup = 'READERROR workgroup'
			confError = True

		self.activeConfigEntry = NoSave(ConfigEnableDisable(default=isEnabled))
		self.serverStringConfigEntry = NoSave(ConfigText(default=serverString, visible_width=50, fixed_size=False))
		self.netbiosNameConfigEntry = NoSave(ConfigText(default=netbiosName, visible_width=50, fixed_size=False))
		self.workgroupConfigEntry = NoSave(ConfigText(default=workgroup, visible_width=50, fixed_size=False))

		self["smbdLabel"] = Label()
		self["nmbdLabel"] = Label()
		self["ButtonGreen"] = Pixmap()
		self["ButtonGreentext"] = Button(_("save and start/restart Samba-Server"))
		self["ButtonRed"] = Pixmap()
		self["ButtonRedtext"] = Label(_("Close"))

		self.startingUp = False
		self.goingDown = False
		self.cmdlist = []
		self.run = 0

		self.createSetup()
		ConfigListScreen.__init__(self, self.list, session=session)
		self.activeConfigEntry.addNotifier(self.toggleServer)

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.cancel,
			"red": self.cancel,
			"green": self.green
		}, -2)

		if confError:
			self.onExecBegin.append(self.errorMbox)

	def errorMbox(self):
		info = self.session.open(MessageBox, _("/etc/smb.conf not found or readerror!"), MessageBox.TYPE_ERROR)
		info.setTitle("setup Samba-Server")
		self.close()

	def createSetup(self):
		self.list = []
		self.list.append(getConfigListEntry(_("Enable/Disable Samba-Server"), self.activeConfigEntry))
		if self.activeConfigEntry.value:
			self.list.append(getConfigListEntry(_("server string"), self.serverStringConfigEntry))
			self.list.append(getConfigListEntry(_("netbios name"), self.netbiosNameConfigEntry))
			self.list.append(getConfigListEntry(_("workgroup"), self.workgroupConfigEntry))
			self["smbdLabel"].show()
			self["nmbdLabel"].show()
			self["ButtonGreentext"].show()
			self["ButtonGreen"].show()
			if self.goingDown or self.startingUp:
				if self.goingDown:
					self["smbdLabel"].setText(_("Status smbd: going down..."))
					self["nmbdLabel"].setText(_("Status nmbd: going down..."))
				if self.startingUp:
					self["smbdLabel"].setText(_("Status smbd: starting up..."))
					self["nmbdLabel"].setText(_("Status nmbd: starting up..."))
			else:
				self.smbdLabelSet()
				self.nmbdLabelSet()
		else:
			self["smbdLabel"].hide()
			self["nmbdLabel"].hide()
			self["ButtonGreentext"].hide()
			self["ButtonGreen"].hide()

	def toggleServer(self, configElement):
		self.createSetup()
		self["config"].l.setList(self.list)
		if not configElement.value:
			if not self.goingDown or not self.startingUp:
				if isRunning('smbd') or isRunning('nmbd'):
					self.sambaDown()
					self.deleteScripts()

	def cancel(self):
		if self.run == len(self.cmdlist):
			self.close()
			self.container.appClosed.remove(self.runFinished)

	def green(self):
		if self.activeConfigEntry.value:
			self.sambaDown()

			confError = 0
			confError += writeAttribute('/etc/samba/smb.conf', 'global', 'server string', self.serverStringConfigEntry.value)
			confError += writeAttribute('/etc/samba/smb.conf', 'global', 'netbios name', self.netbiosNameConfigEntry.value)
			confError += writeAttribute('/etc/samba/smb.conf', 'global', 'workgroup', self.workgroupConfigEntry.value)
			if confError < 3:
				info = self.session.open(MessageBox, _("/etc/smb.conf not found or writeerror!"), MessageBox.TYPE_ERROR)
				info.setTitle("setup Samba-Server")
				self.cancel()
			else:
				self.sambaUp()
				self.createUpScript()
				self.createDownScript()

	def smbdLabelSet(self):
		if isRunning('smbd'):
			self["smbdLabel"].setText(_("Status smbd: started"))
		else:
			self["smbdLabel"].setText(_("Status smbd: stopped"))

	def nmbdLabelSet(self):
		if isRunning('nmbd'):
			self["nmbdLabel"].setText(_("Status nmbd: started"))
		else:
			self["nmbdLabel"].setText(_("Status nmbd: stopped"))

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
			self.smbdLabelSet()
			self.nmbdLabelSet()

	def sambaUp(self):
		self["smbdLabel"].setText(_("Status smbd: starting up..."))
		self["nmbdLabel"].setText(_("Status nmbd: starting up..."))
		self.cmdlist.append("nmbd -D")
		self.cmdlist.append("smbd -D")
		self.startingUp = True
		self.container.execute(self.cmdlist[self.run])

	def sambaDown(self):
		self["smbdLabel"].setText(_("Status smbd: going down..."))
		self["nmbdLabel"].setText(_("Status nmbd: going down..."))
		self.cmdlist.append("killall -9 smbd")
		self.cmdlist.append("killall -9 nmbd")
		self.goingDown = True
		self.container.execute(self.cmdlist[self.run])

	def createUpScript(self):
		scriptfile = open("/etc/network/if-up.d/01samba-start", "w")
		scriptfile.write("#!/bin/sh\n")
		scriptfile.write("nmbd -D\n")
		scriptfile.write("smbd -D\n")
		scriptfile.close()
		Console().ePopen("chmod 755 /etc/network/if-up.d/01samba-start")

	def createDownScript(self):
		scriptfile = open("/etc/network/if-down.d/01samba-kill", "w")
		scriptfile.write("#!/bin/sh\n")
		scriptfile.write("killall -9 smbd\n")
		scriptfile.write("rm -rf /var/log/log.smbd\n")
		scriptfile.write("killall -9 nmbd\n")
		scriptfile.write("rm -rf /var/log/log.nmbd\n")
		scriptfile.close()
		Console().ePopen("chmod 755 /etc/network/if-down.d/01samba-kill")

	def deleteScripts(self):
		Console().ePopen("rm -rf /etc/network/if-up.d/01samba-start")
		Console().ePopen("rm -rf /etc/network/if-down.d/01samba-kill")
