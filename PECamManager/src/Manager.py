# -*- coding: utf-8 -*-
from . import _
from os import path, listdir
from enigma import eTimer
from Components.ActionMap import ActionMap
from Components.config import config, getConfigListEntry
from Components.Console import Console
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from .Softcam import checkconfigdir, getcamcmd, getcamscript, stopcam


class PECamManager(Screen):
	skin = """
		<screen position="center,center" size="630,370" title="PE Cam Manager">
			<eLabel position="5,0" size="620,2" backgroundColor="#aaaaaa" />
			<widget source="list" render="Listbox" position="10,15" size="340,300" \
				scrollbarMode="showOnDemand">
				<convert type="TemplatedMultiContent">
					{
						"template": [MultiContentEntryPixmapAlphaTest(pos=(5, 5), \
								size=(41, 41), png=1),
							MultiContentEntryText(pos=(65, 10), size=(275, 40), font=0, \
								flags=RT_HALIGN_LEFT, text=0),
							MultiContentEntryText(pos=(5, 25), size=(51, 16), font=1, \
								flags=RT_HALIGN_CENTER, text=2),],
						"fonts": [gFont("Regular", 26), gFont("Regular", 12)],
						"itemHeight": 50
					}
				</convert>
			</widget>
			<eLabel horizontalAlignment="center" position="390,10" size="210,35" font="Regular;20" \
				text="ECM Info" transparent="1" />
			<widget name="status" position="360,50" size="320,300" font="Regular;16" \
				horizontalAlignment="left" />
			<eLabel position="12,358" size="148,2" backgroundColor="#00ff2525" />
			<eLabel position="165,358" size="148,2" backgroundColor="#00389416" />
			<eLabel position="318,358" size="148,2" backgroundColor="#00baa329" />
			<eLabel position="471,358" size="148,2" backgroundColor="#006565ff" />
			<widget source="key_red" render="Label" position="12,328" zPosition="2" size="148,30" \
				verticalAlignment="center" horizontalAlignment="center" font="Regular;22" transparent="1" />
			<widget source="key_green" render="Label" position="165,328" zPosition="2" size="148,30" \
				verticalAlignment="center" horizontalAlignment="center" font="Regular;22" transparent="1" />
			<widget source="key_yellow" render="Label" position="318,328" zPosition="2" size="148,30" \
				verticalAlignment="center" horizontalAlignment="center" font="Regular;22" transparent="1" />
			<widget source="key_blue" render="Label" position="471,328" zPosition="2" size="148,30" \
				verticalAlignment="center" horizontalAlignment="center" font="Regular;22" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("PE Cam Manager"))
		self.Console = Console()
		self["key_red"] = StaticText(_("Stop"))
		self["key_green"] = StaticText(_("Start"))
		self["key_yellow"] = StaticText(_("Restart"))
		self["key_blue"] = StaticText(_("Setup"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.ok,
				"green": self.start,
				"red": self.stop,
				"yellow": self.restart,
				"blue": self.setup
			})
		self["status"] = Label()
		self["list"] = List([])
		checkconfigdir()
		self.actcam = config.plugins.PECam.actcam.value
		self.camstartcmd = ""
		self.actcampng = LoadPixmap(path=resolveFilename(SCOPE_PLUGINS,
			"Extensions/PECamManager/images/activate.png"))
		self.defcampng = LoadPixmap(path=resolveFilename(SCOPE_PLUGINS,
			"Extensions/PECamManager/images/deactivate.png"))
		self.stoppingTimer = eTimer()
		self.stoppingTimer.timeout.get().append(self.stopping)
		self.closestopTimer = eTimer()
		self.closestopTimer.timeout.get().append(self.closestop)
		self.createinfo()
		self.Timer = eTimer()
		self.Timer.callback.append(self.listecminfo)
		self.Timer.start(2000, False)

	def listecminfo(self):
		try:
			with open("/tmp/ecm.info", "r") as ecmfile:
				self["status"].setText(ecmfile.read())
			ecmfile.close()
		except:
			self["status"].setText("")

	def createinfo(self):
		self.iscam = False
		self.finish = False
		self.camliststart()
		self.listecminfo()

	def camliststart(self):
		if path.exists(config.plugins.PECam.camdir.value):
			self.softcamlist = listdir(config.plugins.PECam.camdir.value)
			if self.softcamlist:
				self.softcamlist.sort()
				self.iscam = True
				self.Console.ePopen("chmod 755 %s/*" % config.plugins.PECam.camdir.value)
				if self.actcam != "none" and getcamscript(self.actcam):
					self.createcamlist()
				else:
					self.Console.ePopen("pidof %s" % self.actcam, self.camactive)
			else:
				self.finish = True
				self["list"].setList([])
		else:
			checkconfigdir()
			self.camliststart()

	def camactive(self, result, retval, extra_args):
		if result.strip():
			self.createcamlist()
		else:
			self.actcam = "none"
			self.checkConsole = Console()
			for line in self.softcamlist:
				self.checkConsole.ePopen("pidof %s" % line, self.camactivefromlist, line)
			self.checkConsole.ePopen("echo 1", self.camactivefromlist, "none")

	def camactivefromlist(self, result, retval, extra_args):
		if result.strip():
			self.actcam = extra_args
			self.createcamlist()
		else:
			self.finish = True

	def createcamlist(self):
		camlist = []
		if self.actcam != "none":
			camlist.append((self.actcam, self.actcampng, self.checkcam(self.actcam)))
		for line in self.softcamlist:
			if line != self.actcam:
				camlist.append((line, self.defcampng, self.checkcam(line)))
		self["list"].setList(camlist)
		self.finish = True

	def checkcam(self, cam):
		cam = "."
		return cam

	def start(self):
		if self.iscam and self.finish:
			self.camstart = self["list"].getCurrent()[0]
			if self.camstart != self.actcam:
				self.camstartcmd = getcamcmd(self.camstart)
				msg = _("Starting : %s") % self.camstart
				self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
				self.stoppingTimer.start(100, False)

	def stop(self):
		if self.iscam and self.actcam != "none" and self.finish:
			stopcam(self.actcam)
			msg = _("Stopping : %s") % self.actcam
			self.actcam = "none"
			self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
			self.closestopTimer.start(1000, False)

	def closestop(self):
		self.closestopTimer.stop()
		self.mbox.close()
		self.createinfo()

	def restart(self):
		if self.iscam and self.actcam != "none" and self.finish:
			self.camstart = self.actcam
			if self.camstartcmd == "":
				self.camstartcmd = getcamcmd(self.camstart)
			msg = _("Restarting : %s") % self.actcam
			self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
			self.stoppingTimer.start(100, False)

	def stopping(self):
		self.stoppingTimer.stop()
		stopcam(self.actcam)
		self.actcam = self.camstart
		service = self.session.nav.getCurrentlyPlayingServiceReference()
		if service:
			self.session.nav.stopService()
		self.Console.ePopen(self.camstartcmd)
		if self.mbox:
			self.mbox.close()
		if service:
			self.session.nav.playService(service)
		self.createinfo()

	def ok(self):
		if self.iscam and self.finish:
			if self["list"].getCurrent()[0] != self.actcam:
				self.start()
			else:
				self.restart()

	def cancel(self):
		if self.finish:
			if config.plugins.PECam.actcam.value != self.actcam:
				config.plugins.PECam.actcam.value = self.actcam
			config.plugins.PECam.save()
			self.close()
		else:
			self.cancelTimer = eTimer()
			self.cancelTimer.timeout.get().append(self.setfinish)
			self.cancelTimer.start(4000, False)

	def setfinish(self):
		self.cancelTimer.stop()
		self.finish = True
		self.cancel()

	def setup(self):
		if self.finish:
			self.session.openWithCallback(self.createinfo, ConfigEdit)


class ConfigEdit(Screen, ConfigListScreen):
	skin = """
		<screen name="ConfigEdit" position="center,center" size="500,200" \
			title="Cam Path Configuration">
			<eLabel position="5,0" size="490,2" backgroundColor="#aaaaaa" />
			<widget name="config" position="30,20" size="460,50" zPosition="1" \
				scrollbarMode="showOnDemand" />
			<eLabel position="85,180" size="166,2" backgroundColor="#00ff2525" />
			<eLabel position="255,180" size="166,2" backgroundColor="#00389416" />
			<widget source="key_red" render="Label" position="85,150" zPosition="2" size="170,30" \
				verticalAlignment="center" horizontalAlignment="center" font="Regular;22" transparent="1" />
			<widget source="key_green" render="Label" position="255,150" zPosition="2" size="170,30" \
				verticalAlignment="center" horizontalAlignment="center" font="Regular;22" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("Path Configuration"))
		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("Ok"))
		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"red": self.cancel,
				"ok": self.ok,
				"green": self.ok,
			}, -2)
		configlist = []
		ConfigListScreen.__init__(self, configlist, session=session)
		configlist.append(getConfigListEntry(_("Config Directory"),
			config.plugins.PECam.camconfig))
		configlist.append(getConfigListEntry(_("Binary directory"),
			config.plugins.PECam.camdir))
		self["config"].setList(configlist)

	def ok(self):
		msg = []
		if not path.exists(config.plugins.PECam.camconfig.value):
			msg.append("%s " % config.plugins.PECam.camconfig.value)
		if not path.exists(config.plugins.PECam.camdir.value):
			msg.append("%s " % config.plugins.PECam.camdir.value)
		if msg == []:
			if config.plugins.PECam.camconfig.value[-1] == "/":
				config.plugins.PECam.camconfig.value = \
					config.plugins.PECam.camconfig.value[:-1]
			if config.plugins.PECam.camdir.value[-1] == "/":
				config.plugins.PECam.camdir.value = \
					config.plugins.PECam.camdir.value[:-1]
			config.plugins.PECam.save()
			self.close()
		else:
			self.mbox = self.session.open(MessageBox,
				_("Directory %s Doesn't Exist !\nPlease Set The Correct Directory Path !")
				% msg, MessageBox.TYPE_INFO, timeout=5)

	def cancel(self, answer=None):
		if answer is None:
			if self["config"].isChanged():
				self.session.openWithCallback(self.cancel, MessageBox,
					_("Close Without Saving Settings ?"))
			else:
				self.close()
		elif answer:
			config.plugins.PECam.camconfig.cancel()
			config.plugins.PECam.camdir.cancel()
			self.close()
