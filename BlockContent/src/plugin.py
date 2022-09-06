# -*- coding: utf-8 -*-

blockcontent_version = "0.15"

from RecordTimer import parseEvent
from Components.ServiceEventTracker import ServiceEventTracker
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigSubsection, ConfigInteger, ConfigBoolean, ConfigPIN, getConfigListEntry
from enigma import eTimer, eServiceCenter, iPlayableService
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.InputBox import PinInput
from ServiceReference import ServiceReference
from Screens.ParentalControlSetup import ProtectedScreen
from time import time, localtime, strftime
import os
import Screens.Standby

config.plugins.blockcontent = ConfigSubsection()
config.plugins.blockcontent.viewingtime = ConfigInteger(default=0, limits=(0, 30))
config.plugins.blockcontent.reactivetime = ConfigInteger(default=0, limits=(0, 300))
config.plugins.blockcontent.freeview = ConfigInteger(default=24, limits=(0, 24))
config.plugins.blockcontent.casesensitive = ConfigBoolean(default=False)
config.plugins.blockcontent.popup = ConfigBoolean(default=False)
config.plugins.blockcontent.popuptime = ConfigInteger(default=10, limits=(5, 60))
config.plugins.blockcontent.pin = ConfigPIN(default=1111, censor="*")

global blockedcontent_asking
blockedcontent_asking = False


def startConfig(session, **kwargs):
    session.open(BlockContentConfiguration)


def autostart(reason, **kwargs):
    if "session" in kwargs and reason == 0:
        session = kwargs["session"]
        print("[BlockContent] autostart check")
        session.open(BlockContentCheck)


def Plugins(**kwargs):
    	return [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=autostart),
		PluginDescriptor(name="Block Content", description=_("never shown"), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=mainext),
		PluginDescriptor(name=_("Block Content"), description=_("never shown"), where=PluginDescriptor.WHERE_MENU, fnc=mainconf)]


def mainext(session, **kwargs):
    if config.plugins.blockcontent.viewingtime.value == 0:
        session.open(MessageBox, _("Block Content is disabled"), MessageBox.TYPE_ERROR)
    else:
        	session.open(BlockContentEnableDisable)


def mainconf(menuid):
    if menuid != "system":
        return []
    return [(_("Block Content"), startConfig, "blockcontent", None)]


class BlockContentConfiguration(Screen, ConfigListScreen, ProtectedScreen):
    skin = """
        <screen position="center,center" size="600,240" title="Block Content Configuration" >
        <widget name="config" position="0,0" size="600,240" scrollbarMode="showOnDemand" />
        <widget name="buttonred" position="10,200" size="100,40" backgroundColor="red" verticalAlignment="center" horizontalAlignment="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>
        <widget name="buttongreen" position="490,200" size="100,40" backgroundColor="green" verticalAlignment="center" horizontalAlignment="center" zPosition="2"  foregroundColor="white" font="Regular;18"/>
        </screen>"""

    def __init__(self, session, args=0):
	Screen.__init__(self, session)
	ProtectedScreen.__init__(self)
       	self.list = []
        self.list.append(getConfigListEntry(_("Blocking after 1-30 sec [0 = disabled]"), config.plugins.blockcontent.viewingtime))
        self.list.append(getConfigListEntry(_("Freeview after 0-23h [24=disabled]  ]"), config.plugins.blockcontent.freeview))
        self.list.append(getConfigListEntry(_("Reactivate after 0-300 min [0 = disabled]"), config.plugins.blockcontent.reactivetime))
        self.list.append(getConfigListEntry(_("Casesensitive"), config.plugins.blockcontent.casesensitive))
        self.list.append(getConfigListEntry(_("Popup only"), config.plugins.blockcontent.popup))
        self.list.append(getConfigListEntry(_("Popup timeout"), config.plugins.blockcontent.popuptime))
        self.list.append(getConfigListEntry(_("PIN"), config.plugins.blockcontent.pin))
        self.onShown.append(self.setWindowTitle)
       	ConfigListScreen.__init__(self, self.list)

	self.onChangedEntry = []

       	self["buttonred"] = Label(_("Cancel"))
       	self["buttongreen"] = Label(_("OK"))
        self["setupActions"] = ActionMap(["ColorActions", "SetupActions"],
       	{
       		"green": self.save,
        	"red": self.cancel,
            	"save": self.save,
            	"cancel": self.cancel,
            	"ok": self.save,
       	}, 2)

    def setWindowTitle(self):
        self.setTitle(_("Block Content Configuration V%s") % blockcontent_version)

    def save(self):
        for x in self["config"].list:
            x[1].save()
        self.close(True)

    def cancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close(False)

    def pinEntered(self, result):
        if result is None:
            self.cancel()
        elif not result:
            self.session.openWithCallback(self.pinCancel, MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR)

    def pinCancel(self, result):
        self.cancel()

    def protectedWithPin(self):
        return config.plugins.blockcontent.pin.getValue()


class BlockContentEnableDisable(Screen, ProtectedScreen):
    skin = """
        <screen position="center,center" size="350,140" title="Block Content Configuration" >
        </screen>"""

    def __init__(self, session, args=0):
	Screen.__init__(self, session)
	ProtectedScreen.__init__(self)

    def pinCancel(self, result):
        self.close(True)

    def pinEntered(self, result):
	global blockedcontent_deactive
        if result is None:
            self.close()
	elif result:
		if blockedcontent_deactive:
			blockedcontent_deactive = False
               		self.session.openWithCallback(self.pinCancel, MessageBox, _("Block Content is now activated"), MessageBox.TYPE_INFO)
		else:
			blockedcontent_deactive = True
               		self.session.openWithCallback(self.pinCancel, MessageBox, _("Block Content is now deactivated"), MessageBox.TYPE_INFO)
        elif not result:
            self.session.openWithCallback(self.pinCancel, MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR)

    def protectedWithPin(self):
        return config.plugins.blockcontent.pin.getValue()


class BlockContentCheck(Screen):
    skin = """
        <screen position="center,center" size="400,300" title="Block Content Check" >
        </screen>"""

    def __init__(self, session):
        self.skin = BlockContentCheck.skin
	self.session = session
	Screen.__init__(self, session)
	global blockedcontent_deactive
	blockedcontent_deactive = False
	self.blockedcontent_reactive = False
	self.blockedcontent_authorized = "Sesamestrasse"
	self.blockedcontent_check = ""
        self.blockedcontent_begin_time = 0
       	self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
        		iPlayableService.evUpdatedEventInfo: self.EventInfoChanged,
       		})

    def EventInfoChanged(self):
        	service = self.session.nav.getCurrentService()
        old_begin_time = self.blockedcontent_begin_time
        info = service and service.info()
        ptr = info and info.getEvent(0)
        self.blockedcontent_begin_time = ptr and ptr.getBeginTime() or 0
        print("[BlockContent] planning check")
        self.TimerBlockContentCheck = eTimer()
        self.TimerBlockContentCheck.stop()
        self.TimerBlockContentCheck.timeout.get().append(self.CheckBlockContent)
        	self.TimerBlockContentCheck.start(config.plugins.blockcontent.viewingtime.value * 1000, True)

    def CheckBlockContent(self):
	global blockedcontent_deactive
	global blockedcontent_asking
	blockedcontent_asking = False
        self.TimerBlockContentCheck.stop()
	current_hour = int(strftime("%H", localtime()))
        if Screens.Standby.inStandby or config.plugins.blockcontent.viewingtime.value == 0 or config.plugins.blockcontent.freeview.value <= current_hour:
		print("[BlockedContent] resets")
		self.blockedcontent_authorized = ""
		if blockedcontent_deactive:
			blockedcontent_deactive = False
	elif blockedcontent_deactive:
		if config.plugins.blockcontent.reactivetime.value > 0 and not self.blockedcontent_reactive:
		      		print("[BlockContent] reactivate in %s min\n" % config.plugins.blockcontent.reactivetime.value)
		        	self.TimerBlockContentReactivate = eTimer()
		        	self.TimerBlockContentReactivate.stop()
		        	self.TimerBlockContentReactivate.timeout.get().append(self.ReactivateBlockContent)
                			self.TimerBlockContentReactivate.start(config.plugins.blockcontent.reactivetime.value * 60000, True)
				self.blockedcontent_reactive = True
	else:
		eventid = None
		text = ""
		station = ""
		name = ""
		description = ""
		servicerefstr = ""
		serviceref = self.session.nav.getCurrentlyPlayingServiceReference()
		if serviceref is not None:
			servicerefstr = serviceref.toString()
                	 		serviceHandler = eServiceCenter.getInstance()
			info = serviceHandler.info(serviceref)
			station = info.getName(serviceref)
			begin = time()
			event = None
	                service = self.session.nav.getCurrentService()
	                info = service and service.info()
                	        event = info and info.getEvent(0)
                	if event is not None:
                    	curEvent = parseEvent(event)
                    		begin = curEvent[0]
                    			end = curEvent[1]
                    	name = curEvent[2]
                    	description = curEvent[3]
				eventid = curEvent[4]

				text = event.getEventName()
                    			short = event.getShortDescription()
                    			ext = event.getExtendedDescription()
                    			if short and short != text:
                        			text += '\n\n' + short
                    			if ext:
                        			if text:
                            			text += '\n\n'
                        			text += ext
		check = "%s %s %s %s %s" % (servicerefstr, station, name, description, text)
            	if config.plugins.blockcontent.casesensitive.value is False:
			check = check.upper()
		blockedcontent_found = False
		blockedcontent = True
		if os.path.exists("/etc/enigma2/blockedcontent"):
			f = open("/etc/enigma2/blockedcontent")
			while blockedcontent and not blockedcontent_found:
				blockedcontent = f.readline().lstrip().rstrip().rstrip("\r\n")
				if blockedcontent.startswith("userbouquet."):
					if os.path.exists("/etc/enigma2/%s" % blockedcontent):
						blockedbouquet = True
						u = open("/etc/enigma2/%s" % blockedcontent, "r")
						while blockedbouquet and not blockedcontent_found:
							blockedbouquet = u.readline().lstrip().rstrip().rstrip("\r\n")
				 			blockedbouquet = blockedbouquet.replace("#SERVICE", "").replace(" ", "")
							if blockedbouquet.startswith("#") is False and check.find(blockedbouquet) is not -1 and len(blockedbouquet) > 1:
                                    								print("[BlockedContent] %s found in %s" % (blockedbouquet, check))
								blockedcontent_found = True
						u.close()
                    			if config.plugins.blockcontent.casesensitive.value is False:
					blockedcontent = blockedcontent.upper()
				if blockedcontent.startswith("#") is False and check.find(blockedcontent) is not -1 and len(blockedcontent) > 1:
                        					print("[BlockedContent] %s found in %s" % (blockedcontent, check))
					blockedcontent_found = True
			f.close()
		else:
			print("[BlockedContent] /etc/enigma2/blockedcontent not found")
            		if self.blockedcontent_authorized != check:
			self.blockedcontent_authorized = ""
            		if blockedcontent_found and self.blockedcontent_authorized != check and not blockedcontent_asking:
                			if config.plugins.blockcontent.popup.value is False:
					blockedcontent_asking = True
					print("[BlockedContent] asks for PIN")
					self.prev_running_service = serviceref
					self.blockedcontent_check = check
					self.session.nav.stopService()
					try:
                        						self.session.openWithCallback(self.pinEntered, PinInput, pinList=[config.plugins.blockcontent.pin.getValue()], triesEntry=self.getTriesEntry(), title=_("Please enter the correct pin code"), windowTitle=_("Enter pin code"))
					except:
						self.session.nav.playService(self.prev_running_service)
						blockedcontent_asking = False
						pass
                			else:
				        self.session.open(MessageBox, _("Block Content found %s") % blockedcontent, MessageBox.TYPE_WARNING, timeout=config.plugins.blockcontent.popuptime.value)

    def getTriesEntry(self):
        return config.ParentalControl.retries.setuppin

    def pinEntered(self, result):
	global blockedcontent_asking
        if result is None:
		pass
        elif not result:
		pass
        else:
		blockedcontent_asking = False
		self.session.nav.playService(self.prev_running_service)
		self.blockedcontent_authorized = self.blockedcontent_check

    def ReactivateBlockContent(self):
	print("[BlockContent] reactivated")
	global blockedcontent_deactive
	blockedcontent_deactive = False
	self.blockedcontent_authorized = ""
	self.blockedcontent_reactive = False
