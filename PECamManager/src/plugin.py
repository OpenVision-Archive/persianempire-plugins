from . import _
from Components.config import config, ConfigSubsection, ConfigText
from Plugins.Plugin import PluginDescriptor
from Softcam import checkconfigdir
from Manager import PECamManager
from Plugins.Extensions.PersianPalace import *

config.plugins.PECam = ConfigSubsection()
config.plugins.PECam.actcam = ConfigText(default="none")
config.plugins.PECam.camconfig = ConfigText(default="/usr/keys",
	visible_width=100, fixed_size=False)
config.plugins.PECam.camdir = ConfigText(default="/usr/camd",
	visible_width=100, fixed_size=False)

checkconfigdir()

def PELock():
    try:
        from pe import gettitle
        petitle = gettitle()
        return petitle
    except:
        return False

def main(session, **kwargs):
    if PELock() == False:
        return
    else:
	session.open(PECamManager)

EnigmaStart = False

def startcam(reason, **kwargs):
	if config.plugins.PECam.actcam.value != "none":
		global EnigmaStart
		if reason == 0 and not EnigmaStart:
			from Startup import startcamonstart
			EnigmaStart = True
			startcamonstart.start()
		elif reason == 1:
			from Softcam import stopcam
			stopcam(config.plugins.PECam.actcam.value)

def Plugins(**kwargs):
	return [PluginDescriptor(name = _("PE Cam Manager"),
		description = _("Special Version For Persian Empire"),
		where = [PluginDescriptor.WHERE_PLUGINMENU,
		PluginDescriptor.WHERE_EXTENSIONSMENU],
		icon = "pecammanager.png", fnc = main),
	PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART,
		needsRestart = True, fnc = startcam)]
