#!/usr/bin/python
# -*- coding: utf-8 -*-
from Components.Language import language
from Components.config import config
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import os, gettext
from skin import loadSkin

PluginLanguageDomain = 'PEPanel'
PluginLanguagePath = 'SystemPlugins/PEPanel/locale'

def loadSkinReal(skinPath):
    if os.path.exists(skinPath):
        loadSkin(skinPath)


def loadPluginSkin(pluginPath):
    loadSkinReal(pluginPath + '/' + config.skin.primary_skin.value)
    loadSkinReal(pluginPath + '/skin.xml')


def localeInit():
    lang = language.getLanguage()[:2]
    os.environ['LANGUAGE'] = lang
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


def _(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)
