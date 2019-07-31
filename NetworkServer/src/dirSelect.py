# -*- coding: utf-8 -*-
from __init__ import _
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.Button import Button
from Components.FileList import FileList

class dirSelectDlg(Screen):
	skin = """
		<screen name="dirSelectDlg" position="center,center" size="560,350">
			<widget name="filelist" position="10,10" size="540,210" scrollbarMode="showOnDemand" />
			<widget name="ButtonGreentext" position="50,270" size="460,21" halign="left" zPosition="10" font="Regular;21" transparent="1" />
			<widget name="ButtonGreen" pixmap="buttons/button_green.png" position="30,273" zPosition="10" size="15,16" transparent="1" alphatest="on" />
			<widget name="ButtonRedtext" position="50,300" size="460,21" halign="left" zPosition="10" font="Regular;21" transparent="1" />
			<widget name="ButtonRed" pixmap="buttons/button_red.png" position="30,303" zPosition="10" size="15,16" transparent="1" alphatest="on" />
			<ePixmap pixmap="bottombar.png" position="10,250" size="540,120" zPosition="1" transparent="1" alphatest="on" />
		</screen>"""

	def __init__(self, session, currDir):
		self.skin = dirSelectDlg.skin
		Screen.__init__(self, session)
		self.session = session

		self["ButtonGreen"] = Pixmap()
		self["ButtonGreentext"] = Button()
		self["ButtonRed"] = Pixmap()
		self["ButtonRedtext"] = Label(_("Close"))
		self["filelist"] = FileList(currDir, showDirectories = True, showFiles = False, showMountpoints = False, useServiceRef = False)

		self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"],
		{
			"ok": self.ok,
			"back": self.cancel,
			"left": self.left,
			"right": self.right,
			"up": self.up,
			"down": self.down,
			"green": self.green,
			"red": self.red
		}, -1)

		self.onLayoutFinish.append(self.setStartDir)

	def setStartDir(self):
		if self["filelist"].canDescent():
			self["filelist"].descent()
		self.CurrentDirectory = self["filelist"].getCurrentDirectory()
		self.instance.setTitle(self.CurrentDirectory)
		self.setPathName()

	def updatePathName(self):
		if len(self["filelist"].getFilename()) > len(self.CurrentDirectory):
			self.setPathName()
		else:
			self["ButtonGreentext"].hide()
			self["ButtonGreen"].hide()
		self.instance.setTitle(self.CurrentDirectory)

	def setPathName(self):
		self.epath = self["filelist"].getFilename()
		if len(self.epath) > 1 and self.epath.endswith('/'):
			self.epath = self.epath[:-1]
		self["ButtonGreentext"].setText(_("select:") + " " + self.epath)
		self["ButtonGreentext"].show()
		self["ButtonGreen"].show()

	def ok(self):
		if self["filelist"].canDescent():
			self["filelist"].descent()
			if len(self["filelist"].getFilename()) > len(self["filelist"].getCurrentDirectory()):
				self.setPathName()
			else:
				self["ButtonGreentext"].hide()
				self["ButtonGreen"].hide()
			self.CurrentDirectory = self["filelist"].getCurrentDirectory()
			self.instance.setTitle(self.CurrentDirectory)

	def up(self):
		self["filelist"].up()
		self.updatePathName()

	def down(self):
		self["filelist"].down()
		self.updatePathName()

	def left(self):
		self["filelist"].pageUp()
		self.updatePathName()

	def right(self):
		self["filelist"].pageDown()
		self.updatePathName()

	def cancel(self):
		self.close(False)

	def red(self):
		self.close(False)

	def green(self):
		self.close(self.epath)
