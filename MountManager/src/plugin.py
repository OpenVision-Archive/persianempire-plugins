#!/usr/bin/python
# -*- coding: utf-8 -*-
from . import _
from Components.config import config, ConfigSubsection, ConfigText, ConfigYesNo
from Plugins.Plugin import PluginDescriptor
from HddMount import MountHddOnStart

config.plugins.HddMount = ConfigSubsection()
config.plugins.HddMount.MountOnStart = ConfigYesNo(default=True)
config.plugins.HddMount.MountOnHdd = ConfigText(default="nothing")
config.plugins.HddMount.MountOnMovie = ConfigText(default="nothing")
config.plugins.HddMount.SwapOnStart = ConfigYesNo(default=False)
config.plugins.HddMount.SwapFile = ConfigText(default="no")


def main(session, **kwargs):
	from Manager import MountSetup
	session.open(MountSetup)


EnigmaStart = False


def OnStart(reason, **kwargs):
	global EnigmaStart
	if reason == 0 and EnigmaStart == False:
		EnigmaStart = True
		enableswap = False
		if config.plugins.HddMount.SwapOnStart.value:
			SwapFile = config.plugins.HddMount.SwapFile.value
			if SwapFile != "no":
				if SwapFile[:2] == "sd":
					from Components.Console import Console
					Console().ePopen("swapon /dev/%s" % SwapFile[:4])
				else:
					enableswap = True
		if config.plugins.HddMount.MountOnStart.value:
			MountHddOnStart(config.plugins.HddMount.MountOnHdd.value,
				config.plugins.HddMount.MountOnMovie.value, enableswap)
		elif enableswap:
			MountHddOnStart("nothing", "nothing", enableswap)


def startMountManager(menuid):
	if menuid != "system":
		return []
	return [(_("Mount Manager"), main, "mount_manager", None)]


def Plugins(**kwargs):
	return PluginDescriptor(name=_("Mount Manager"), description="Special version for Open Vision", where=PluginDescriptor.WHERE_MENU, fnc=startMountManager)
