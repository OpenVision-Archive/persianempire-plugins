from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
from Tools.Directories import fileExists
from GlobalActions import globalActionMap
from keymapparser import readKeymap, removeKeymap
from os import environ
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.Console import Console
from Components.Language import language
from Components.config import config, getConfigListEntry, ConfigText, ConfigInteger, ConfigClock, ConfigSelection, ConfigSubsection, ConfigYesNo, configfile, NoSave
from Components.ConfigList import ConfigListScreen
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Components.Sources.StaticText import StaticText
import os
import gettext
from Components.PluginComponent import plugins

if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/PECamManager/Softcam.py"):
	from Plugins.Extensions.PECamManager.Softcam import getcamcmd
	
lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("camrestart", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/CamRestart/locale/"))

def _(txt):
	t = gettext.dgettext("camrestart", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t
	
config.plugins.pecr = ConfigSubsection()
config.plugins.pecr.keyname = ConfigSelection(default = "KEY_TEXT", choices = [
		("KEY_TEXT", "TEXT"),
		("KEY_SUBTITLE", "SUBTITLE"),
		("KEY_HELP", "HELP"),
		])

class QuickEmu():
	def __init__(self):
		self.dialog = None

	def gotSession(self, session):
		self.session = session
		self.Console = Console()
		keymap = "/usr/lib/enigma2/python/Plugins/Extensions/CamRestart/keymap.xml"
		global globalActionMap
		readKeymap(keymap)
		globalActionMap.actions['showCamRestart'] = self.restartCam
		
	def restartCam(self):
		camname = ""
		emunam = ""
		estart = ""
		estop = ""

		if fileExists("/etc/rc3.d/S99camd-persianpalace.sh"):
			self.Console.ePopen("/etc/rc3.d/S99camd-persianpalace.sh restart")

		elif fileExists("/usr/lib/enigma2/python/Plugins/Extensions/PECamManager/Softcam.py"):
			service = self.session.nav.getCurrentlyPlayingServiceReference()
			emunam = config.plugins.PECam.actcam.value
			if emunam != "none":
				self.Console.ePopen("killall -9 %s" % emunam)
				if service:
					self.session.nav.stopService()
				self.Console.ePopen(getcamcmd(emunam))
				if service:
					self.session.nav.playService(service)

	def showcamname(self):
		serlist = None
		camdlist = None
		nameemu = []
		nameser = []

		if fileExists("/tmp/.cam.info"):
			try:
				for line in open("/tmp/.cam.info"):
					return line
			except:
				return None

		elif fileExists("/usr/lib/enigma2/python/Plugins/Extensions/PECamManager/plugin.py"): 
			if config.plugins.PECam.actcam.value != "none": 
				return config.plugins.PECam.actcam.value 
			else: 
				return None

class pecr_setup(ConfigListScreen, Screen):
	skin = """
<screen name="pecr_setup" position="center,160" size="750,370" title="PE Cam Restart">
  <widget position="15,10" size="720,200" name="config" scrollbarMode="showOnDemand" />
   <ePixmap position="10,358" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CamRestart/images/red.png" alphatest="blend" />
  <widget source="key_red" render="Label" position="10,328" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
  <ePixmap position="175,358" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CamRestart/images/green.png" alphatest="blend" />
  <widget source="key_green" render="Label" position="175,328" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_("PE Cam Restart"))
		self.list = []
		self.list.append(getConfigListEntry(_("Restart Key (Long Press)"), config.plugins.pecr.keyname))
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "EPGSelectActions"],
		{
			"red": self.cancel,
			"cancel": self.cancel,
			"green": self.save,
			"ok": self.save
		}, -2)
	

	def cancel(self):
		for i in self["config"].list:
			i[1].cancel()
		self.close(False)

	def save(self):
		config.plugins.pecr.keyname.save()
		configfile.save()
		keyfile = open("/usr/lib/enigma2/python/Plugins/Extensions/CamRestart/keymap.xml", "w")
		keyfile.write('<keymap>\n\t<map context="GlobalActions">\n\t\t<key id="%s" mapto="showCamRestart" flags="l" />\n\t</map>\n</keymap>' % config.plugins.pecr.keyname.value)
		keyfile.close()
		self.mbox = self.session.open(MessageBox,(_("Saved")), MessageBox.TYPE_INFO, timeout = 3 )
		plugins.reloadPlugins()

def main(session, **kwargs):
	session.open(pecr_setup)

pEmu = QuickEmu()

def sessionstart(reason,session=None, **kwargs):
	if reason == 0:
		pEmu.gotSession(session)

def Plugins(**kwargs):
	result = [
		PluginDescriptor(
			where = [PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART],
			fnc = sessionstart
		),
		PluginDescriptor(
			name=_("Cam Restart"),
			description = _("Special version for Open Vision"),
			where = PluginDescriptor.WHERE_PLUGINMENU,
			icon = 'camrestart.png',
			fnc = main
		),
	]
	return result
