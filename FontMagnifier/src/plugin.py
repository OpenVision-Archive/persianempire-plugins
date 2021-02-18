#!/usr/bin/python
# -*- coding: utf-8 -*-
fm_version="0.6.2"

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Components.config import config, ConfigSubsection, ConfigEnableDisable, ConfigInteger, ConfigSelection, getConfigListEntry, ConfigText
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LIBDIR
from Components.Label import Label
from Components.MenuList import MenuList
from Screens.MessageBox import MessageBox
from enigma import eTimer, getBoxType
from time import *
from __init__ import _
import os
import xml.etree.cElementTree
import glob
from Components.Console import Console

model = getBoxType()

config.plugins.fm = ConfigSubsection()
config.plugins.fm.display_manipulation_active = ConfigEnableDisable(default=False)
config.plugins.fm.active = ConfigEnableDisable(default=False)
config.plugins.fm.display_subtitles = ConfigEnableDisable(default=False)
config.plugins.fm.fontsize = ConfigInteger(default=80, limits=(40, 90))
config.plugins.fm.evv_fontsize = ConfigInteger(default=22, limits=(10, 50))
config.plugins.fm.show_only_clock = ConfigEnableDisable(default=False)
config.plugins.fm.single_epg_description_fontsize = ConfigInteger(default=20, limits=(10, 40))
config.plugins.fm.single_epg_list_fontsize = ConfigInteger(default=25, limits=(10, 40))
config.plugins.fm.single_epg_list_fontsize2 = ConfigInteger(default=25, limits=(10, 40))
config.plugins.fm.channel_list_epg_description_fontsize = ConfigInteger(default=20, limits=(10, 40))
config.plugins.fm.channel_list_fontsize = ConfigInteger(default=20, limits=(10, 40))
config.plugins.fm.Subtitle_TTX = ConfigInteger(default=40, limits=(20, 80))
config.plugins.fm.Subtitle_Regular = ConfigInteger(default=40, limits=(20, 80))
config.plugins.fm.Subtitle_Bold = ConfigInteger(default=40, limits=(20, 80))
config.plugins.fm.Subtitle_Italic = ConfigInteger(default=40, limits=(20, 80))
config.plugins.fm.movie_list_fontsize = ConfigInteger(default=20, limits=(10, 40))
config.plugins.fm.infobar_fontsize_event_now = ConfigInteger(default=22, limits=(10, 30))
config.plugins.fm.infobar_fontsize_event_next = ConfigInteger(default=22, limits=(10, 30))
regularFontExistInXML = 0
regularFontList = ConfigSelection(choices=[], default="")
config.plugins.fm.regular_Font = ConfigText(default="")
savedSettingsList = []

def Plugins(**kwargs):
    return [PluginDescriptor(name=("Font Magnifier 0.6.1"), description=_("Tool to change font sizes easily."), where=PluginDescriptor.WHERE_PLUGINMENU, icon="fm.png", fnc=main)]

def main(session, **kwargs):
        hw_type_string = model
        hw_type_string = hw_type_string + "\n"
        hw_type_file = open("/tmp/fontmagnifier_hw_type.txt", "w")
        hw_type_file.write(hw_type_string)
        hw_type_file.close()
        session.open(fmConfiguration)

class fmConfiguration(Screen, ConfigListScreen):
    skin = """
        <screen name="FontMagnifierConfigScreen" position="center,center" size="560,425" title="Font Magnifier V%s">
            <ePixmap pixmap="buttons/red.png" position="0,0" size="140,40" alphatest="on" />
            <ePixmap pixmap="buttons/green.png" position="140,0" size="140,40" alphatest="on" />
            <ePixmap pixmap="buttons/key_info.png" position="520,0" size="140,40" alphatest="on" />
            <ePixmap pixmap="buttons/key_menu.png" position="470,0" size="140,40" alphatest="on" />
            <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
            <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
            <widget name="config" position="5,50" size="550,385" scrollbarMode="showOnDemand" zPosition="1"/>
        </screen>""" % fm_version

    def __init__(self, session, args=0):
        Screen.__init__(self, session)

        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("OK"))
        self["setupActions"] = ActionMap(["EPGSelectActions", "SetupActions", "ColorActions", "MenuActions", "DirectionActions"],
        {
            "green": self.save,
            "red": self.cancel,
            "save": self.save,
            "cancel": self.cancel,
            "ok": self.save,
            "info": self.info,
            "menu": self.handle_menukey,
        })

        self.list = []
        ConfigListScreen.__init__(self, self.list, session=session)
        self.tree = xml.etree.cElementTree.parse("/usr/share/enigma2/%s" % (config.skin.primary_skin.value))
        self.root = self.tree.getroot()
        self.list_of_screens = self.root.findall("screen")
        self.list_of_subtitles = self.root.findall("subtitles")
        self.list_of_fonts = self.root.findall("fonts")

        self.getcurrent_font_epg_description()
        self.getcurrent_font_single_epg_description()
        self.getcurrent_font_single_epg_service_list()
        self.getcurrent_font_epg_descr_channel_list()
        self.getcurrent_font_channel_list()
        self.getcurrent_font_subtitles()
        self.getcurrent_font_movie_list()
        self.getcurrent_font_infobar_event_now()
        self.getcurrent_font_infobar_event_next()
        self.getcurrent_regularFont()
        self.createSetup()

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.createSetup()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.createSetup()

    def getcurrent_font_epg_description(self):
        tag_gefunden=0
        for element in self.list_of_screens:
            if element.keys():
                for name, value in element.items():
                    if name == "name" and value == "EventView":
                        if element.getchildren():
                            for child in element:
                                if child.get("name") == "epg_description":
                                    epg_description_font = child.get("font")
                                    font_elements = epg_description_font.split(";")
                                    if len(font_elements)==2:
                                        config.plugins.fm.evv_fontsize.value = int(font_elements[1])
                                        tag_gefunden=1
                                        break
                            if tag_gefunden==1:
                                break
                if tag_gefunden==1:
                    break

    def getcurrent_font_single_epg_description(self):
        tag_gefunden=0
        for element in self.list_of_screens:
            if element.keys():
                for name, value in element.items():
                    if name == "name" and value == "EPGSelection":
                        if element.getchildren():
                            for child in element:
                                if child.getchildren():
                                    for sub_child in child:
                                        if sub_child.tag == "convert":
                                            if sub_child.text == "ExtendedDescription":
                                                tag_gefunden=1
                                                break
                                    if tag_gefunden == 1:
                                        epg_description_font = child.get("font")
                                        font_elements = epg_description_font.split(";")
                                        if len(font_elements)==2:
                                            config.plugins.fm.single_epg_description_fontsize.value = int(font_elements[1])
                                        break
                            if tag_gefunden==1:
                                break
                if tag_gefunden==1:
                    break

    def getcurrent_font_single_epg_service_list(self):
        try:
            config.plugins.fm.single_epg_list_fontsize.value = 0
            config.plugins.fm.single_epg_list_fontsize2.value = 0
            EpgList_file = open(resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/EpgList.pyo"), "r")
            anzahl_der_gefundenen_schriften = 0
            for zeile in EpgList_file:
                if zeile.find("\t\tself.l.setFont(0") is not -1:
                    function_arguments = zeile.split(",")
                    if len(function_arguments) == 3:
                        font_size_argument = function_arguments[2]
                        font_size = font_size_argument.split(")")
                        if len(font_size) == 3:
                            config.plugins.fm.single_epg_list_fontsize.value = int(font_size[0])
                            anzahl_der_gefundenen_schriften += 1
                elif zeile.find("\t\tself.l.setFont(1") is not -1:
                    function_arguments = zeile.split(",")
                    if len(function_arguments) == 3:
                        font_size_argument = function_arguments[2]
                        font_size = font_size_argument.split(")")
                        if len(font_size) == 3:
                            config.plugins.fm.single_epg_list_fontsize2.value = int(font_size[0])
                            anzahl_der_gefundenen_schriften += 1
                if anzahl_der_gefundenen_schriften == 2:
                    break
            EpgList_file.close()
        except:
            config.plugins.fm.single_epg_list_fontsize.value = 0
            config.plugins.fm.single_epg_list_fontsize2.value = 0

    def getcurrent_font_epg_descr_channel_list(self):
        try:
            tag_gefunden=0
            config.plugins.fm.channel_list_epg_description_fontsize.value=0
            for element in self.list_of_screens:
                if element.keys():
                    for name, value in element.items():
                        if name == "name" and value == "ChannelSelection":
                            if element.getchildren():
                                for child in element:
                                    if child.getchildren():
                                        for sub_child in child:
                                            if sub_child.tag == "convert":
                                                if sub_child.text == "ExtendedDescription":
                                                    tag_gefunden=1
                                                    break
                                        if tag_gefunden == 1:
                                            epg_description_font = child.get("font")
                                            font_elements = epg_description_font.split(";")
                                            if len(font_elements) == 2:
                                                config.plugins.fm.channel_list_epg_description_fontsize.value = int(font_elements[1])
                                            break
                                if tag_gefunden == 1:
                                    break
                    if tag_gefunden == 1:
                        break
        except:
            config.plugins.fm.channel_list_epg_description_fontsize.value = 0

    def getcurrent_font_channel_list(self):
        try:
            tag_gefunden=0
            for element in self.list_of_screens:
                if element.keys():
                    for name, value in element.items():
                        if name == "name" and value == "ChannelSelection":
                            if element.getchildren():
                                for child in element:
                                    if child.get("name") == "list":
                                        epg_description_font = child.get("serviceNameFont")
                                        font_elements = epg_description_font.split(";")
                                        if len(font_elements)==2:
                                            config.plugins.fm.channel_list_fontsize.value = int(font_elements[1])
                                            tag_gefunden=1
                                            break
                                if tag_gefunden==1:
                                    break
                    if tag_gefunden==1:
                        break
        except:
            config.plugins.fm.channel_list_fontsize.value = 0

    def getcurrent_font_subtitles(self):
        config.plugins.fm.Subtitle_TTX.value = 0
        config.plugins.fm.Subtitle_Regular.value = 0
        config.plugins.fm.Subtitle_Bold.value = 0
        config.plugins.fm.Subtitle_Italic.value = 0
        if len(self.list_of_subtitles) != 0:
            for element in self.list_of_subtitles:
                if element.getchildren():
                    for child in element:
                        if child.get("name") == "Subtitle_TTX":
                            font = child.get("font")
                            font_elements = font.split(";")
                            if len(font_elements)==2:
                                config.plugins.fm.Subtitle_TTX.value = int(font_elements[1])
                        elif child.get("name") == "Subtitle_Regular":
                            font = child.get("font")
                            font_elements = font.split(";")
                            if len(font_elements)==2:
                                config.plugins.fm.Subtitle_Regular.value = int(font_elements[1])
                        elif child.get("name") == "Subtitle_Bold":
                            font = child.get("font")
                            font_elements = font.split(";")
                            if len(font_elements)==2:
                                config.plugins.fm.Subtitle_Bold.value = int(font_elements[1])
                        elif child.get("name") == "Subtitle_Italic":
                            font = child.get("font")
                            font_elements = font.split(";")
                            if len(font_elements)==2:
                                config.plugins.fm.Subtitle_Italic.value = int(font_elements[1])

    def getcurrent_font_movie_list(self):
        try:
            config.plugins.fm.movie_list_fontsize.value = 0
            MovieList_file = open(resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/MovieList.pyo"), "r")
            for zeile in MovieList_file:
                if zeile.find("\t\t\tself.l.setFont(0") is not -1:
                    function_arguments = zeile.split(",")
                    if len(function_arguments) == 3:
                        font_size_argument = function_arguments[2]
                        font_size = font_size_argument.split(")")
                        if len(font_size) == 3:
                            config.plugins.fm.movie_list_fontsize.value = int(font_size[0])
                            break
            MovieList_file.close()
        except:
            config.plugins.fm.movie_list_fontsize.value = 0

    def getcurrent_font_infobar_event_now(self):
        config.plugins.fm.infobar_fontsize_event_now.value=0
        tag_gefunden=0
        for element in self.list_of_screens:
            if element.keys():
                for name, value in element.items():
                    if name == "name" and value == "InfoBar":
                        if element.getchildren():
                            for child in element:
                                if child.get("source") == "session.Event_Now":
                                    if child.getchildren():
                                        for sub_child in child:
                                            if sub_child.tag == "convert":
                                                if sub_child.text == "Name":
                                                    tag_gefunden=1
                                                    break
                                        if tag_gefunden == 1:
                                            infobar_font = child.get("font")
                                            font_elements = infobar_font.split(";")
                                            if len(font_elements) == 2:
                                                config.plugins.fm.infobar_fontsize_event_now.value = int(font_elements[1])
                                            break
                                if tag_gefunden == 1:
                                    break
                    if tag_gefunden == 1:
                        break

    def getcurrent_font_infobar_event_next(self):
        config.plugins.fm.infobar_fontsize_event_next.value=0
        tag_gefunden=0
        for element in self.list_of_screens:
            if element.keys():
                for name, value in element.items():
                    if name == "name" and value == "InfoBar":
                        if element.getchildren():
                            for child in element:
                                if child.get("source") == "session.Event_Next":
                                    if child.getchildren():
                                        for sub_child in child:
                                            if sub_child.tag == "convert":
                                                if sub_child.text == "Name":
                                                    tag_gefunden=1
                                                    break
                                        if tag_gefunden == 1:
                                            infobar_font = child.get("font")
                                            font_elements = infobar_font.split(";")
                                            if len(font_elements) == 2:
                                                config.plugins.fm.infobar_fontsize_event_next.value = int(font_elements[1])
                                            break
                                if tag_gefunden == 1:
                                    break
                    if tag_gefunden == 1:
                        break
    def getcurrent_regularFont(self):
        global regularFontExistInXML
        global regularFontList
        if len(self.list_of_fonts) != 0:
            for element in self.list_of_fonts:
                if element.getchildren():
                    for child in element:
                        if child.get("name") == "Regular":
                            currentRegularFontFilename = child.get("filename")
                            defaultFontFilename = currentRegularFontFilename
                            regularFontExistInXML = 1

        if regularFontExistInXML == 1:
            fontList=[]
            fontListWithPath = glob.glob("/usr/share/fonts/*.ttf")
            for sFile in fontListWithPath:
                fontList.append(sFile.replace("/usr/share/fonts/", ""))

            regularFontList = ConfigSelection(choices=fontList, default=defaultFontFilename)
            regularFontList.setValue(currentRegularFontFilename)

    def createSetup(self):
        global regularFontExistInXML
        global regularFontList
        self.list = []
        self.list.append(getConfigListEntry(_("Enable display options"), config.plugins.fm.display_manipulation_active))
        if config.plugins.fm.display_manipulation_active.value:
            if os.path.exists(resolveFilename(SCOPE_PLUGINS, "Extensions/ExtendedServiceInfo")):
                self.list.append(getConfigListEntry(_("Enable service number in display"), config.plugins.fm.active))
            if config.plugins.fm.active.value:
                self.list.append(getConfigListEntry(_("Enter service number font size in pixel"), config.plugins.fm.fontsize))
            self.list.append(getConfigListEntry(_("Show only time in display when box is in standby"), config.plugins.fm.show_only_clock))

        if regularFontExistInXML == 1:
            self.list.append(getConfigListEntry(_("Select regular font"), regularFontList))

        self.list.append(getConfigListEntry(_("Enter font size for epg description in pixel"), config.plugins.fm.evv_fontsize))
        self.list.append(getConfigListEntry(_("Enter font size for epg description in single epg"), config.plugins.fm.single_epg_description_fontsize))
        if config.plugins.fm.single_epg_list_fontsize.value != 0:
            self.list.append(getConfigListEntry(_("Enter font size for channel list in single epg"), config.plugins.fm.single_epg_list_fontsize))
        if config.plugins.fm.single_epg_list_fontsize2.value != 0:
            self.list.append(getConfigListEntry(_("Enter font size for date/time in multi epg"), config.plugins.fm.single_epg_list_fontsize2))
        if config.plugins.fm.channel_list_epg_description_fontsize.value != 0:
            self.list.append(getConfigListEntry(_("Font size for epg description in channel list"), config.plugins.fm.channel_list_epg_description_fontsize))
        if config.plugins.fm.channel_list_fontsize.value != 0:
            self.list.append(getConfigListEntry(_("Font size for channel list"), config.plugins.fm.channel_list_fontsize))
        if config.plugins.fm.movie_list_fontsize.value != 0:
            self.list.append(getConfigListEntry(_("Font size for movie list"), config.plugins.fm.movie_list_fontsize))
        if config.plugins.fm.infobar_fontsize_event_now.value != 0:
            self.list.append(getConfigListEntry(_("Font size for infobar event now"), config.plugins.fm.infobar_fontsize_event_now))
        if config.plugins.fm.infobar_fontsize_event_next.value != 0:
            self.list.append(getConfigListEntry(_("Font size for infobar event next"), config.plugins.fm.infobar_fontsize_event_next))

        self.list.append(getConfigListEntry(_("show subtitle options"), config.plugins.fm.display_subtitles))
        if config.plugins.fm.display_subtitles.value:
            if config.plugins.fm.Subtitle_TTX.value != 0:
                self.list.append(getConfigListEntry(_("Font size for subtitles (Teletext)"), config.plugins.fm.Subtitle_TTX))
            if config.plugins.fm.Subtitle_Regular.value != 0:
                self.list.append(getConfigListEntry(_("Font size for subtitles (Regular)"), config.plugins.fm.Subtitle_Regular))
            if config.plugins.fm.Subtitle_Bold.value != 0:
                self.list.append(getConfigListEntry(_("Font size for subtitles (Bold)"), config.plugins.fm.Subtitle_Bold))
            if config.plugins.fm.Subtitle_Italic.value != 0:
                self.list.append(getConfigListEntry(_("Font size for subtitles (Italic)"), config.plugins.fm.Subtitle_Italic))

        self["config"].list = self.list
        self["config"].l.setList(self.list)

    def save(self):
        for x in self["config"].list:
           x[1].save()

        self.session.open(fmWaitScreen, self.tree)
        self.close()

    def cancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close(False)

    def info(self):
        aboutbox = self.session.open(MessageBox, _("Font magnifier plugin\n\nThis plugin helps you to\nset up different font sizes.\n\n(c) 2012 - BigReaper"), MessageBox.TYPE_INFO)
        aboutbox.setTitle(_("Info...")) 

    def handle_menukey(self):
        self.session.open(fmOptions)

class fmOptions(Screen):
    skin = """
        <screen name="fmOptionsScreen" position="center,center" size="450,130" zPosition="6" title="Options">
            <widget name="optionslist" position="10,5" zPosition="7" size="450,130" scrollbarMode="showOnDemand" transparent="1" />
        </screen>"""

    def __init__(self, session, args=0):
        Screen.__init__(self, session)

        self["setupActions"] = ActionMap(["SetupActions", "MenuActions"],
        {
            "cancel": self.cancel,
            "ok": self.ok,
        })

        self.list = []
        if os.path.exists("/usr/share/enigma2/%s.bak" % (config.skin.primary_skin.value)):
            self.list.append(_("restore skin.xml"))
        if os.path.exists(resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/EpgList.pyo.bak")):
            self.list.append(_("restore EpgList.pyo"))
        if os.path.exists(resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/MovieList.pyo.bak")):
            self.list.append(_("restore MovieList.pyo"))
        if os.path.exists(resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/ServiceList.pyo.bak")):
            self.list.append(_("restore ServiceList.pyo"))
        if os.path.exists("/etc/enigma2/skin_user.xml.bak"):
            self.list.append(_("restore skin_user.xml"))

        self.list.append(_("Save settings"))
        savedSettingsListWithPath = glob.glob("/tmp/*FontMagnifierSettings.xml")
        if len(savedSettingsListWithPath) > 0:
            self.list.append(_("Restore settings"))
            del savedSettingsList[:]
            for sFile in savedSettingsListWithPath:
                savedSettingsList.append(sFile.replace("/tmp/", ""))

        self.selection = ""

        if len(self.list) == 0:
            self.list.append(_("No files to restore!"))
            self["optionslist"] = MenuList(self.list)
            self.setTitle(_("Info..."))
        else:
            self["optionslist"] = MenuList(self.list)
            self.setTitle(_("restore options"))
 
    def cancel(self):
        self.close(False)

    def ok(self):
        self.selection = self["optionslist"].getCurrent()

        if self.selection == _("No files to restore!"):
            self.close(False)
        elif self.selection == _("Save settings"):
            self.saveSettings()
        elif self.selection == _("Restore settings"):
            self.restoreSettings()
        else:
            self.session.openWithCallback(self.restoringConfirmed, MessageBox, "%s ?" % self.selection)

    def restoringConfirmed(self, confirmed):
        if self.selection == _("restore skin.xml"):
            self.selection = "skin.xml"
        elif self.selection == _("restore EpgList.pyo"):
            self.selection = "EpgList.pyo"
        elif self.selection == _("restore MovieList.pyo"):
            self.selection = "MovieList.pyo"
        elif self.selection == _("restore ServiceList.pyo"):
            self.selection = "ServiceList.pyo"
        elif self.selection == _("restore skin_user.xml"):
            self.selection = "skin_user.xml"

        if not confirmed:
            messagebox_text = self.selection + _(" not restored.")
            confirmbox = self.session.open(MessageBox, messagebox_text, MessageBox.TYPE_INFO)
            confirmbox.setTitle(_("Info..."))
            self.close(False)
            return

        try:
            if self.selection == "skin.xml":
                Console().ePopen("mv -f /usr/share/enigma2/%s.bak /usr/share/enigma2/%s" % (config.skin.primary_skin.value, config.skin.primary_skin.value))            
            elif self.selection == "EpgList.pyo":
                Console().ePopen("mv -f %s %s") % (resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/EpgList.pyo.bak"), resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/EpgList.pyo"))
            elif self.selection == "MovieList.pyo":
                Console().ePopen("mv -f %s %s") % (resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/MovieList.pyo.bak"), resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/MovieList.pyo"))
            elif self.selection == "ServiceList.pyo":
                Console().ePopen("mv -f %s %s") % (resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/ServiceList.pyo.bak"), resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/ServiceList.pyo"))
            elif self.selection == "skin_user.xml":
                Console().ePopen("mv -f /etc/enigma2/skin_user.xml.bak /etc/enigma2/skin_user.xml")            

            messagebox_text = self.selection + _(" restored.")
            confirmbox = self.session.open(MessageBox, messagebox_text, MessageBox.TYPE_INFO)
        except:
            messagebox_text = self.selection + _(" not restored.")
            confirmbox = self.session.open(MessageBox, messagebox_text, MessageBox.TYPE_INFO)

        confirmbox.setTitle(_("Info..."))
        self.close(False)

    def saveSettings(self):
        list = []
        list.append('<?xml version="1.0" encoding="utf-8" ?>\n')
        list.append('<FontMagnifier-Settings>\n')
        list.append('\t<settings ')

        config.plugins.fm.regular_Font.setValue(regularFontList.value)

        for key, val in config.plugins.fm.dict().iteritems():
            if key != "regular_Font":
                list.append(key + '="' + str(val.getValue()) + '" ')
            else:
                list.append(key + '="' + str(val.value) + '" ')
        list.append('/>\n')
        list.append('</FontMagnifier-Settings>\n')

        lt = localtime()
        filename = "/tmp/"
        filename = filename + strftime("%Y-%m-%d_%H:%M:%S_FontMagnifierSettings.xml", lt)
        try:    
            file = open(filename, "w")
            for x in list:
                file.write(x)
            file.close()
            messagebox_text = _("Settins saved to ")
            messagebox_text = messagebox_text + filename
            confirmbox = self.session.open(MessageBox, messagebox_text, MessageBox.TYPE_INFO)
            confirmbox.setTitle(_("Info..."))
            self.close(False)
        except:
            messagebox_text = _("Saving settings failed!")
            confirmbox = self.session.open(MessageBox, messagebox_text, MessageBox.TYPE_ERROR)
            confirmbox.setTitle(_("Error..."))
            self.close(False)

    def restoreSettings(self):
        self.session.open(fmRestoreSettings)
        self.close(False)

class fmRestoreSettings(Screen):
    skin = """
        <screen name="fmRestoreScreen" position="center,center" size="600,130" zPosition="6" title="Restore Settings">
            <widget name="restorelist" position="10,5" zPosition="7" size="600,130" scrollbarMode="showOnDemand" transparent="1" />
        </screen>"""

    def __init__(self, session, args=0):
        Screen.__init__(self, session)

        self["setupActions"] = ActionMap(["SetupActions", "MenuActions"],
        {
            "cancel": self.cancel,
            "ok": self.ok,
        })

        self.list = []
        for sFile in savedSettingsList:
            self.list.append(sFile)
        
        self.selection = ""

        if len(self.list) == 0:
            self.list.append(_("No files to restore!"))
            self["restorelist"] = MenuList(self.list)
            self.setTitle(_("Info..."))
        else:
            self["restorelist"] = MenuList(self.list)
            self.setTitle(_("Please select settings to restore"))
 
    def cancel(self):
        self.close(False)

    def ok(self):
        self.selection = self["restorelist"].getCurrent()

        if self.selection == _("No files to restore!"):
            self.close(False)
        else:
            filename = "/tmp/" + self.selection
            file = open(filename, "r")
            data = file.read().decode("utf-8").replace('&', "&amp;").encode("ascii", 'xmlcharrefreplace')
            file.close()
            xmlAttributesToConfig_errors = False
            projectfiledom = xml.dom.minidom.parseString(data)
            for node in projectfiledom.childNodes[0].childNodes:
              if node.nodeType == xml.dom.minidom.Element.nodeType:
                if node.tagName == 'settings':
                    if self.xmlAttributesToConfig(node, config.plugins.fm) is False:
                        xmlAttributesToConfig_errors = True

            font_with_path="/usr/share/fonts/"+str(config.plugins.fm.regular_Font.value)
            if os.path.exists(font_with_path):
                regularFontList.setValue(str(config.plugins.fm.regular_Font.value))
            else:
                config.plugins.fm.regular_Font.setValue(regularFontList.value)

            if xmlAttributesToConfig_errors is False:
                messagebox_text = _("Saved settings restored!\n(%s)" % self.selection)
                confirmbox = self.session.open(MessageBox, messagebox_text, MessageBox.TYPE_INFO)
                confirmbox.setTitle(_("Info..."))
            else:
                messagebox_text = _("Saved settings restored with errors!\n(%s)" % self.selection)
                confirmbox = self.session.open(MessageBox, messagebox_text, MessageBox.TYPE_ERROR)
                confirmbox.setTitle(_("Error..."))
            self.close(False)

    def xmlAttributesToConfig(self, node, config):
        attribute_error_string=""
        XML_attribute_error_string=""
        try:
            i = 0
            while i < node.attributes.length:
                item = node.attributes.item(i)
                key = item.name.encode("utf-8")
                try:
                    val = eval(item.nodeValue)
                except (NameError, SyntaxError):
                    val = item.nodeValue.encode("utf-8")
                try:
                    config.dict()[key].setValue(val)
                except (KeyError):
                    attribute_error_string="Unknown attribute '%s'" % (key)
                    raise AttributeError
                i += 1
        except AttributeError:
            XML_attribute_error_string="Restore failed: XML attribute error '%s' / " % (node.toxml("utf-8"))
            messagebox_text = XML_attribute_error_string + attribute_error_string
            confirmbox = self.session.open(MessageBox, messagebox_text, MessageBox.TYPE_ERROR)
            confirmbox.setTitle(_("Error..."))
            return False
        return True

class fmWaitScreen(Screen):
    skin = """
        <screen name="fmWaitScreen" position="center,center" size="450,110" zPosition="1" title=" ">
            <ePixmap position="30,10" size="64,64" pixmap="%s" transparent="1" alphatest="blend" />
            <widget source="label" render="Label" position="130,25" size="350,50" font="Regular;32" transparent="1"  />
        </screen>""" % resolveFilename(SCOPE_PLUGINS, "Extensions/FontMagnifier/wait-icon.png")

    def __init__(self, session, skin_tree=None):
        Screen.__init__(self, session)

        self["label"] = StaticText("")
        self["label"].setText(_("Please wait..."))
        self.tree = skin_tree
        self.root = self.tree.getroot()
        self.list_of_screens = self.root.findall("screen")
        self.list_of_subtitles = self.root.findall("subtitles")
        self.list_of_fonts = self.root.findall("fonts")
        self.timer = eTimer()
        self.timer.callback.append(self.writeXml)
        self.timer.start(500, 1)

    def writeXml(self):
        global regularFontList
        try:
            if not os.path.exists("/etc/enigma2/skin_user.xml"):
                skin_user_xml_file = open("/etc/enigma2/skin_user.xml", "w")
                skin_user_xml_text = "<skin>\n"
                skin_user_xml_text = skin_user_xml_text + "</skin>\n"
                skin_user_xml_file.write(skin_user_xml_text)
                skin_user_xml_file.close()

            if not os.path.exists("/etc/enigma2/skin_user.xml.bak"):
                Console().ePopen("cp /etc/enigma2/skin_user.xml /etc/enigma2/skin_user.xml.bak")

            if config.plugins.fm.display_manipulation_active.value:
                if (not config.plugins.fm.active.value) and (not config.plugins.fm.show_only_clock.value):
                    if os.path.exists("/etc/enigma2/skin_user.xml.bak"):
                        Console().ePopen("mv /etc/enigma2/skin_user.xml.bak /etc/enigma2/skin_user.xml")
                    elif os.path.exists("/etc/enigma2/skin_user.xml"):
                        Console().ePopen("rm /etc/enigma2/skin_user.xml")
                else:
                    skin_user_xml_file = open("/etc/enigma2/skin_user.xml", "w")
                    skin_user_xml_text = "<skin>\n"
                    if config.plugins.fm.active.value:
                        if model == "dm800se":
                            skin_user_xml_text = skin_user_xml_text + "\t<screen name=\"InfoBarSummary\" position=\"0,0\" size=\"96,64\" id=\"2\">\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t<widget font=\"Regular;%s\" halign=\"center\" position=\"1,1\" render=\"Label\" size=\"92,64\" source=\"session.CurrentService\" valign=\"center\">\n" % (config.plugins.fm.fontsize.value)
                        else:
                            skin_user_xml_text = skin_user_xml_text + "\t<screen name=\"InfoBarSummary\" position=\"0,0\" size=\"132,64\">\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t<widget font=\"Regular;%s\" halign=\"center\" position=\"1,1\" render=\"Label\" size=\"128,64\" source=\"session.CurrentService\" valign=\"center\">\n" % (config.plugins.fm.fontsize.value)
                        skin_user_xml_text = skin_user_xml_text + "\t\t\t<convert type=\"ExtendedServiceInfo\">ServiceNumber</convert>\n"
                        skin_user_xml_text = skin_user_xml_text + "\t\t</widget>\n"
                        skin_user_xml_text = skin_user_xml_text + "\t</screen>\n"
                    if config.plugins.fm.show_only_clock.value:
                        if model == "dm800se":
                            skin_user_xml_text = skin_user_xml_text + "\t<screen name=\"StandbySummary\" position=\"0,0\" size=\"96,64\">\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t<widget font=\"Regular;40\" halign=\"center\" position=\"0,0\" render=\"Label\" size=\"96,64\" source=\"global.CurrentTime\" valign=\"center\">\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t\t<convert type=\"ClockToText\">Format:%H:%M</convert>\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t</widget>\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t<widget position=\"6,0\" render=\"FixedLabel\" size=\"84,64\" source=\"session.RecordState\" text=\" \" zPosition=\"1\">\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t\t<convert type=\"ConfigEntryTest\">config.usage.blinking_display_clock_during_recording,True,CheckSourceBoolean</convert>\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t\t<convert type=\"ConditionalShowHide\">Blink</convert>\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t</widget>\n"
                            skin_user_xml_text = skin_user_xml_text + "\t</screen>\n"
                        else:
                            skin_user_xml_text = skin_user_xml_text + "\t<screen name=\"StandbySummary\" position=\"0,0\" size=\"132,64\">\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t<widget font=\"Regular;44\" halign=\"center\" position=\"0,0\" render=\"Label\" size=\"132,64\" source=\"global.CurrentTime\" valign=\"center\">\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t\t<convert type=\"ClockToText\">Format:%H:%M</convert>\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t</widget>\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t<widget position=\"6,0\" render=\"FixedLabel\" size=\"120,64\" source=\"session.RecordState\" text=\" \" zPosition=\"1\">\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t\t<convert type=\"ConfigEntryTest\">config.usage.blinking_display_clock_during_recording,True,CheckSourceBoolean</convert>\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t\t<convert type=\"ConditionalShowHide\">Blink</convert>\n"
                            skin_user_xml_text = skin_user_xml_text + "\t\t</widget>\n"
                            skin_user_xml_text = skin_user_xml_text + "\t</screen>\n"

                    skin_user_xml_text = skin_user_xml_text + "</skin>\n"
                    skin_user_xml_file.write(skin_user_xml_text)
                    skin_user_xml_file.close()
            else:
                if os.path.exists("/etc/enigma2/skin_user.xml.bak"):
                    Console().ePopen("mv /etc/enigma2/skin_user.xml.bak /etc/enigma2/skin_user.xml")
        except:
            self.session.openWithCallback(self.close, MessageBox, _("Sorry, unable modify skin_user.xml"), type=MessageBox.TYPE_INFO)

        if not os.path.exists("/usr/share/enigma2/%s.bak" % (config.skin.primary_skin.value)):
            Console().ePopen("cp /usr/share/enigma2/%s /usr/share/enigma2/%s.bak" % (config.skin.primary_skin.value, config.skin.primary_skin.value))

        try:
            for element in self.list_of_screens:
                if element.keys():
                    for name, value in element.items():
                        if name == "name" and value == "EventView":
                            if element.getchildren():
                                for child in element:
                                    if child.get("name") == "epg_description":
                                        epg_description_font = child.get("font")
                                        font_elements = epg_description_font.split(";")
                                        if len(font_elements) == 2:
                                            new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.evv_fontsize.value)
                                            child.set("font", new_font)
                                            break
                        elif name == "name" and value == "EPGSelection":
                            tag_gefunden=0
                            if element.getchildren():
                                for child in element:
                                    if child.getchildren():
                                        for sub_child in child:
                                            if sub_child.tag == "convert":
                                                if sub_child.text == "ExtendedDescription":
                                                    tag_gefunden=1
                                                    break
                                        if tag_gefunden == 1:
                                            epg_description_font = child.get("font")
                                            font_elements = epg_description_font.split(";")
                                            if len(font_elements) == 2:
                                                new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.single_epg_description_fontsize.value)
                                                child.set("font", new_font)
                                                break
                        elif name == "name" and value == "ChannelSelection":
                            tag_gefunden=0
                            if element.getchildren():
                                for child in element:
                                    if (child.get("name") == "list"):
                                        service_name_font = child.get("serviceNameFont", "")
                                        service_info_font = child.get("serviceInfoFont", "")
                                        service_number_font = child.get("serviceNumberFont", "")

                                        font_elements = service_name_font.split(";")
                                        if len(font_elements) == 2:
                                            new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.channel_list_fontsize.value)
                                            if (config.plugins.fm.channel_list_fontsize.value != 0):
                                                child.set("serviceNameFont", new_font)

                                        font_elements = service_info_font.split(";")
                                        if len(font_elements) == 2:
                                            new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.channel_list_fontsize.value-2)
                                            if (config.plugins.fm.channel_list_fontsize.value != 0):
                                                child.set("serviceInfoFont", new_font)

                                        new_font = "%s" % (config.plugins.fm.channel_list_fontsize.value+6)
                                        if (config.plugins.fm.channel_list_fontsize.value != 0):
                                            child.set("serviceItemHeight", new_font)

                                        font_elements = service_number_font.split(";")
                                        if len(font_elements) == 2:
                                            new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.channel_list_fontsize.value)
                                            if (config.plugins.fm.channel_list_fontsize.value != 0):
                                                child.set("serviceNumberFont", new_font)

                                    if child.getchildren():
                                        for sub_child in child:
                                            if sub_child.tag == "convert":
                                                if sub_child.text == "ExtendedDescription":
                                                    tag_gefunden=1
                                                    break
                                        if tag_gefunden == 1:
                                            epg_description_font = child.get("font")
                                            font_elements = epg_description_font.split(";")
                                            if len(font_elements) == 2:
                                                new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.channel_list_epg_description_fontsize.value)
                                                if (config.plugins.fm.channel_list_epg_description_fontsize.value != 0):
                                                    child.set("font", new_font)
                        elif name == "name" and value == "InfoBar":
                            if element.getchildren():
                                children_modified=0
                                for child in element:
                                    if child.get("source") == "session.Event_Now":
                                        if child.getchildren():
                                            tag_gefunden=0
                                            for sub_child in child:
                                                if sub_child.tag == "convert":
                                                    if sub_child.text == "Name":
                                                        tag_gefunden=1
                                                        break
                                            if tag_gefunden == 1:
                                                infobar_event_next_font = child.get("font")
                                                font_elements = infobar_event_next_font.split(";")
                                                if len(font_elements) == 2:
                                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.infobar_fontsize_event_now.value)
                                                    if (config.plugins.fm.infobar_fontsize_event_now.value != 0):
                                                        child.set("font", new_font)
                                                        children_modified=children_modified+1
                                            tag_gefunden=0
                                            for sub_child in child:
                                                if sub_child.tag == "convert":
                                                    if sub_child.text == "StartTime":
                                                        tag_gefunden=1
                                                        break
                                            if tag_gefunden == 1:
                                                infobar_event_next_font = child.get("font")
                                                font_elements = infobar_event_next_font.split(";")
                                                if len(font_elements) == 2:
                                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.infobar_fontsize_event_now.value)
                                                    if (config.plugins.fm.infobar_fontsize_event_now.value != 0):
                                                        child.set("font", new_font)
                                                        children_modified=children_modified+1
                                            tag_gefunden=0
                                            for sub_child in child:
                                                if sub_child.tag == "convert":
                                                    if sub_child.text == "Remaining":
                                                        tag_gefunden=1
                                                        break
                                            if tag_gefunden == 1:
                                                infobar_event_next_font = child.get("font")
                                                font_elements = infobar_event_next_font.split(";")
                                                if len(font_elements) == 2:
                                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.infobar_fontsize_event_now.value)
                                                    if (config.plugins.fm.infobar_fontsize_event_now.value != 0):
                                                        child.set("font", new_font)
                                                        children_modified=children_modified+1
                                    elif child.get("source") == "session.Event_Next":
                                        if child.getchildren():
                                            tag2_gefunden=0
                                            for sub_child in child:
                                                if sub_child.tag == "convert":
                                                    if sub_child.text == "Name":
                                                        tag2_gefunden=1
                                                        break
                                            if tag2_gefunden == 1:
                                                infobar_event_next_font = child.get("font")
                                                font_elements = infobar_event_next_font.split(";")
                                                if len(font_elements) == 2:
                                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.infobar_fontsize_event_next.value)
                                                    if (config.plugins.fm.infobar_fontsize_event_next.value != 0):
                                                        child.set("font", new_font)
                                                        children_modified=children_modified+1
                                            tag2_gefunden=0
                                            for sub_child in child:
                                                if sub_child.tag == "convert":
                                                    if sub_child.text == "StartTime":
                                                        tag2_gefunden=1
                                                        break
                                            if tag2_gefunden == 1:
                                                infobar_event_next_font = child.get("font")
                                                font_elements = infobar_event_next_font.split(";")
                                                if len(font_elements) == 2:
                                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.infobar_fontsize_event_next.value)
                                                    if (config.plugins.fm.infobar_fontsize_event_next.value != 0):
                                                        child.set("font", new_font)
                                                        children_modified=children_modified+1
                                            tag2_gefunden=0
                                            for sub_child in child:
                                                if sub_child.tag == "convert":
                                                    if sub_child.text == "Duration":
                                                        tag2_gefunden=1
                                                        break
                                            if tag2_gefunden == 1:
                                                infobar_event_next_font = child.get("font")
                                                font_elements = infobar_event_next_font.split(";")
                                                if len(font_elements) == 2:
                                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.infobar_fontsize_event_next.value)
                                                    if (config.plugins.fm.infobar_fontsize_event_next.value != 0):
                                                        child.set("font", new_font)
                                                        children_modified=children_modified+1
                                    if children_modified==6:
                                        break

            if len(self.list_of_subtitles) != 0:
                for element in self.list_of_subtitles:
                    if element.getchildren():
                        for child in element:
                            if child.get("name") == "Subtitle_TTX":
                                font = child.get("font")
                                font_elements = font.split(";")
                                if len(font_elements)==2:
                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.Subtitle_TTX.value)
                                    if config.plugins.fm.Subtitle_TTX.value != 0:
                                        child.set("font", new_font)
                            elif child.get("name") == "Subtitle_Regular":
                                font = child.get("font")
                                font_elements = font.split(";")
                                if len(font_elements)==2:
                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.Subtitle_Regular.value)
                                    if config.plugins.fm.Subtitle_Regular.value != 0:
                                        child.set("font", new_font)
                            elif child.get("name") == "Subtitle_Bold":
                                font = child.get("font")
                                font_elements = font.split(";")
                                if len(font_elements)==2:
                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.Subtitle_Bold.value)
                                    if config.plugins.fm.Subtitle_Bold.value != 0:
                                        child.set("font", new_font)
                            elif child.get("name") == "Subtitle_Italic":
                                font = child.get("font")
                                font_elements = font.split(";")
                                if len(font_elements)==2:
                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.Subtitle_Italic.value)
                                    if config.plugins.fm.Subtitle_Italic.value != 0:
                                        child.set("font", new_font)

            if len(self.list_of_fonts) != 0:
                for element in self.list_of_fonts:
                    if element.getchildren():
                        for child in element:
                            if child.get("name") == "Regular":
                                child.set("filename", regularFontList.value)

            self.tree.write("/usr/share/enigma2/%s" % (config.skin.primary_skin.value))
        except:
            self.session.openWithCallback(self.close, MessageBox, _("Sorry, unable to parse /usr/share/enigma2/%s." % (config.skin.primary_skin.value)), type=MessageBox.TYPE_INFO)

        try:
            if config.plugins.fm.single_epg_list_fontsize.value != 0:
                EpgList_file = open(resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/EpgList.pyo"), "r")
                EpgList_text=EpgList_file.read()
                if EpgList_text.find("\t\tself.l.setItemHeight") is not -1:
                    item_height_gefunden = 1
                else:
                    item_height_gefunden = 0
                EpgList_file.close()

                EpgList_text_neu = ""
                EpgList_file = open(resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/EpgList.pyo"), "r")
                for zeile in EpgList_file:
                    if zeile.find("\t\tself.l.setFont(0") is not -1:
                        if item_height_gefunden == 0:
                            EpgList_text_neu = EpgList_text_neu + "\t\tself.l.setItemHeight(%d)\n" % (config.plugins.fm.single_epg_list_fontsize.value+5)
                        EpgList_text_neu = EpgList_text_neu + "\t\tself.l.setFont(0, gFont(\"Regular\", %d))\n" % (config.plugins.fm.single_epg_list_fontsize.value)
                    elif zeile.find("\t\tself.l.setFont(1") is not -1:
                        EpgList_text_neu = EpgList_text_neu + "\t\tself.l.setFont(1, gFont(\"Regular\", %d))\n" % (config.plugins.fm.single_epg_list_fontsize2.value)
                    elif zeile.find("\t\tself.l.setItemHeight") is not -1:
                        EpgList_text_neu = EpgList_text_neu + "\t\tself.l.setItemHeight(%d)\n" % (config.plugins.fm.single_epg_list_fontsize.value+5)
                    else:
                        EpgList_text_neu = EpgList_text_neu + zeile

                EpgList_file.close()

                if not os.path.exists(resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/EpgList.pyo.bak")):
                    Console().ePopen("cp %s %s") % (resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/EpgList.pyo"), resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/EpgList.pyo.bak"))

                EpgList_file = open(resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/EpgList.pyo"), "w")
                EpgList_file.write(EpgList_text_neu)
                EpgList_file.close()
        except:
            self.session.openWithCallback(self.close, MessageBox, _("Sorry, unable to parse EpgList.pyo"), type=MessageBox.TYPE_INFO)

        try:
            if config.plugins.fm.movie_list_fontsize.value != 0:
                MovieList_text_neu = ""
                MovieList_file = open(resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/MovieList.pyo"), "r")
                for zeile in MovieList_file:
                    if zeile.find("\t\tself.l.setFont(0") is not -1:
                        MovieList_text_neu = MovieList_text_neu + "\t\t\tself.l.setFont(0, gFont(\"Regular\", %d))\n" % (config.plugins.fm.movie_list_fontsize.value)
                    else:
                        MovieList_text_neu = MovieList_text_neu + zeile

                MovieList_file.close()

                if not os.path.exists(resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/MovieList.pyo.bak")):
                    Console().ePopen("cp %s %s") % (resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/MovieList.pyo"), resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/MovieList.pyo.bak"))


                MovieList_file = open(resolveFilename(SCOPE_LIBDIR, "enigma2/python/Components/MovieList.pyo"), "w")
                MovieList_file.write(MovieList_text_neu)
                MovieList_file.close()
        except:
            self.session.openWithCallback(self.close, MessageBox, _("Sorry, unable to parse MovieList.pyo"), type=MessageBox.TYPE_INFO)

        restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, _("GUI needs a restart to apply a new settings\nDo you want to Restart the GUI now?"), MessageBox.TYPE_YESNO)
        restartbox.setTitle(_("Restart GUI now?"))

    def restartGUI(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()
