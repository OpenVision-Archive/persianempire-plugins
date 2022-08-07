# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Button import Button
from Components.Label import Label
from Components.Language import language
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigList, ConfigListScreen
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from Components.MenuList import MenuList
from urllib2 import Request, urlopen
from xml.dom import minidom
from enigma import loadPic, eTimer, ePoint, getDesktop, ePixmap, eActionMap
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.config import config, configfile, ConfigInteger, ConfigSubsection, ConfigYesNo, getConfigListEntry, ConfigSelection
from os import environ as os_environ
import gettext
from Screens.InfoBarGenerics import InfoBarPlugins
from Screens.InfoBar import InfoBar
from time import localtime, strftime
import os
import re
import time
from keyids import KEYIDS
import xml.parsers.expat
import urllib2
from Components.Console import Console

shortMONTHS = (_("Jan"),
               _("Feb"),
               _("Mar"),
               _("Apr"),
               _("May"),
               _("Jun"),
               _("Jul"),
               _("Aug"),
               _("Sep"),
               _("Oct"),
               _("Nov"),
               _("Dec"))

shortMONTHSRU = (_("Янв."),
               _("Фев."),
               _("Мрт."),
               _("Апр."),
               _("Май"),
               _("Июнь"),
               _("Июль"),
               _("Авг."),
               _("Сент."),
               _("Окт."),
               _("Нояб."),
               _("Дек."))

WeatherInfoBarKeys = [
	["Red", _("RED"), ["KEY_RED"]],
	["Green", _("GREEN"), ["KEY_GREEN"]],
	["Yellow", _("YELLOW"), ["KEY_YELLOW"]],
	["Radio", _("RADIO"), ["KEY_RADIO"]],
	["Text", _("TEXT"), ["KEY_TEXT"]],
	["Tv", _("TV"), ["KEY_TV"]],
	["Help", _("HELP"), ["KEY_HELP"]],
]

UserAgent = "Mozilla/5.0 (X11; U; Linux x86_64; de; rv:1.9.0.15) Gecko/2009102815 Ubuntu/9.04 (jaunty) Firefox/3."
global pluginpath
global showTimer
pluginpath = resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/weathericons")
windpath = resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/windicons")
maintext = ""
InfoBarShow = None
InfoBarHide = None
gInfoBarWeather__init__ = None
StartOnlyOneTime = False
OnlyOneTime = False
gInfoBarWeather = None
baseInfoBar__init__ = None
config.plugins.WeatherPlugin = ConfigSubsection()
config.plugins.WeatherPlugin.enabled = ConfigYesNo(default=True)
config.plugins.WeatherPlugin.usebutton = ConfigYesNo(default=False)
config.plugins.WeatherPlugin.clock = ConfigSelection(default="2", choices=[("0", _("Weather time")), ("1", _("clock")), ("2", _("clock+day")), ("3", _("updates time"))])
config.plugins.WeatherPlugin.city = ConfigSelection(default="1", choices=[("0", _("Weather xml")), ("1", _("Config file"))])
config.plugins.WeatherPlugin.caches = ConfigYesNo(default=True)
config.plugins.WeatherPlugin.anim = ConfigSelection(default="0", choices=[("0", _("Static Icons")), ("1", _("Icons+animation")), ("2", _("Animated icons"))])
config.plugins.WeatherPlugin.anim2 = ConfigYesNo(default=False)
config.plugins.WeatherPlugin.position_x = ConfigInteger(default=33)
config.plugins.WeatherPlugin.position_y = ConfigInteger(default=52)
config.plugins.WeatherPlugin.timeout = ConfigInteger(60, (30, 150))
config.plugins.WeatherPlugin.wind = ConfigSelection(default="0", choices=[("0", _("Kmph")), ("1", _("m/s"))])
config.plugins.WeatherPlugin.language = ConfigSelection(default="1", choices=[("0", _("Russian")), ("1", _("English"))])
config.plugins.WeatherPlugin.hotkey = ConfigSelection([(x[0], x[1]) for x in WeatherInfoBarKeys], "Help")
config.plugins.WeatherPlugin.anim3 = ConfigSelection(default="/media/hdd/AnimatedIcons", choices=[("/media/hdd/AnimatedIcons", _("/media/hdd/")), ("/media/usb/AnimatedIcons", _("/media/usb/")), ("/usr/share/enigma2/AnimatedIcons", _("/usr/share/enigma2/"))])
config.plugins.WeatherPlugin.days = ConfigSelection(default="0", choices=[("0", _("Three day")), ("1", _("One day"))])


def localeInit():
    lang = language.getLanguage()[:2]
    os_environ["LANGUAGE"] = lang
    gettext.bindtextdomain("QuickWeather", resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/locale"))


def _(txt):
    t = gettext.dgettext("QuickWeather", txt)
    if t == txt:
        print("[QuickWeather] fallback to default translation for", txt)
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)


def WeatherInfoBar__init__(self, session):
	baseInfoBar__init__(self, session)
	self.Weatherinfobar = WeatherInfoBar(session, self)


def main(session, **kwargs):
	session.open(WeatherPluginMenu)


def sessionstart(reason, **kwargs):
	global gInfoBarWeather__init__
	if "session" in kwargs:
            if config.plugins.WeatherPlugin.enabled.value and config.plugins.WeatherPlugin.usebutton.value == False:
		if gInfoBarWeather__init__ is None:
			gInfoBarWeather__init__ = InfoBarPlugins.__init__
		InfoBarPlugins.__init__ = InfoBarPlugins__init__
		InfoBarPlugins.switch = switch
		InfoBarPlugins.swOff = swOff


def InfoBarPlugins__init__(self):
	global OnlyOneTime
	if not OnlyOneTime:
		OnlyOneTime = True
                self["WeatherActions"] = ActionMap(["WeatherActions"], {"ok_but": self.switch, "exit_but": self.swOff}, -1)
		self.Weathertimer = eTimer()
		self.Weathertimer.callback.append(self.swOff)
		self.Weatherdialog = self.session.instantiateDialog(WeatherPluginScreen)
		if config.plugins.WeatherPlugin.enabled.value:
			self.onHide.append(lambda: self.Weatherdialog.hide())
			self.onShow.append(lambda: self.Weatherdialog.show())

		def CheckWeathertimer():
			if self.Weathertimer.isActive():
				self.Weathertimer.stop()
		self.Weatherdialog.onHide.append(CheckWeathertimer)
	else:
		InfoBarPlugins.__init__ = InfoBarPlugins.__init__
		InfoBarPlugins.switch = None
		InfoBarPlugins.swOff = None
	gInfoBarWeather__init__(self)


def switch(self):
        global StartOnlyOneTime
	if isinstance(self, InfoBar):
		if config.plugins.WeatherPlugin.enabled.value:
			if not self.shown and not self.Weatherdialog.shown:
				self.toggleShow()
			elif self.shown and not self.Weatherdialog.shown:
                            if not StartOnlyOneTime:
                                StartOnlyOneTime = True
				self.Weatherdialog.show()
				idx = config.usage.infobar_timeout.index
				if (idx > 0):
					self.Weathertimer.start(idx * 1000, True)
			elif not self.shown and self.Weatherdialog.shown:
				self.Weatherdialog.hide()
				self.toggleShow()
			elif self.shown and self.Weatherdialog.shown:
				self.Weatherdialog.hide()
				self.toggleShow()

			else:
				self.toggleShow()


def swOff(self):
	if isinstance(self, InfoBar):
                if (self.shown and self.Weatherdialog.shown):
			self.Weatherdialog.hide()
		else:
			self.Weatherdialog.hide()
			self.hide()


def autostart(reason, **kwargs):
	if reason == 0:
            if config.plugins.WeatherPlugin.enabled.value and config.plugins.WeatherPlugin.usebutton.value == True:
		global baseInfoBar__init__
		if baseInfoBar__init__ is None:
			baseInfoBar__init__ = InfoBar.__init__
		InfoBar.__init__ = WeatherInfoBar__init__


def Plugins(**kwargs):
        return [
             PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart),
             PluginDescriptor(where=[PluginDescriptor.WHERE_AUTOSTART], fnc=autostart),
	     PluginDescriptor(name=_("Quick Weather"), description=_("Special version for Open Vision"), where=[PluginDescriptor.WHERE_PLUGINMENU], icon="icon-fs8.png", fnc=main)]


HDSkn = False


class WeatherPluginScreen2(Screen):
	skin = """
	    <screen position="center,center" size="230,245" zPosition="3" backgroundColor="#ff000000" flags="wfNoBorder">
            <widget name="zastavka" position="0,0" size="230,245" zPosition="2" transparent="1" alphatest="on" />
            <widget name="lab1" position="24,25" halign="center" size="180,20" zPosition="4" font="Regular;20" foregroundColor="#00ffcc33" backgroundColor="#30000000" valign="top" transparent="1" />
            <widget name="City" position="24,48" halign="center" size="180,18" zPosition="4" font="Regular;16" foregroundColor="#00ffcc33" backgroundColor="#30000000" valign="top" transparent="1" />
            <widget name="Icons now" position="67,66" size="138,95" zPosition="3" transparent="1" alphatest="on" />
            <widget name="Wind icons" position="24,106" size="50,50" zPosition="3" transparent="1" alphatest="on" />
            <widget name="Temp now" position="24,77" halign="left" size="80,30" zPosition="4" font="Regular;27" valign="top" backgroundColor="#00000000" transparent="1" />
            <widget name="Description now" position="24,150" halign="center" size="180,80" zPosition="4" font="Regular;18" valign="top" backgroundColor="#00000000" transparent="1" />
	    </screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self["lab1"] = Label(_("Started"))
		self["City"] = Label(_("Connection..."))
		self["zastavka"] = Pixmap()
		self["Icons now"] = Pixmap()
		self["Wind icons"] = Pixmap()
		self["Temp now"] = Label("")
		self["Description now"] = Label("")


class WeatherPluginScreen(Screen):
	skin = """
	    <screen position="center,center" size="230,415" zPosition="3" backgroundColor="#ff000000" flags="wfNoBorder">
            <widget name="zastavka" position="0,0" size="230,415" zPosition="2" transparent="1" alphatest="on" />
            <widget name="lab1" position="24,25" halign="center" size="180,20" zPosition="4" font="Regular;20" foregroundColor="#00ffcc33" backgroundColor="#30000000" valign="top" transparent="1" />
            <widget name="City" position="24,48" halign="center" size="180,18" zPosition="4" font="Regular;16" foregroundColor="#00ffcc33" backgroundColor="#30000000" valign="top" transparent="1" />
            <widget name="Icons now" position="67,66" size="138,95" zPosition="3" transparent="1" alphatest="on" />
            <widget name="Wind icons" position="24,106" size="50,50" zPosition="3" transparent="1" alphatest="on" />
            <widget name="Temp now" position="24,77" halign="left" size="80,30" zPosition="4" font="Regular;27" valign="top" backgroundColor="#00000000" transparent="1" />
            <widget name="Description now" position="24,150" halign="center" size="180,80" zPosition="4" font="Regular;18" valign="top" backgroundColor="#00000000" transparent="1" />
            <widget name="Date of tomorrow" position="24,229" halign="center" size="180,20" zPosition="4" foregroundColor="#00ffcc33" backgroundColor="#30000000" font="Regular;20" valign="top" transparent="1" />
            <widget name="Icons tomorrow" position="117,260" size="87,60" zPosition="3" transparent="1" alphatest="on" />
            <widget name="Description tomorrow" position="24,252" halign="left" size="180,60" zPosition="4" font="Regular;16" valign="top" backgroundColor="#00000000" transparent="1" />
            <widget name="day after tomorrow" position="24,312" halign="center" size="180,20" zPosition="4" foregroundColor="#00ffcc33" backgroundColor="#30000000" font="Regular;20" valign="top" transparent="1" />
            <widget name="Icons2" position="117,340" size="87,60" zPosition="3" transparent="1" alphatest="on" />
            <widget name="Description2" position="24,333" halign="left" size="180,60" zPosition="4" font="Regular;16" valign="top" backgroundColor="#00000000" transparent="1" />
	    </screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
 		if config.plugins.WeatherPlugin.days.value == "0":
		     self.skin = WeatherPluginScreen.skin
 		if config.plugins.WeatherPlugin.days.value == "1":
		     self.skin = WeatherPluginScreen2.skin
                global showTimer
		self["lab1"] = Label(_("Started"))
		self["City"] = Label(_("Connection..."))
		self["zastavka"] = Pixmap()
		self["Icons now"] = Pixmap()
		self["Wind icons"] = Pixmap()
		self["Temp now"] = Label("")
		self["Description now"] = Label("")
		self["Date of tomorrow"] = Label("")
		self["Icons tomorrow"] = Pixmap()
		self["Description tomorrow"] = Label("")
		self["day after tomorrow"] = Label("")
		self["Icons2"] = Pixmap()
		self["Description2"] = Label("")
		self["lab12"] = Label("")
		self["lab13"] = Pixmap()
		self["lab14"] = Label("")
		self.timer = eTimer()
		self.activityTimer = eTimer()
		showTimer = self.activityTimer
		self.activityTimer.timeout.get().append(self.startConnection)
		self.onShow.append(self.movePosition)
		self.onClose.append(self.delTimer)
	        self.showTimer = eTimer()
		self.showTimer.callback.append(self.delTimer)
		self.showTimer.start(50, 1)
		self.previousflag = None
		if config.plugins.WeatherPlugin.usebutton.value == True:

                         self["actions"] = ActionMap(["OkCancelActions"],
		         {
			         "ok": self.exit,
			         "cancel": self.exit,
		         }, -1)

	def exit(self):
		self.close()

	def movePosition(self):
		if self.instance:
			self.instance.move(ePoint(config.plugins.WeatherPlugin.position_x.value, config.plugins.WeatherPlugin.position_y.value))
                if config.plugins.WeatherPlugin.enabled.value:
		        self.activityTimer.start(10)
		else:
                        self.activityTimer.stop()

	def startConnection(self):
                if config.plugins.WeatherPlugin.usebutton.value == False:
                    if self.activityTimer.isActive():
		        self.activityTimer.stop()
		else:
                    self.activityTimer.stop()
		if config.plugins.WeatherPlugin.enabled.value == True:
		     self["lab1"].setText("Connession...")
		     self.updateInfo()
		     if config.plugins.WeatherPlugin.usebutton.value == False:
		          self.activityTimer.start(int(config.plugins.WeatherPlugin.timeout.value) * 60000)
	        else:
                     self.delTimer()

	def updateInfo(self):
                maintext = ""
                controlldom = 1
                RESET_TIME = int(config.plugins.WeatherPlugin.timeout.value)
		myurl = self.get_Url()
		if not fileExists("/tmp/indbweather.xml"):
		      Console().ePopen("wget -P /tmp -T2 '%s' -O /tmp/indbweather.xml" % myurl)
		if fileExists("/tmp/indbweather.xml"):
                        if int((time.time() - os.stat("/tmp/indbweather.xml").st_mtime) / 60) >= RESET_TIME:
                            Console().ePopen("rm -f /tmp/indbweather.xml")
                            Console().ePopen("wget -P /tmp -T2 '%s' -O /tmp/indbweather.xml" % myurl)
                        if fileExists("/tmp/indbweather.xml"):
			    handler = open("/tmp/indbweather.xml")
			    xml_response = handler.read().encode('utf-8')
			    handler.close()
			else:
                            xml_response = '<data><error><msg>Unable to find any matching weather location to the query submitted!</msg></error></data>'
			if (xml_response == ''):
			    self.resetLabels2()
			    if config.plugins.WeatherPlugin.anim.value == "2":
                                id = "NA"
                                self.runiconanim(id)
			    maintext = "Error getting XML document!"
		            decode = '<data><error><msg>Unable to find any matching weather location to the query submitted!</msg></error></data>'
                            temp_file = open("/tmp/indbweather.xml", 'w')
                            temp_file.write(decode)
                            temp_file.close()
			else:
			    content_results = xml_response[xml_response.find('<error>'):xml_response.find('</error>')]
     			    if content_results:
                                self.resetLabels2()
                                maintext = "Error getting XML document!"
			        if config.plugins.WeatherPlugin.anim.value == "2":
                                    id = "NA"
                                    self.runiconanim(id)
                                self["City"].setText(_("Invalid city"))
                            else:
                                try:
   			            dom = minidom.parseString(xml_response)
   			        except xml.parsers.expat.ExpatError:
                                    controlldom = 0
                                    self.resetLabels2()
			            if config.plugins.WeatherPlugin.anim.value == "2":
                                        id = "NA"
                                        self.runiconanim(id)
                                    self["City"].setText(_("Invalid city"))
			        maintext = ""
			        tmptext = ""
			        tmptext3 = ""
			        tmptext4 = ""
			        tmptext5 = ""
			        maintext1 = ""
			        tmptext2 = 0
			        if controlldom != 0:
				    weather_data = {}
    				    weather_dom = dom.getElementsByTagName('data')[0]
    				    data_structure = {
        				    'request': ('query', 'type'),
        				    'current_condition': ('weatherDesc', 'temp_C', 'humidity', 'windspeedKmph', 'winddir16Point', 'weatherIconUrl', 'observation_time')
    				    }
    				    for (tag, list_of_tags2) in data_structure.iteritems():
        				    tmp_conditions = {}
       					    for tag2 in list_of_tags2:
            					    try:
                					tmp_conditions[tag2] = weather_dom.getElementsByTagName(tag)[0].getElementsByTagName(tag2)[0].firstChild.wholeText
            					    except IndexError:
                					pass
        				    weather_data[tag] = tmp_conditions
    				    weather = ('date', 'tempMinC', 'tempMaxC', 'weatherIconUrl', 'weatherDesc')
    				    forecasts = []
				    for forecast in dom.getElementsByTagName('weather'):
        				    tmp_forecast = {}
        				    for tag in weather:
            					tmp_forecast[tag] = forecast.getElementsByTagName(tag)[0].firstChild.wholeText
        				    forecasts.append(tmp_forecast)
    				    weather_data['forecasts'] = forecasts
    				    dom.unlink()
				    if fileExists("/tmp/indbweather.xml"):
				          maintext1 = time.localtime(os.stat("/tmp/indbweather.xml").st_mtime)
				          maintext = strftime("%b %H:%M", maintext1)
				          maintext = "%s" % (maintext)
				    else:
                                          maintext = str(weather_data['current_condition']['observation_time'])
				    mytime = str(weather_data['request']['query'])
			            mytime3 = str(weather_data['current_condition']['temp_C'])
				    mytime2 = str(weather_data['current_condition']['humidity'])
				    if config.plugins.WeatherPlugin.city.value == "0":
				         self["City"].setText("" + mytime)
				    if config.plugins.WeatherPlugin.city.value == "1":
				         if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/city.cfg')):
                            		    f = open(resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/city.cfg'), 'r')
			                    line = f.readline()
			                    text = line.strip()
			                    f.close()
			                    self["City"].setText("" + text)
		                         else:
                                            self["City"].setText("" + mytime)
				    myicon = self.checkIcon(str(weather_data['current_condition']['weatherIconUrl']))
				    global png2
				    png2 = loadPic(myicon, 138, 95, 0, 0, 0, 1)
				    if config.plugins.WeatherPlugin.anim.value == "1":
                                        self.runanim()
                                    if config.plugins.WeatherPlugin.anim.value == "0":
				        self["Icons now"].instance.setPixmap(png2)
				    if config.plugins.WeatherPlugin.anim.value == "2":
                                        myicon2 = self.checkIconanim(str(weather_data['current_condition']['weatherIconUrl']))
                                        id = myicon2
                                        self.runiconanim(id)
				    self["Temp now"].setText(mytime3 + " °C")
				    if config.plugins.WeatherPlugin.wind.value == "0":
				         tmptext2 = int(weather_data['current_condition']['windspeedKmph'])
				         tmptext4 = self.eXtendedDay(" Kmph")
				    if config.plugins.WeatherPlugin.wind.value == "1":
                                         tmptext2 = int(weather_data['current_condition']['windspeedKmph']) * 1000 / 3600
                                         tmptext4 = self.eXtendedDay(" m/s")
				    tmptext3 = '%s' % (tmptext2)
				    tmptext5 = str(weather_data['current_condition']['winddir16Point'])
				    tmptext = self.eXtendedDay(str(weather_data['current_condition']['weatherDesc'])) + "   " + self.eXtendedDay("Humidity: ") + mytime2 + "   " + self.eXtendedDay("Wind: ") + self.Wind(tmptext5) + "   " + tmptext3 + tmptext4
				    self["Description now"].setText(tmptext)
				    windicon = self.checkWindIcon(tmptext5)
			            png6 = loadPic(windicon, 50, 50, 0, 0, 0, 1)
			            self["Wind icons"].instance.setPixmap(png6)
				    tmptext = str(weather_data['forecasts'][1]['date'])
				    self["Date of tomorrow"].setText(tmptext)
				    myicon = self.checkIcon(str(weather_data['forecasts'][1]['weatherIconUrl']))
				    global png1
				    png1 = loadPic(myicon, 87, 60, 0, 0, 0, 1)
				    if config.plugins.WeatherPlugin.anim2.value:
                                        self.runanim1()
                                    else:
				        self["Icons tomorrow"].instance.setPixmap(png1)
				    tmptext = self.eXtendedDay(str(weather_data['forecasts'][1]['weatherDesc'])) + self.eXtendedDay("\nMin °C: ") + str(weather_data['forecasts'][1]['tempMinC']) + self.eXtendedDay("\nMax °C: ") + str(weather_data['forecasts'][1]['tempMaxC'])
				    self["Description tomorrow"].setText(tmptext)
				    tmptext = str(weather_data['forecasts'][2]['date'])
				    self["day after tomorrow"].setText(tmptext)
				    myicon = self.checkIcon(str(weather_data['forecasts'][2]['weatherIconUrl']))
				    global png3
				    png3 = loadPic(myicon, 87, 60, 0, 0, 0, 1)
				    if config.plugins.WeatherPlugin.anim2.value:
                                        self.runanim2()
                                    else:
				         self["Icons2"].instance.setPixmap(png3)
				    tmptext = self.eXtendedDay(str(weather_data['forecasts'][2]['weatherDesc'])) + self.eXtendedDay("\nMin °C: ") + str(weather_data['forecasts'][2]['tempMinC']) + self.eXtendedDay("\nMax °C: ") + str(weather_data['forecasts'][2]['tempMaxC'])
				    self["Description2"].setText(tmptext)
				    tmptext = str(weather_data['forecasts'][3]['date'])
				    self["lab12"].setText(tmptext)
				    myicon = self.checkIcon(str(weather_data['forecasts'][3]['weatherIconUrl']))
				    png = loadPic(myicon, 87, 60, 0, 0, 0, 1)
				    self["lab13"].instance.setPixmap(png)
				    tmptext = self.eXtendedDay(str(weather_data['forecasts'][3]['weatherDesc'])) + "\nMin °C: " + str(weather_data['forecasts'][3]['tempMinC']) + "\nMax °C: " + str(weather_data['forecasts'][3]['tempMaxC'])
				    self["lab14"].setText(tmptext)
				    if config.plugins.WeatherPlugin.caches.value == True:
				            Console().ePopen("echo 1 > /proc/sys/vm/drop_caches")
		else:
			    maintext = "Error getting XML document!"
			    self.resetLabels2()
			    if config.plugins.WeatherPlugin.anim.value == "2":
                                id = "NA"
                                self.runiconanim(id)
		            decode = '<data><error><msg>Unable to find any matching weather location to the query submitted!</msg></error></data>'
                            temp_file = open("/tmp/indbweather.xml", 'w')
                            temp_file.write(decode)
                            temp_file.close()
                if config.plugins.WeatherPlugin.clock.value == "0":
		    self["lab1"].setText(maintext)
		if config.plugins.WeatherPlugin.clock.value == "1":
                    tm = localtime()
                    name = strftime("%H:%M", tm)
                    self["lab1"].setText(name)
                    self.timer.startLongTimer(60 - tm.tm_sec)
		if config.plugins.WeatherPlugin.clock.value == "2":
                    tm = localtime()
                    if config.plugins.WeatherPlugin.language.value == "0":
                        name = str(tm[2]) + " " + shortMONTHSRU[tm[1] - 1] + " " + strftime("%H:%M", tm)
                    else:
                        name = str(tm[2]) + " " + shortMONTHS[tm[1] - 1] + " " + strftime("%H:%M", tm)
                    self["lab1"].setText(name)
                    self.timer.startLongTimer(60 - tm.tm_sec)
                if config.plugins.WeatherPlugin.clock.value == "3":
                    maintext2 = 0
                    maintext2 = int((time.time() - os.stat("/tmp/indbweather.xml").st_mtime) / 60)
                    maintext = int(config.plugins.WeatherPlugin.timeout.value) - maintext2
                    maintext1 = _("Before update:")
                    maintext = "%s %s min" % (maintext1, maintext)
		    self["lab1"].setText(maintext)
 		if config.plugins.WeatherPlugin.days.value == "0":
		    self["zastavka"].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/backg.png"))
 		if config.plugins.WeatherPlugin.days.value == "1":
                    self["zastavka"].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/backg2.png"))

        def CrewRoleList(self, file):
                if file:
                     return file.replace('		', '').replace('			', '').replace('				', '').replace('\n', '').replace('\t', '')

	def checkIconanim(self, filename):
                localfile = ""
		parts = filename.split("/")
		totsp = (len(parts) - 1)
		localfile = parts[totsp].replace('.png', '')
		return localfile

	def checkIconUA(self, filename):
                localfile = ""
		parts = '%s' % filename
		localfile = pluginpath + "/" + parts
		return localfile

	def checkWindIcon(self, filename):
                localfile = ""
		parts = '%s.png' % filename
		localfile = windpath + "/" + parts
		return localfile

        def runiconanim(self, id):
            global png2, total
            animokicon = False
            if fileExists('%s/%s' % (config.plugins.WeatherPlugin.anim3.value, id)):
                pathanimicon = '%s/%s/a' % (config.plugins.WeatherPlugin.anim3.value, id)
                path = '%s/%s' % (config.plugins.WeatherPlugin.anim3.value, id)
                dir_work = os.listdir(path)
                total = len(dir_work)
                self.slideicon = total
                animokicon = True
            else:
                pathanimicon = resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/NA/a')
                path = resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/NA')
                dir_work = os.listdir(path)
                total = len(dir_work)
                self.slideicon = total
                animokicon = True
            if (animokicon == True):
                self.picsicon = []
                for x in range(self.slideicon):
                    self.picsicon.append(LoadPixmap(((pathanimicon + str(x)) + '.png')))
                self.timericon = eTimer()
                self.timericon.callback.append(self.timerEventicon)
                self.timericon.start(100, True)
            else:
                self["Icons now"].instance.setPixmap(png2)

        def timerEventicon(self):
                global total
                global png2
                if config.plugins.WeatherPlugin.anim.value == "2":
                    if (self.slideicon == 0):
                        self.slideicon = total
                    self.timericon.stop()
                    self["Icons now"].instance.setPixmap(self.picsicon[(self.slideicon - 1)])
                    self.slideicon = (self.slideicon - 1)
                    self.timericon.start(100, True)
                else:
                    self.timericon.stop()

        def runanim(self):
            global png2
            self.slide = 8
            animok2 = False
            if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/anim/a7.png')):
                pathanim = resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/anim/a')
                animok2 = True
            if (animok2 == True):
                self.pics = []
                for x in range(self.slide):
                    self.pics.append(LoadPixmap(((pathanim + str(x)) + '.png')))
                self.timer = eTimer()
                self.timer.callback.append(self.timerEvent)
                self.timer.start(70, True)
            else:
                self["Icons now"].instance.setPixmap(png2)

        def timerEvent(self):
            global png2
            if (self.slide != 0):
                self.timer.stop()
                self["Icons now"].instance.setPixmap(self.pics[(self.slide - 1)])
                self.slide = (self.slide - 1)
                self.timer.start(70, True)
            else:
                self.timer.stop()
                self["Icons now"].instance.setPixmap(png2)

        def runanim1(self):
            global png1
            self.slide1 = 8
            animok = False
            if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/anim/n7.png')):
                pathanim1 = resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/anim/n')
                animok = True
            if (animok == True):
                self.pics1 = []
                for x in range(self.slide1):
                    self.pics1.append(LoadPixmap(((pathanim1 + str(x)) + '.png')))
                self.timer1 = eTimer()
                self.timer1.callback.append(self.timerEvent1)
                self.timer1.start(70, True)
            else:
                self["Icons tomorrow"].instance.setPixmap(png1)

        def timerEvent1(self):
            global png1
            if (self.slide1 != 0):
                self.timer1.stop()
                self["Icons tomorrow"].instance.setPixmap(self.pics1[(self.slide1 - 1)])
                self.slide1 = (self.slide1 - 1)
                self.timer1.start(70, True)
            else:
                self.timer1.stop()
                self["Icons tomorrow"].instance.setPixmap(png1)

        def runanim2(self):
            global png3
            self.slide3 = 8
            animok = False
            if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/anim/n7.png')):
                pathanim3 = resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/anim/n')
                animok = True
            if (animok == True):
                self.pics3 = []
                for x in range(self.slide3):
                    self.pics3.append(LoadPixmap(((pathanim3 + str(x)) + '.png')))
                self.timer3 = eTimer()
                self.timer3.callback.append(self.timerEvent2)
                self.timer3.start(70, True)
            else:
                self["Icons2"].instance.setPixmap(png3)

        def timerEvent2(self):
            global png3
            if (self.slide3 != 0):
                self.timer3.stop()
                self["Icons2"].instance.setPixmap(self.pics3[(self.slide3 - 1)])
                self.slide3 = (self.slide3 - 1)
                self.timer3.start(70, True)
            else:
                self.timer3.stop()
                self["Icons2"].instance.setPixmap(png3)

	def get_Url(self):
		url = 'http://api.worldweatheronline.com/free/v1/weather.ashx?q='
		text = "Kiev"
                if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/weatherindb.cfg')):
		       cfgfile = resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/weatherindb.cfg")
		else:
                       cfgfile = "/etc/weatherindb.cfg"
		if fileExists(cfgfile):
			f = open(cfgfile, 'r')
			line = f.readline()
			text = line.strip()
			f.close()
		else:
                        text = "Kiev"
		url = url + text + "&format=xml&num_of_days=5&key=9mujy42c6ptawhunprq7yvps"
		url = url.replace(' ', '%20')
		return url

	def resetLabels2(self):
		self["lab1"].setText(_("Error getting XML document!"))
		self["City"].setText(_("Connection failed!"))
		self["Wind icons"].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/windicons/none.png"))
                if config.plugins.WeatherPlugin.anim.value != "2":
		    self["Icons now"].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/NA.png"))
		self["Temp now"].setText("")
		self["Description now"].setText(_("Page not available!"))
		self["Date of tomorrow"].setText(_("None"))
		self["day after tomorrow"].setText(_("None"))
		self["Description2"].setText(_("None"))
		self["lab12"].setText("")
		self["lab14"].setText("")
		self["Icons tomorrow"].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/na2.png"))
		self["Description tomorrow"].setText("")
		self["Icons2"].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/na2.png"))
		self["lab13"].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/na2.png"))

	def checkIcon(self, filename):
		parts = filename.split("/")
		totsp = (len(parts) - 1)
		localfile = pluginpath + "/" + parts[totsp]
		if fileExists(localfile):
			pass
		else:
			url = filename
			handler = urlopen(url)
			if (handler):
				content = handler.read()
				fileout = open(localfile, "wb")
				fileout.write(content)
    				handler.close()
				fileout.close()
		return localfile

	def Wind(self, day):
                if config.plugins.WeatherPlugin.language.value == "0":
		     if (day == 'W'):
			     day1 = "З"
		     elif (day == 'WNW'):
			     day1 = "ЗСЗ"
		     elif (day == 'NW'):
			     day1 = "СЗ"
		     elif (day == 'NNW'):
			     day1 = "ССЗ"
		     elif (day == 'N'):
			     day1 = "С"
		     elif (day == 'NNE'):
			     day1 = "ССВ"
		     elif (day == 'NE'):
			     day1 = "СВ"
		     elif (day == 'ENE'):
			     day1 = "ВСВ"
		     elif (day == 'E'):
			     day1 = "В"
		     elif (day == 'ESE'):
			     day1 = "ВЮВ"
		     elif (day == 'SE'):
			     day1 = "ЮВ"
		     elif (day == 'SSE'):
			     day1 = "ЮЮВ"
		     elif (day == 'S'):
			     day1 = "Ю"
		     elif (day == 'SSW'):
			     day1 = "ЮЮЗ"
		     elif (day == 'SW'):
			     day1 = "ЮЗ"
		     elif (day == 'WSW'):
			     day1 = "ЗЮЗ"
		     return day1
		else:
		     if day.find('WNW') != -1:
			     day = "WNW"
		     return day

	def Icons(self, direct):
                    info = ''
		    if direct == "_0_moon.gif":
			    info = 'wsymbol_0008_clear_sky_night.png'
		    elif direct == "_0_sun.gif":
			    info = 'wsymbol_0001_sunny.png'
		    elif direct == "_1_moon_cl.gif":
			    info = 'wsymbol_0003_white_cloud.png'
		    elif direct == "_1_sun_cl.gif":
			    info = 'wsymbol_0005_hazy_sun.png'
		    elif direct == "_2_cloudy.gif":
			    info = 'wsymbol_0003_white_cloud.png'
		    elif direct == "_3_pasmurno.gif":
			    info = 'wsymbol_0004_black_low_cloud.png'
		    elif direct == "_4_short_rain.gif":
			    info = 'wsymbol_0009_light_rain_showers.png'
		    elif direct == "_5_rain.gif":
			    info = 'wsymbol_0010_heavy_rain_showers.png'
		    elif direct == "_6_lightning.gif":
			    info = 'wsymbol_0024_thunderstorms.png'
		    elif direct == "_7_hail.gif":
			    info = 'wsymbol_0015_heavy_hail_showers.png'
		    elif direct == "_8_rain_swon.gif":
			    info = 'wsymbol_0021_cloudy_with_sleet.png'
		    elif direct == "_9_snow.gif":
			    info = 'wsymbol_0019_cloudy_with_light_snow.png'
		    elif direct == "_10_heavy_snow.gif":
			    info = 'wsymbol_0020_cloudy_with_heavy_snow.png'
		    elif direct == "_255_NA.gif":
			    info = 'NA.png'
		    return info

	def Timecontrol(self, direct):
                    info = ''
		    if direct >= 0 and direct < 6:
			    info = '3'
		    elif direct >= 6 and direct < 12:
			    info = '9'
		    elif direct >= 12 and direct < 18:
			    info = '15'
		    elif direct >= 18 and direct <= 23:
			    info = '21'
		    return info

	def Winddirect(self, direct):
                    info = ''
		    if direct >= 0 and direct <= 20:
			    info = _('N')
		    elif direct >= 21 and direct <= 35:
			    info = _('NNE')
		    elif direct >= 36 and direct <= 55:
			    info = _('NE')
		    elif direct >= 56 and direct <= 70:
			    info = _('ENE')
		    elif direct >= 71 and direct <= 110:
			    info = _('E')
		    elif direct >= 111 and direct <= 125:
			    info = _('ESE')
		    elif direct >= 126 and direct <= 145:
			    info = _('SE')
		    elif direct >= 146 and direct <= 160:
			    info = _('SSE')
		    elif direct >= 161 and direct <= 200:
			    info = _('S')
		    elif direct >= 201 and direct <= 215:
			    info = _('SSW')
		    elif direct >= 216 and direct <= 235:
			    info = _('SW')
		    elif direct >= 236 and direct <= 250:
			    info = _('WSW')
		    elif direct >= 251 and direct <= 290:
			    info = _('W')
		    elif direct >= 291 and direct <= 305:
			    info = _('WNW')
		    elif direct >= 306 and direct <= 325:
			    info = _('NW')
		    elif direct >= 326 and direct <= 340:
			    info = _('NNW')
		    elif direct >= 341 and direct <= 360:
			    info = _('N')
		    return info

	def Cloud(self, direct):
            info = ''
            if config.plugins.WeatherPlugin.language.value == "0":
		    if direct >= 0 and direct < 10:
			    info = _('Ясно')
		    elif direct >= 10 and direct < 20:
			    info = _('Местами облачно')
		    elif direct >= 20 and direct < 30:
			    info = _('Облачно')
		    elif direct >= 30 and direct < 40:
			    info = _('Пасмурно')
		    elif direct >= 40 and direct < 50:
			    info = _('Местами дождь')
		    elif direct >= 50 and direct < 60:
			    info = _('Дождь')
		    elif direct >= 60 and direct < 70:
			    info = _('Гроза')
		    elif direct >= 70 and direct < 80:
			    info = _('Град')
		    elif direct >= 80 and direct < 90:
			    info = _('Снег с дождем')
		    elif direct >= 90 and direct < 100:
			    info = _('Небольшой снег')
		    elif direct >= 100 and direct < 110:
			    info = _('Снег')
		    return info
            if config.plugins.WeatherPlugin.language.value == "1":
		    if direct >= 0 and direct < 10:
			    info = _('Clear')
		    elif direct >= 10 and direct < 20:
			    info = _('Partly Cloudy')
		    elif direct >= 20 and direct < 30:
			    info = _('Cloudy')
		    elif direct >= 30 and direct < 40:
			    info = _('Overcast')
		    elif direct >= 40 and direct < 50:
			    info = _('Mostly sunny')
		    elif direct >= 50 and direct < 60:
			    info = _('Rain')
		    elif direct >= 60 and direct < 70:
			    info = _('Thunderstorm')
		    elif direct >= 70 and direct < 80:
			    info = _('Hail')
		    elif direct >= 80 and direct < 90:
			    info = _('Sleet')
		    elif direct >= 90 and direct < 100:
			    info = _('Light snow')
		    elif direct >= 100 and direct < 110:
			    info = _('Snow')
		    return info

	def eXtendedDay(self, day):
                if config.plugins.WeatherPlugin.language.value == "0":
		     if day.find('Moderate or heavy snow in area with thunder') != -1:
			     day = "Сильный снегопад"
		     elif day.find('Patchy light snow in area with thunder') != -1:
			     day = "Небольшой снегопад"
		     elif day.find('Moderate or heavy rain in area with thunder') != -1:
			     day = "Гроза"
		     elif day.find('Patchy light rain in area with thunder') != -1:
			     day = "Небольшая гроза"
		     elif day.find('Moderate or heavy showers of ice pellets') != -1:
			     day = "Ливень с градом"
		     elif day.find('Light showers of ice pellets') != -1:
			     day = "Дождь с градом"
		     elif day.find('Moderate or heavy snow showers') != -1:
			     day = "Cильный снегопад"
		     elif day.find('Light snow showers') != -1:
			     day = "Небольшой снег"
		     elif day.find('Moderate or heavy sleet showers') != -1:
			     day = "Ливень со снегом"
		     elif day.find('Light sleet showers') != -1:
			     day = "Дождь со снегом"
		     elif day.find('Torrential rain shower') != -1:
			     day = "Ливень"
		     elif day.find('Moderate or heavy rain shower') != -1:
			     day = "Сильный дождь"
		     elif day.find('Light rain shower') != -1:
			     day = "Небольшой дождь"
		     elif day.find('Ice pellets') != -1:
			     day = "Град"
		     elif day.find('Heavy snow') != -1:
			     day = "Сильный снегопад"
		     elif day.find('Patchy heavy snow') != -1:
			     day = "Снегопад"
		     elif day.find('Moderate snow') != -1:
			     day = "Снег"
		     elif day.find('Patchy moderate snow') != -1:
			     day = "Местами снег"
		     elif day.find('Light snow') != -1:
			     day = "Небольшой снег"
		     elif day.find('Patchy light snow') != -1:
			     day = "Местами снег"
		     elif day.find('Moderate or heavy sleet') != -1:
			     day = "Дождь со снегом"
		     elif day.find('Light sleet') != -1:
			     day = "Мокрый снег"
		     elif day.find('Moderate or Heavy freezing rain') != -1:
			     day = "Мокрый снег"
		     elif day.find('Light freezing rain') != -1:
			     day = "Мокрый снег"
		     elif day.find('Heavy rain') != -1:
			     day = "Сильный ливень"
		     elif day.find('Heavy rain at times') != -1:
			     day = "Местами ливень"
		     elif day.find('Moderate rain') != -1:
			     day = "Небольшой дождь"
		     elif day.find('Moderate rain at times') != -1:
			     day = "Местами дождь"
		     elif day.find('Light rain') != -1:
			     day = "Небольшой дождь"
		     elif day.find('Patchy light rain') != -1:
			     day = "Местами дождь"
		     elif day.find('Heavy freezing drizzle') != -1:
			     day = "Сильная изморозь"
		     elif day.find('Freezing drizzle') != -1:
			     day = "Изморозь"
		     elif day.find('Light drizzle') != -1:
			     day = "Мелкий дождь"
		     elif day.find('Patchy light drizzle') != -1:
			     day = "Местами дождь"
		     elif day.find('Freezing fog') != -1:
			     day = "Густой туман"
                     elif day.find('Fog') != -1:
			     day = "Туман"
		     elif day.find('Blizzard') != -1:
			     day = "Метель"
		     elif day.find('Blowing snow') != -1:
			     day = "Небольшая метель"
		     elif day.find('Thundery outbreaks in nearby') != -1:
			     day = "Гроза"
		     elif day.find('Patchy freezing drizzle nearby') != -1:
			     day = "Мокрый снег"
		     elif day.find('Patchy sleet nearby') != -1:
			     day = "Местами мокрый снег"
		     elif day.find('Patchy snow nearby') != -1:
			     day = "Местами снег"
		     elif day.find('Patchy rain nearby') != -1:
			     day = "Местами дождь"
		     elif day.find('Mist') != -1:
			     day = "Пасмурно"
		     elif day.find('Overcast') != -1:
			     day = "Облачно"
		     elif day.find('Cloudy') != -1:
			     day = "Облачно"
		     elif day.find('Partly Cloudy') != -1:
			     day = "Переменная облачность"
		     elif day.find('Clear') != -1:
			     day = "Ясно"
		     elif day.find('Sunny') != -1:
			     day = "Ясно"
		     elif day.find('Humidity:') != -1:
			     day = "Влаж.:"
		     elif day.find('Wind: ') != -1:
			     day = "Ветер: "
		     elif day.find(' Kmph') != -1:
			     day = " Км/ч"
		     elif day.find(' m/s') != -1:
			     day = " м/с"
		     elif day.find('\nMin °C: ') != -1:
			     day = "\nМин. °C: "
		     elif day.find('\nMax °C: ') != -1:
			     day = "\nМакс. °C: "
		     return day
                if config.plugins.WeatherPlugin.language.value == "1":
		     if day.find('Moderate or heavy snow in area with thunder') != -1:
			     day = (_("Heavy snow"))
		     elif day.find('Patchy light snow in area with thunder') != -1:
			     day = (_("Light snow"))
		     elif day.find('Moderate or heavy rain in area with thunder') != -1:
			     day = (_("Heavy rain"))
		     elif day.find('Patchy light rain in area with thunder') != -1:
			     day = (_("Light rain"))
		     elif day.find('Moderate or heavy showers of ice pellets') != -1:
			     day = (_("Heavy rain and hail"))
		     elif day.find('Light showers of ice pellets') != -1:
			     day = (_("Rain and hail"))
		     elif day.find('Moderate or heavy snow showers') != -1:
			     day = (_("Heavy snow"))
		     elif day.find('Light snow showers') != -1:
			     day = (_("Light snow showers"))
		     elif day.find('Moderate or heavy sleet showers') != -1:
			     day = (_("Heavy sleet showers"))
		     elif day.find('Light sleet showers') != -1:
			     day = (_("Sleet showers"))
		     elif day.find('Torrential rain shower') != -1:
			     day = (_("Shower"))
		     elif day.find('Moderate or heavy rain shower') != -1:
			     day = (_("Heavy rain shower"))
		     elif day.find('Light rain shower') != -1:
			     day = (_("Rain shower"))
		     elif day.find('Ice pellets') != -1:
			     day = (_("Ice pellets"))
		     elif day.find('Heavy snow') != -1:
			     day = (_("Heavy snow"))
		     elif day.find('Patchy heavy snow') != -1:
			     day = (_("Heavy snow"))
		     elif day.find('Moderate snow') != -1:
			     day = (_("Snow"))
		     elif day.find('Patchy moderate snow') != -1:
			     day = (_("Patchy snow"))
		     elif day.find('Light snow') != -1:
			     day = (_("Light snow"))
		     elif day.find('Patchy light snow') != -1:
			     day = (_("Light snow"))
		     elif day.find('Moderate or heavy sleet') != -1:
			     day = (_("Rain and snow"))
		     elif day.find('Light sleet') != -1:
			     day = (_("Light sleet"))
		     elif day.find('Moderate or Heavy freezing rain') != -1:
			     day = (_("Heavy freezing rain"))
		     elif day.find('Light freezing rain') != -1:
			     day = (_("Freezing rain"))
		     elif day.find('Heavy rain') != -1:
			     day = (_("Heavy rain"))
		     elif day.find('Heavy rain at times') != -1:
			     day = (_("Heavy rain"))
		     elif day.find('Moderate rain') != -1:
			     day = (_("Moderate rain"))
		     elif day.find('Moderate rain at times') != -1:
			     day = (_("Moderate rain"))
		     elif day.find('Light rain') != -1:
			     day = (_("Light rain"))
		     elif day.find('Patchy light rain') != -1:
			     day = (_("light rain"))
		     elif day.find('Heavy freezing drizzle') != -1:
			     day = (_("Freezing drizzle"))
		     elif day.find('Freezing drizzle') != -1:
			     day = (_("Freezing drizzle"))
		     elif day.find('Light drizzle') != -1:
			     day = (_("Light drizzle"))
		     elif day.find('Patchy light drizzle') != -1:
			     day = (_("Light drizzle"))
		     elif day.find('Freezing fog') != -1:
			     day = (_("Freezing fog"))
                     elif day.find('Fog') != -1:
			     day = (_("Fog"))
		     elif day.find('Blizzard') != -1:
			     day = (_("Blizzard"))
		     elif day.find('Blowing snow') != -1:
			     day = (_("Blowing snow"))
		     elif day.find('Thundery outbreaks in nearby') != -1:
			     day = (_("Thunderstorm"))
		     elif day.find('Patchy freezing drizzle nearby') != -1:
			     day = (_("Drizzle nearby"))
		     elif day.find('Patchy sleet nearby') != -1:
			     day = (_("Patchy sleet nearby"))
		     elif day.find('Patchy snow nearby') != -1:
			     day = (_("Patchy snow nearby"))
		     elif day.find('Patchy rain nearby') != -1:
			     day = (_("Patchy rain nearby"))
		     elif day.find('Mist') != -1:
			     day = (_("Mist"))
		     elif day.find('Overcast') != -1:
			     day = (_("Overcast"))
		     elif day.find('Cloudy') != -1:
			     day = (_("Cloudy"))
		     elif day.find('Partly Cloudy') != -1:
			     day = (_("Partly Cloudy"))
		     elif day.find('Clear') != -1:
			     day = (_("Clear"))
		     elif day.find('Sunny') != -1:
			     day = (_("Sunny"))
		     return day

	def delTimer(self):
                if config.plugins.WeatherPlugin.enabled.value == False:
                     if self.activityTimer.isActive():
                           self.activityTimer.stop()
                self.showTimer.start(50, 1)


class WeatherPluginPositioner(Screen):
	skin = """
		 <screen position="center,center" size="230,415" zPosition="-1" backgroundColor="#ff000000" flags="wfNoBorder">
                 <ePixmap pixmap="~/backg.png" zPosition="2" position="0,0" size="230,415" alphatest="on" />
                 <widget name="lab1" position="24,25" halign="center" size="180,20" zPosition="4" font="Regular;20" foregroundColor="#33bab329" backgroundColor="#00000000" valign="top" transparent="1" />
                 <widget name="City" position="24,48" halign="center" size="180,18" zPosition="4" font="Regular;16" foregroundColor="#33bab329" backgroundColor="#00000000" valign="top" transparent="1" />
                 <ePixmap pixmap="~/NA.png" position="67,66" size="138,95" zPosition="3" transparent="1" alphatest="on" />
                 <widget name="Temp now" position="24,81" halign="left" size="80,60" zPosition="4" font="Regular;27" valign="top" backgroundColor="#00000000" transparent="1" />
                 <widget name="Description now" position="24,150" halign="center" size="180,80" zPosition="4" font="Regular;18" valign="top" backgroundColor="#00000000" transparent="1" />
                 <widget name="Date of tomorrow" position="24,229" halign="center" size="180,20" zPosition="4" foregroundColor="#33bab329" backgroundColor="#00000000" font="Regular;20" valign="top" transparent="1" />
                 <ePixmap pixmap="~/na2.png"  position="117,260" size="87,60" zPosition="3" transparent="1" alphatest="on" />
                 <widget name="Description tomorrow" position="24,252" halign="left" size="180,60" zPosition="4" font="Regular;16" valign="top" backgroundColor="#00000000" transparent="1" />
                 <widget name="day after tomorrow" position="24,312" halign="center" size="180,20" zPosition="4" foregroundColor="#33bab329" backgroundColor="#00000000" font="Regular;20" valign="top" transparent="1" />
                 <ePixmap pixmap="~/na2.png" position="117,340" size="87,60" zPosition="3" transparent="1" alphatest="on" />
                 <widget name="Description2" position="24,333" halign="left" size="180,60" zPosition="4" font="Regular;16" valign="top" backgroundColor="#00000000" transparent="1" />
                 </screen>"""
	skin1 = """
	    <screen position="center,center" size="230,245" zPosition="3" backgroundColor="#ff000000" flags="wfNoBorder">
	    <ePixmap pixmap="~/backg2.png" zPosition="2" position="0,0" size="230,245" alphatest="on" />
            <widget name="lab1" position="24,25" halign="center" size="180,20" zPosition="4" font="Regular;20" foregroundColor="#00ffcc33" backgroundColor="#30000000" valign="top" transparent="1" />
            <widget name="City" position="24,48" halign="center" size="180,18" zPosition="4" font="Regular;16" foregroundColor="#00ffcc33" backgroundColor="#30000000" valign="top" transparent="1" />
            <ePixmap pixmap="~/NA.png" position="67,66" size="138,95" zPosition="3" transparent="1" alphatest="on" />
            <widget name="Temp now" position="24,77" halign="left" size="80,30" zPosition="4" font="Regular;27" valign="top" backgroundColor="#00000000" transparent="1" />
            <widget name="Description now" position="24,150" halign="center" size="180,80" zPosition="4" font="Regular;18" valign="top" backgroundColor="#00000000" transparent="1" />
	    </screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather")
 		if config.plugins.WeatherPlugin.days.value == "0":
		     self.skin = WeatherPluginPositioner.skin
 		if config.plugins.WeatherPlugin.days.value == "1":
		     self.skin = WeatherPluginPositioner.skin1
		self["lab1"] = Label(_("Started"))
		self["City"] = Label(_("Connection..."))
		self["Temp now"] = Label("")
		self["Description now"] = Label("")
		self["Date of tomorrow"] = Label("")
		self["Description tomorrow"] = Label("")
		self["day after tomorrow"] = Label("")
		self["Description2"] = Label("")
		self.activityTimer = eTimer()
		self["actions"] = ActionMap(["WizardActions"],
		{
			"left": self.left,
			"up": self.up,
			"right": self.right,
			"down": self.down,
			"ok": self.ok,
			"back": self.exit
		}, -1)

		desktop = getDesktop(0)
		self.desktopWidth = desktop.size().width()
		self.desktopHeight = desktop.size().height()
		self.resetLabels2()
		self.moveTimer = eTimer()
		self.moveTimer.callback.append(self.movePosition)
		self.moveTimer.start(50, 1)

	def resetLabels2(self):
		self["lab1"].setText(_("None"))
		self["City"].setText("Chernivtsi, Ukraine")
		self["Temp now"].setText("")
		self["Description now"].setText(_("None"))
		self["Date of tomorrow"].setText(_("None"))
		self["day after tomorrow"].setText(_("None"))
		self["Description2"].setText(_("None"))
		self["Description tomorrow"].setText(_("None"))

	def movePosition(self):
		self.instance.move(ePoint(config.plugins.WeatherPlugin.position_x.value, config.plugins.WeatherPlugin.position_y.value))
		self.moveTimer.start(50, 1)

	def left(self):
		value = config.plugins.WeatherPlugin.position_x.value
		value -= 1
		if value < 0:
			value = 0
		config.plugins.WeatherPlugin.position_x.value = value

	def up(self):
		value = config.plugins.WeatherPlugin.position_y.value
		value -= 1
		if value < 0:
			value = 0
		config.plugins.WeatherPlugin.position_y.value = value

	def right(self):
		value = config.plugins.WeatherPlugin.position_x.value
		value += 1
		if value > self.desktopWidth:
			value = self.desktopWidth
		config.plugins.WeatherPlugin.position_x.value = value

	def down(self):
		value = config.plugins.WeatherPlugin.position_y.value
		value += 1
		if value > self.desktopHeight:
			value = self.desktopHeight
		config.plugins.WeatherPlugin.position_y.value = value

	def ok(self):
		config.plugins.WeatherPlugin.position_x.save()
		config.plugins.WeatherPlugin.position_y.save()
		self.close()

	def exit(self):
		config.plugins.WeatherPlugin.position_x.cancel()
		config.plugins.WeatherPlugin.position_y.cancel()
		self.close()


class WeatherPluginMenu(Screen):
	skin = """
		<screen position="center,center" size="420,260" title="Quick Weather Menu">
		<widget name="list" position="10,10" size="400,180" />
                <ePixmap pixmap="~/info.png" position="0,183" zPosition="1" size="420,80" alphatest="on" />
                <widget name="info" position="11,203" halign="center" size="400,50" zPosition="4" font="Regular;18" valign="top" backgroundColor="#00000000" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather")
		self.session = session
		self.setTitle(_('Quick Weather Menu v.8.2'))
		self["info"] = Label("")
		self["list"] = MenuList([])
		self["actions"] = ActionMap(["OkCancelActions", 'DirectionActions'], {"ok": self.okClicked,
                'cancel': self.exit,
                'down': self.pageDown,
                'up': self.pageUp,
                'left': self.pageUp,
                'right': self.pageDown}, -1)
 		self.onLayoutFinish.append(self.showMenu)
 		self.reed()

        def pageUp(self):
            self['list'].instance.moveSelection(self['list'].instance.moveUp)
            id = self["list"].getCurrent()
	    self.search_info(id)

        def pageDown(self):
            self['list'].instance.moveSelection(self['list'].instance.moveDown)
            id = self["list"].getCurrent()
	    self.search_info(id)

	def showMenu(self):
		list = []
		list.append(_("Change Quick Weather position"))
		list.append(_("Setup Quick Weather"))
		list.append(_("Enter city for worldweatheronline.com"))
		list.append(_("Enter city for infobar"))
		list.append(_("Change background image"))
		list.append(_("Selection of weather icons"))
		list.append(_("Choice keymap for plugin"))
		self["list"].setList(list)
                id = self["list"].getCurrent()
	        self.search_info(id)

        def search_info(self, id):
                if id == _("Setup Quick Weather"):
			self["info"].setText(_("Basic settings plugin Quick Weather"))
                elif id == _("Change background image"):
			self["info"].setText(_("Selection of background images for the plugin Quick Weather"))
                elif id == _("Enter city for worldweatheronline.com"):
			self["info"].setText(_("Enter city to find weather from the server worldweatheronline.com"))
                elif id == _("Enter city for infobar"):
			self["info"].setText(_("Enter an alternative name for the city in infobare plugin-not to find weather"))
                elif id == _("Choice keymap for plugin"):
			self["info"].setText(_("Selection keys on which the plugin is called"))
                elif id == _("Selection of weather icons"):
			self["info"].setText(_("Selection of weather icons and their storage"))
		else:
			self["info"].setText(_("Positioning infobar plugin on the screen"))

	def okClicked(self):
		sel = self["list"].getCurrent()
                if sel == _("Setup Quick Weather"):
			self.session.openWithCallback(self.positionerCallback, SetupMenu)
                elif sel == _("Change background image"):
			self.session.openWithCallback(self.positionerCallback, SetupMenu2)
                elif sel == _("Enter city for worldweatheronline.com"):
                        self.session.openWithCallback(self.ShowsearchBarracuda, VirtualKeyBoard, title=_("Enter only the English name of the city!!!"), text="")
                elif sel == _("Enter city for infobar"):
			self.session.openWithCallback(self.ShowsearchBarracuda2, VirtualKeyBoard, title=_("Enter an alternative name for the output of its plug-in infobare."), text="")
                elif sel == _("Selection of weather icons"):
			self.session.openWithCallback(self.positionerCallback, SetupIcons)
                elif sel == _("Choice keymap for plugin"):
			self.session.openWithCallback(self.positionerCallback, SetupKeymap)
		else:
			self.session.openWithCallback(self.positionerCallback, WeatherPluginPositioner)

	def positionerCallback(self, callback=None):
		 self.working = False

	def ShowsearchBarracuda(self, cmd):
		if cmd is not None:
			self.session.open(WeatherSelectCity, cmd)

	def ShowsearchBarracuda2(self, cmd):
		if cmd is not None:
			self.session.open(WeatherCityInfobar, cmd)

        def reed(self):
            global ekran, ekransmol
            ekran = None
            ekransmol = None
            f = open('/etc/enigma2/settings')
            commentRe = re.compile('#(.*)')
            entryRe = re.compile('(.*)=(.*)')
            try:
                for line in f.readlines():
                    comment = re.findall(commentRe, line)
                    if not comment:
                        entry = re.findall(entryRe, line)
                        if entry:
                            key = entry[0][0].strip()
                            value = entry[0][1].strip()
                            if key == 'config.plugins.WeatherPlugin.enabled':
                                ekran = value
                                print(ekran)
                            elif key == 'config.plugins.WeatherPlugin.days':
                                ekransmol = value
                                print(ekransmol)
            finally:
                f.close()

        def exit(self):
            ekran2 = None
            ekransmol2 = None
            f = open('/etc/enigma2/settings')
            commentRe = re.compile('#(.*)')
            entryRe = re.compile('(.*)=(.*)')
            try:
                for line in f.readlines():
                    comment = re.findall(commentRe, line)
                    if not comment:
                        entry = re.findall(entryRe, line)
                        if entry:
                            key = entry[0][0].strip()
                            value = entry[0][1].strip()
                            if key == 'config.plugins.WeatherPlugin.enabled':
                                ekran2 = value
                                print(ekran2)
                            elif key == 'config.plugins.WeatherPlugin.days':
                                ekransmol2 = value
                                print(ekransmol2)
            finally:
                f.close()

            if ekran2 != ekran or ekransmol2 != ekransmol:
                restart = self.session.openWithCallback(self.restart, MessageBox, _('You have changed the menu Activate Quick Weather or Display the weather for') + '\n\n' + _('Do you want restart GUI now?'), MessageBox.TYPE_YESNO)
                restart.setTitle(_('Restart GUI now?'))
            else:
                Console().ePopen("rm -rf /tmp/indbweather.xml")
                self.close()

        def restart(self, confirmed):
            if confirmed:
                Console().ePopen("rm -rf /tmp/indbweather.xml")
                from Screens.Standby import TryQuitMainloop
                self.session.open(TryQuitMainloop, 3)
            else:
                self.close()


class SetupMenu(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="560,190" title="Setup Quick Weather" backgroundColor="#31000000" >
	<widget name="config" position="10,10" size="540,145" zPosition="1" transparent="0" backgroundColor="#31000000" scrollbarMode="showOnDemand" />
	<widget name="key_green" position="0,155" zPosition="2" size="250,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="#00389416" />
	<widget name="key_red" position="250,155" zPosition="2" size="250,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="#00ff2525" />
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_('Setup Quick Weather'))
		self['key_red'] = Button(_('Cancel'))
		self['key_green'] = Button(_('Save'))
		self['actions'] = ActionMap(['SetupActions',
		    'ColorActions'], {'green': self.save,
	            'ok': self.save,
	            'red': self.exit,
	            'cancel': self.exit}, -2)
		list = []
		list.append(getConfigListEntry(_('Activate Quick Weather'), config.plugins.WeatherPlugin.enabled))
		list.append(getConfigListEntry(_('Display the weather for:'), config.plugins.WeatherPlugin.days))
		list.append(getConfigListEntry(_('Use buttons for show Weather'), config.plugins.WeatherPlugin.usebutton))
		list.append(getConfigListEntry(_('Use time in the plugin:'), config.plugins.WeatherPlugin.clock))
		list.append(getConfigListEntry(_('Auto update (30-150min):'), config.plugins.WeatherPlugin.timeout))
		list.append(getConfigListEntry(_('Weather languages:'), config.plugins.WeatherPlugin.language))
	        list.append(getConfigListEntry(_('Clearing the cache:'), config.plugins.WeatherPlugin.caches))
	        list.append(getConfigListEntry(_('Show wind:'), config.plugins.WeatherPlugin.wind))
	        list.append(getConfigListEntry(_('Show animation for icons now:'), config.plugins.WeatherPlugin.anim))
	        list.append(getConfigListEntry(_('Show animation for the other days:'), config.plugins.WeatherPlugin.anim2))
	        list.append(getConfigListEntry(_('Choosing the path to animated icons:'), config.plugins.WeatherPlugin.anim3))
	        list.append(getConfigListEntry(_('Buttons for Weather plugin:'), config.plugins.WeatherPlugin.hotkey))
	        list.append(getConfigListEntry(_('Show city of:'), config.plugins.WeatherPlugin.city))
		ConfigListScreen.__init__(self, list)

	def save(self):
		ConfigListScreen.keySave(self)
		configfile.save()

	def exit(self):
		self.close()


class SetupMenu2(Screen):
    skin = """
        <screen position="center,center" size="560,400" title="Change background image" backgroundColor="#31000000" >
	<widget name="menu" position="10,5" size="330,380" zPosition="1" transparent="0" backgroundColor="#31000000" scrollbarMode="showOnDemand" />
        <widget name="previem" position="345,4" size="211,380" zPosition="3" transparent="1" alphatest="on" />
	</screen>"""

    def __init__(self, session):
        self.skin = SetupMenu2.skin
        Screen.__init__(self, session)
	self.setTitle(_('Change background image'))
        self.resultlist = []
	self.onShow.append(self.getPanelmenu)
        self['menu'] = MenuList(self.resultlist)
        self["previem"] = Pixmap()
        self['actions'] = ActionMap(['OkCancelActions', 'DirectionActions'], {'ok': self.showDetails,
         'cancel': self.exit,
         'down': self.pageDown,
         'up': self.pageUp,
         'left': self.pageUp,
         'right': self.pageDown}, -1)

    def pageUp(self):
        self['menu'].instance.moveSelection(self['menu'].instance.moveUp)
        id = str(self['menu'].getCurrent()[0])
	self.search_poster(id)

    def pageDown(self):
        self['menu'].instance.moveSelection(self['menu'].instance.moveDown)
        id = str(self['menu'].getCurrent()[0])
	self.search_poster(id)

    def exit(self):
        self.close()

    def showDetails(self):
        id = str(self['menu'].getCurrent()[0])
        text = '%s' % (id)
        if config.plugins.WeatherPlugin.days.value == "0":
            Console().ePopen("cp -f %s %s") % (resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/background/%s.png" % text), resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/background/backg.png"))
        if config.plugins.WeatherPlugin.days.value == "1":
            Console().ePopen("cp -f %s %s") % (resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/background1/%s.png" % text), resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/background/backg2.png"))
        self.exit()

    def getPanelmenu(self):
        title = ''
        try:
            results = self.getList()
        except:
            results = []
        if len(results) == 0:
            return False
        self.resultlist = []
        for searchResult in results:
            try:
                self.resultlist.append(searchResult)
            except:
                pass
        self['menu'].l.setList(self.resultlist)
        id = str(self['menu'].getCurrent()[0])
	self.search_poster(id)

    def search_poster(self, id):
                text = '%s' % (id)
                if config.plugins.WeatherPlugin.days.value == "0":
		    filename = resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/background/%s.png') % text
                if config.plugins.WeatherPlugin.days.value == "1":
		    filename = resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/background1/%s.png') % text
                png2 = loadPic(filename, 211, 380, 0, 0, 0, 1)
                self["previem"].instance.setPixmap(png2)

    def getList(self):
	    b00klist = []
	    if config.plugins.WeatherPlugin.days.value == "0":
		if os.path.exists(resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/background")) == True:
           		for name in os.listdir(resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/background")):
              			if name.endswith(".png") is True:
                 			bname = name.split(".png")
                      			b00klist.append((bname[0], name))
	    else:
		if os.path.exists(resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/background1")) == True:
           		for name in os.listdir(resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/background1")):
              			if name.endswith(".png") is True:
                 			bname = name.split(".png")
                      			b00klist.append((bname[0], name))
            b00klist.sort()
	    return b00klist


class WeatherSelectCity(Screen):
	def __init__(self, session, cmd):
		Screen.__init__(self, session)
		self['list'] = List([])
		self.searchEvent(cmd)

	def searchEvent(self, cmd):
		flist = []
		mycache = []
		idx = 0
		if len(cmd) > 1:
			if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/weatherindb.cfg')):
				fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/weatherindb.cfg'))
			mycache.append(cmd)
			if len(mycache) > 10:
				mycache = mycache[1:]
			f1 = open(resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/weatherindb.cfg'), 'w')
			for fil in mycache:
				f1.write(fil + '\n')
			f1.close()
                Console().ePopen("rm -rf /tmp/indbweather.xml")
		self.close()

	def workingFinished(self, callback=None):
		self.working = False


class WeatherCityInfobar(Screen):
	def __init__(self, session, cmd):
		Screen.__init__(self, session)
		self['list'] = List([])
		self.searchEvent(cmd)

	def searchEvent(self, cmd):
		flist = []
		mycache = []
		idx = 0
		if len(cmd) > 1:
			if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/city.cfg')):
				fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/city.cfg'))
			mycache.append(cmd)
			if len(mycache) > 10:
				mycache = mycache[1:]
			f1 = open(resolveFilename(SCOPE_PLUGINS, 'Extensions/QuickWeather/city.cfg'), 'w')
			for fil in mycache:
				f1.write(fil + '\n')
			f1.close()
		self.close()

	def workingFinished(self, callback=None):
		self.working = False


class WeatherInfoBar:
	def __init__(self, session, infobar):
		self.session = session
		self.infobar = infobar
		self.lastKey = None
		self.hotkeys = {}
		self.dialog = None
		for x in WeatherInfoBarKeys:
			self.hotkeys[x[0]] = [KEYIDS[key] for key in x[2]]
		eActionMap.getInstance().bindAction('', -10, self.keyPressed)

	def keyPressed(self, key, flag):
		for k in self.hotkeys[config.plugins.WeatherPlugin.hotkey.value]:
			if key == k and self.session.current_dialog == self.infobar:
				if flag == 0:
					self.lastKey = key
				elif self.lastKey != key or flag == 4:
					self.lastKey = None
					continue
				elif flag == 1:
					self.lastKey = None
					self.showWeather()
				return 1
		return 0

	def showWeather(self):
		self.session.open(WeatherPluginScreen)


class SetupKeymap(Screen):
    skin = """
	<screen position="center,center" size="500,190" title="Change background image" backgroundColor="#31000000" >
	<widget name="menu" position="10,10" size="480,145" zPosition="1" transparent="0" backgroundColor="#31000000" scrollbarMode="showOnDemand" />
	<widget name="key_green" position="0,155" zPosition="2" size="250,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="#00389416" />
	<widget name="key_red" position="250,155" zPosition="2" size="250,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="#00ff2525" />
	</screen>"""

    def __init__(self, session):
        self.skin = SetupKeymap.skin
        Screen.__init__(self, session)
	self.setTitle(_('Change Keymap'))
        self.resultlist = []
	self['key_red'] = Button(_('Cancel'))
	self['key_green'] = Button(_('Save'))
        self['menu'] = MenuList(self.resultlist)
        self['actions'] = ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions'], {'ok': self.showDetails,
         'cancel': self.exit,
         'down': self.pageDown,
         'up': self.pageUp,
         'green': self.showDetails,
         'red': self.exit,
         'left': self.pageUp,
         'right': self.pageDown}, -1)
        self.getPanelmenu()

    def pageUp(self):
        self['menu'].instance.moveSelection(self['menu'].instance.moveUp)

    def pageDown(self):
        self['menu'].instance.moveSelection(self['menu'].instance.moveDown)

    def exit(self):
        self.close()

    def showDetails(self):
        id = str(self['menu'].getCurrent()[0])
        text = '%s' % (id)
        Console().ePopen("cp -f %s %s") % (resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/SetupKeymap/%s.xml" % text), resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/keymap.xml"))
        from Screens.Standby import TryQuitMainloop
        self.session.open(TryQuitMainloop, 3)

    def getPanelmenu(self):
        title = ''
        try:
            results = self.getList()
        except:
            results = []
        if len(results) == 0:
            return False
        self.resultlist = []
        for searchResult in results:
            try:
                self.resultlist.append(searchResult)
            except:
                pass
        self['menu'].l.setList(self.resultlist)

    def getList(self):
		b00klist = []
		if os.path.exists(resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/SetupKeymap")) == True:
           		for name in os.listdir(resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/SetupKeymap")):
              			if name.endswith(".xml") is True:
                 			bname = name.split(".xml")
                      			b00klist.append((bname[0], name))
        	b00klist.sort()
	        return b00klist


class SetupIcons(Screen):
    skin = """
	<screen position="center,center" size="460,400" title="Change background image" backgroundColor="#31000000" >
	<widget name="menu" position="10,5" size="440,120" zPosition="1" transparent="0" backgroundColor="#31000000" scrollbarMode="showOnDemand" />
        <widget name="previem" position="22,160" size="420,236" zPosition="3" transparent="1" alphatest="on" />
        <ePixmap pixmap="buttons/key_menu.png" position="16,132" zPosition="1" size="35,25" alphatest="on" />
        <widget name="menutext" position="51,134" halign="left" size="380,18" zPosition="4" font="Regular;18" foregroundColor="#33bab329" backgroundColor="#00000000" valign="top" transparent="1" />
	</screen>"""

    def __init__(self, session):
        self.skin = SetupIcons.skin
        Screen.__init__(self, session)
	self.setTitle(_('Setup Icons'))
        self.resultlist = []
	self.onShow.append(self.getPanelmenu)
        self['menu'] = MenuList(self.resultlist)
        self["previem"] = Pixmap()
        self["menutext"] = Label(_("Enter your way to the storage of icons"))
        self['actions'] = ActionMap(['OkCancelActions', 'DirectionActions', 'MovieSelectionActions'], {'ok': self.showDetails,
         'cancel': self.exit,
         'down': self.pageDown,
         'up': self.pageUp,
         'left': self.pageUp,
         'contextMenu': self.openVirtualKeyBoard,
         'right': self.pageDown}, -1)

    def openVirtualKeyBoard(self):
	    self.session.openWithCallback(
		    self.ShowsearchBarracuda,
		    VirtualKeyBoard,
		    title=_("Enter your way to the storage of icons"),
                    text=self.name()
	    )

    def name(self):
        cfgfile = resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/weathericons.cfg")
        text = ""
        if fileExists(cfgfile):
            		f = open(cfgfile, 'r')
			line = f.readline()
			text = line.strip()
			f.close()
	else:
             text = "/media/hdd/"
        return text

    def ShowsearchBarracuda(self, cmd):
	    if cmd is not None:
                            localfile = resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/weathericons.cfg")
		            temp_file = open(localfile, "w")
                            temp_file.write(cmd)
                            temp_file.close()
                            self.close()

    def pageUp(self):
        self['menu'].instance.moveSelection(self['menu'].instance.moveUp)
        id = str(self['menu'].getCurrent()[0])
	self.search_poster(id)

    def pageDown(self):
        self['menu'].instance.moveSelection(self['menu'].instance.moveDown)
        id = str(self['menu'].getCurrent()[0])
	self.search_poster(id)

    def exit(self):
        self.close()

    def showDetails(self):
        id = str(self['menu'].getCurrent()[0])
        text = '%s' % (id)
        setup = '%s%s' % (self.name(), "SetupIcons")
        if fileExists("%s/%s" % (setup, text)):
             Console().ePopen("rm -rf %s") % resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/weathericons")
             Console().ePopen("cp -R %s/%s %s %s") % (setup, text, resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/weathericons"))
             self.close()
        else:
            self.close()

    def getPanelmenu(self):
        title = ''
        try:
            results = self.getList()
        except:
            results = []
        if len(results) == 0:
            return False
        self.resultlist = []
        for searchResult in results:
            try:
                self.resultlist.append(searchResult)
            except:
                pass
        self['menu'].l.setList(self.resultlist)
        id = str(self['menu'].getCurrent()[0])
	self.search_poster(id)

    def search_poster(self, id):
                text = '%s' % (id)
                setup = '%s%s' % (self.name(), "SetupIcons")
		filename = '%s/%s.png' % (setup, text)
		if filename is None:
                     filename = resolveFilename(SCOPE_PLUGINS, "Extensions/QuickWeather/NA.png")
                png2 = loadPic(filename, 420, 236, 0, 0, 0, 1)
                self["previem"].instance.setPixmap(png2)

    def getList(self):
		b00klist = []
		setup = '%s%s' % (self.name(), "SetupIcons")
		if os.path.exists(setup) == True:
           		for name in os.listdir(setup):
              			if name.endswith(".png") is True:
                 			bname = name.split(".png")
                      			b00klist.append((bname[0], name))
        	b00klist.sort()
	        return b00klist


class SearchResults(list):
    def __str__(self):
        return "%s" % (repr(self).replace("['", '').replace("']", ''))
