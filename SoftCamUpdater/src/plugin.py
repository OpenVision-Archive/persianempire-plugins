#!/usr/bin/python
# -*- coding: utf-8 -*-
from Components.ActionMap import ActionMap
from Components.config import config, getConfigListEntry, ConfigSelection, ConfigSubsection
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.Sources.List import List
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
from Screens.PluginBrowser import PluginBrowser
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
import os
from Components.Console import Console

adress = "http://www.satsharing.net/files/SoftCam.Key"
bissaddress = "https://openvision.tech/persianpalace/Persian.BISS"
ownbiss = "Persian.BISS"

config.plugins.SoftCamUpdater = ConfigSubsection()
config.plugins.SoftCamUpdater.path = ConfigSelection(default = "/usr/keys/", choices = [
		("/usr/keys/", "/usr/keys/"),
		("/var/keys/", "/var/keys/"),
		("/var/emu/keys/", "/var/emu/keys/"),
		("/etc/keys/", "/etc/keys/"),
		("/var/etc/", "/var/etc/"),
		("/var/etc/emud/", "/var/etc/emud/"),
		("/etc/", "/etc/"),
		("/etc/tuxbox/config/", "/etc/tuxbox/config/"),
		])
config.plugins.SoftCamUpdater.keyname = ConfigSelection(default = "SoftCam.Key", choices = [
		("SoftCam.Key", "SoftCam.Key"),
		("softcam.cfg", "softcam.cfg"),
		("constant.cw", "constant.cw"),
		("AutoRoll.Key", "AutoRoll.Key"),
		("Autoupdate.Key", "Autoupdate.Key"),
		("keylist", "keylist"),
		("rsakeylist", "rsakeylist"),
		("tpscrypt", "tpscrypt"),
		("ppua", "ppua"),
		("constantcw", "constantcw"),
		("constcw", "constcw"),
		("cryptoworks", "cryptoworks"),
		("irdeto", "irdeto"),
		("irdeto2", "irdeto2"),
		("Keylist.txt", "Keylist.txt"),
		("nagra", "nagra"),
		("nagra2", "nagra2"),
		("seca", "seca"),
		("seca2", "seca2"),
		("via", "via"),
		("conax", "conax"),
		("crypto", "crypto"),
		("nds", "nds"),
		("oscam.keys", "oscam.keys"),
		("oscam.biss", "oscam.biss"),
		("ncam.keys", "ncam.keys"),
		("ncam.biss", "ncam.biss"),
		])
class SoftCamUpdater(ConfigListScreen, Screen):
	skin = """
<screen name="SoftCamUpdater" position="center,160" size="670,200" title="SoftCam Updater for Persian Palace">
		<widget position="15,10" size="640,50" name="config" scrollbarMode="showOnDemand" />
		<ePixmap position="80,170" zPosition="1" size="165,2" pixmap="~/images/red.png" alphatest="blend" />
		<widget source="Redkey" render="Label" position="80,170" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
		<ePixmap position="245,170" zPosition="1" size="165,2" pixmap="~/images/green.png" alphatest="blend" />
		<widget source="Greenkey" render="Label" position="245,170" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
		<ePixmap position="410,170" zPosition="1" size="165,2" pixmap="~/images/yellow.png" alphatest="blend" />
		<widget source="Yellowkey" render="Label" position="410,170" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
		<widget name="information" position="10,60" font="Regular;20" halign="center" valign="center" size="640,100" />
</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/SoftCamUpdater")
		self["information"] = Label(_("Latest Persian.BISS will be automatically merged."))
		self.list = []
		self.list.append(getConfigListEntry(_("Path"), config.plugins.SoftCamUpdater.path))
		self.list.append(getConfigListEntry(_("File name"), config.plugins.SoftCamUpdater.keyname))		
		ConfigListScreen.__init__(self, self.list)
		self["Redkey"] = StaticText(_("Close"))
		self["Greenkey"] = StaticText(_("Save"))
		self["Yellowkey"] = StaticText(_("Download"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "EPGSelectActions"],
		{
			"red": self.cancel,
			"cancel": self.cancel,
			"green": self.save,
			"yellow": self.downkey,
			"ok": self.save
		}, -2)
		
	def cancel(self):
		for i in self["config"].list:
			i[1].cancel()
		self.close(False)
	
	def save(self):
		for i in self["config"].list:
			i[1].save()
		self.mbox = self.session.open(MessageBox,(_("Saved successfull!")), MessageBox.TYPE_INFO, timeout = 3 )
		
	def downkey(self):
		try:
			Console().ePopen("wget -P /tmp %s" % bissaddress)
			Console().ePopen("wget -P /tmp %s" % adress)
			Console().ePopen("cat /tmp/%s /tmp/SoftCam.Key > /tmp/keyfile.tmp" % ownbiss)
			Console().ePopen("rm -rf /tmp/SoftCam.Key")
			if fileExists("%s%s" % (config.plugins.SoftCamUpdater.path.value, config.plugins.SoftCamUpdater.keyname.value)):
				Console().ePopen("cp -f %s%s %s%s.old" % (config.plugins.SoftCamUpdater.path.value, config.plugins.SoftCamUpdater.keyname.value, config.plugins.SoftCamUpdater.path.value, config.plugins.SoftCamUpdater.keyname.value[:-4]))
				Console().ePopen("rm -rf %s%s" % (config.plugins.SoftCamUpdater.path.value, config.plugins.SoftCamUpdater.keyname.value))
			Console().ePopen("cp -f /tmp/keyfile.tmp %s%s" % (config.plugins.SoftCamUpdater.path.value, config.plugins.SoftCamUpdater.keyname.value))
			Console().ePopen("rm -rf /tmp/keyfile.tmp")
			Console().ePopen("rm -rf /tmp/%s" % ownbiss)
			self.mbox = self.session.open(MessageBox,(_("Downloaded successfull!")), MessageBox.TYPE_INFO, timeout = 3 )
		except:
			self.mbox = self.session.open(MessageBox,(_("Download failed!")), MessageBox.TYPE_INFO, timeout = 3 )


def main(session, **kwargs):
	session.open(SoftCamUpdater)

def Plugins(**kwargs):
	return PluginDescriptor(
			name = _("SoftCam Updater 3.1"),
			description = _("Special version for Persian Palace"),
			where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
			icon="softcamupdater.png",
			fnc=main)
