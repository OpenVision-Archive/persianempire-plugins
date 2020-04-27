#!/usr/bin/python
# -*- coding: utf-8 -*-
from gettext import bindtextdomain, dgettext, gettext
from os import environ
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

def localeInit():
	environ["LANGUAGE"] = language.getLanguage()[:2]
	bindtextdomain("MountManager", resolveFilename(SCOPE_PLUGINS, \
		"SystemPlugins/MountManager/locale"))

def _(txt):
	t = dgettext("MountManager", txt)
	if t == txt:
		t = gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)
