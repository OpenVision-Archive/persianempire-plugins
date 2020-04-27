# -*- coding: utf-8 -*-
from . import _
from Plugins.Plugin import PluginDescriptor
import ui

def main(session,**kwargs):
	session.open(ui.LocaleManager)

def Plugins(path,**kwargs):
	return [PluginDescriptor(name="Locale Manager", description=_("Special version for Open Vision"), where = PluginDescriptor.WHERE_PLUGINMENU, icon = "plugin.png", fnc=main)]
