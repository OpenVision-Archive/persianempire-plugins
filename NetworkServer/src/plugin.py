#!/usr/bin/python
# -*- coding: utf-8 -*-
from __init__ import _
from Plugins.Plugin import PluginDescriptor
from setupSamba import setupSamba
from setupNfs import setupNfs

plugin_path = ""


def isInstalled(package):
	package = 'Package: ' + package
	try:
		f = open('/usr/lib/opkg/status', 'r')
		for line in f:
			if line.strip() == package:
				f.close()
				return True
	except IOError:
		pass

	return False


def setupSambaMain(session, iface=None, **kwargs):
	session.open(setupSamba, iface, plugin_path)


def setupNfsMain(session, iface=None, **kwargs):
	session.open(setupNfs, iface, plugin_path)


def setupSambaCallFunction(iface):
	if isInstalled('sambaserver') and not isInstalled('samba'):
		return setupSambaMain
	else:
		return None


def setupNfsCallFunction(iface):
	if isInstalled('nfs-utils'):
		return setupNfsMain
	else:
		return None


def Plugins(path, **kwargs):
	global plugin_path
	plugin_path = path
	return [
		PluginDescriptor(name=_("setupSamba"), description=_("Activate and configurate your Samba-Server"), where=PluginDescriptor.WHERE_NETWORKSETUP, fnc={"ifaceSupported": setupSambaCallFunction, "menuEntryName": lambda x: _("Samba-Server Setup"), "menuEntryDescription": lambda x: _("Start/Stop and manage your Samba-Server...\n")}),
		PluginDescriptor(name=_("setupNFS"), description=_("Activate and configurate your NFS-Server"), where=PluginDescriptor.WHERE_NETWORKSETUP, fnc={"ifaceSupported": setupNfsCallFunction, "menuEntryName": lambda x: _("NFS-Server Setup"), "menuEntryDescription": lambda x: _("Start/Stop and manage your NFS-Server...\n")})
	]
