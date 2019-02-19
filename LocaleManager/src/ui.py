from . import _
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.config import ConfigSubsection, ConfigSelection, ConfigYesNo, ConfigDirectory, getConfigListEntry, NoSave, config
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.Language import language
from Tools.Directories import resolveFilename, fileExists, pathExists, SCOPE_LANGUAGE, SCOPE_PLUGINS
import os
from Screens.LocationBox import LocationBox

VERSION = 1.04

TEMP = "/tmp/"
STARTDIR = "/media/hdd/"
if not pathExists(STARTDIR):
	STARTDIR = TEMP

config.plugins.LocaleManager = ConfigSubsection()
choicelist = []
languages = language.getLanguageList()
default_language = language.getActiveLanguage()
for lng in languages:
	choicelist.append((lng[0],lng[1][0]))
config.plugins.LocaleManager.usedlang = NoSave(ConfigSelection(default = default_language, choices = choicelist))
config.plugins.LocaleManager.target = NoSave(ConfigDirectory(STARTDIR))
config.plugins.LocaleManager.enigma = NoSave(ConfigSelection(default = "move", choices = [("no", _("nothing")), (("delete", _("delete"))), (("move", _("move")))]))
config.plugins.LocaleManager.plugins = NoSave(ConfigYesNo(default = True))
cfg = config.plugins.LocaleManager


if not pathExists(cfg.target.value):
	cfg.target.value = TEMP

ENIGMA = resolveFilename(SCOPE_LANGUAGE).rstrip("/po/")
PLUGINS = resolveFilename(SCOPE_PLUGINS)

class LocaleManager(Screen, ConfigListScreen):
	y_size = 175
	skin = """
		<screen name="LocaleManager" position="center,center" size="560,%d" backgroundColor="#31000000" title="Locale Manager">
			<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
			<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
			<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
			<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
			<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="config" position="10,40" size="540,100" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="skin_default/div-h.png" position="0,%d" zPosition="1" size="560,2" />
			<ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,%d" size="14,14" zPosition="3"/>
			<widget font="Regular;18" halign="right" position="495,%d" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
				<convert type="ClockToText">Default</convert>
			</widget>
			<widget name="statusbar" position="10,%d" size="480,20" font="Regular;18" zPosition="2" transparent="0" foregroundColor="white" />
		</screen>""" % (y_size, y_size-25, y_size-19, y_size-22, y_size-20)

	def __init__(self, session):
		self.skin = LocaleManager.skin
		self.session = session
		Screen.__init__(self, session)

		self["actions"] = ActionMap(['ColorActions', 'SetupActions'],
		{
			"cancel": self.close,
			"red": self.close,
			"green": self.runRemove,
			"blue": self.selectTarget
		})

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Run"))
		self["key_blue"] = Label()

		self["statusbar"] = Label()

		self.inhibitDirs = ["/autofs", "/bin", "/boot", "/dev", "/etc", "/lib", "/proc", "/sbin", "/sys", "/tmp", "/usr", "/media/net"]

		self.removeLocaleCfglist = []
		self.removeLocaleCfglist.append(getConfigListEntry(_("Primary Language"), cfg.usedlang))
		self.removeLocaleCfglist.append(getConfigListEntry(_("Remove Unused Plugin's Language Files"), cfg.plugins))
		self.removeLocaleCfglist.append(getConfigListEntry(_("What About Enigma2 Language Files ?"), cfg.enigma))

		self.onChangedEntry = []
		ConfigListScreen.__init__(self, self.removeLocaleCfglist, session, on_change = self.changedEntry)

	def changedEntry(self):
		if cfg.enigma.value == "move":
			self["key_blue"].setText(_("Path"))
			self["statusbar"].setText(_("Move To %s") % cfg.target.value)
		else:
			self["key_blue"].setText("")
			self["statusbar"].setText("")	

	def runRemove(self):
		language = cfg.usedlang.value
		if cfg.plugins.value:
			dirs = self.lookDirs(PLUGINS, "locale", language)
			self.removeFiles(dirs, "locale", language)
		if cfg.enigma.value in["delete", "move"]:
			dirs = self.lookDirs(ENIGMA, "po", language)
			if cfg.enigma.value == "delete":
				self["statusbar"].setText(_("Deleting ..."))
				self.removeFiles(dirs, "po", language)
			elif cfg.enigma.value == "move":
				self["statusbar"].setText(_("Moving ..."))
				self.moveEnigmaFiles(dirs,language)

	def lookDirs(self, path, directory, language):
		locales = []
		lang = "%s/%s" % (directory, self.getName(language, directory))
		lastdir = directory + "/"
		for path, dirs, files in os.walk(path):
			if path.find(lastdir) != -1 and path.find("LC_MESSAGES") == -1 and path.find(lang) == -1:
				locales.append(path)
		return locales

	def getName(self, language, directory):
		if language.find("pt_BR") != -1 and directory == "po":
			return language
		return language.split("_")[0]

	def removeFiles(self, dirs, typ, language):
		for path in dirs:
			if typ == "po":
				try:
					path += "/LC_MESSAGES/enigma2.mo"
					self.osSystem("rm -R %s" % (path))
					target = "".join((ENIGMA,"/po/",self.getName(language,typ),"/LC_MESSAGES/enigma2.mo"))
					self.osSystem("ln -s %s %s" % (target, path))
				except:
					print "[LocaleManager] error", path
			else:
				try:
					self.osSystem("rm -R %s" % (path))
				except:
					print "[LocaleManager] error", path				
		self["statusbar"].setText(_("Removed"))

	def moveEnigmaFiles(self, dirs, language):
		newPath = cfg.target.value + "po"
		if not os.path.exists(newPath):
    			os.makedirs(newPath)
		for path in dirs:
			try:
				subDir = "".join((newPath,"/",path.split("/")[-1],"/LC_MESSAGES"))
				if not os.path.exists(subDir):
		    			os.makedirs(subDir)
				path += "/LC_MESSAGES/enigma2.mo"
				self.osSystem("mv %s %s" % (path, subDir))
				subDir += "/enigma2.mo"
				self.osSystem("ln -s %s %s" % (subDir, path))
			except:
				print "[LocaleManager] error", path
		self["statusbar"].setText(_("Moved"))

	def osSystem(self, cmd):
		os.system(cmd)

	def selectTarget(self):
		if cfg.enigma.value is not "move":
			return
		txt = _("Language Files Will Be Moved To")
		self.session.openWithCallback(self.targetDirSelected, LocationBox, text=txt, currDir=cfg.target.value,
						autoAdd=False, editDir=True,
						inhibitDirs=self.inhibitDirs, minFree=10 )

	def targetDirSelected(self, res):
		if res is not None:
			cfg.target.value = res
			self["statusbar"].setText("%s" % res)

