from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Plugins.Plugin import PluginDescriptor

class DeviceInfo(Screen):
    skin = """
        <screen position="250,100" size="650,550" title="Device Info">
          <eLabel backgroundColor="blue" position="70,50" size="420,5" zPosition="2" />	
          <eLabel font="Regular;29" position="70,10" size="400,40" text="PE Device Information" transparent="1" zPosition="2" />	
          <ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DeviceInfo/images/dev_flash.png" position="80,70" size="48,48" />
          <widget source="session.Event_Now" render="Progress" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DeviceInfo/images/device.png" position="160,78" size="100,15" transparent="1" borderWidth="1" borderColor="grey" zPosition="1">
           <convert type="ProgressDiskSpaceInfo">FlashInfo</convert>
          </widget>
          <widget source="session.CurrentService" render="Label" position="160,103" size="475,40" zPosition="1" font="Regular; 16" halign="left" valign="center" transparent="1" noWrap="0">
            <convert type="ProgressDiskSpaceInfo">FlashInfo,Full</convert>
           </widget>
           <widget source="session.CurrentService" render="Label" position="284,148" size="210,15" zPosition="1" font="Regular; 14" halign="left" valign="center" transparent="1" noWrap="0">
            <convert type="ProgressDiskSpaceInfo">HddTemp</convert>
           </widget>
           <ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DeviceInfo/images/dev_hdd.png" position="80,140" size="48,48" />
           <widget source="session.Event_Now" render="Progress" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DeviceInfo/images/device.png" position="160,148" size="100,15" transparent="1" borderWidth="1" borderColor="grey" zPosition="1">
           <convert type="ProgressDiskSpaceInfo">HddInfo</convert>
          </widget>
          <widget source="session.CurrentService" render="Label" position="160,173" size="475,40" zPosition="1" font="Regular; 16" halign="left" valign="center" transparent="1" noWrap="0">
           <convert type="ProgressDiskSpaceInfo">HddInfo,Full</convert>
          </widget>
          <ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DeviceInfo/images/dev_usb.png" position="80,210" size="48,48" />
          <widget source="session.Event_Now" render="Progress" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DeviceInfo/images/device.png" position="160,218" size="100,15" transparent="1" borderWidth="1" borderColor="grey" zPosition="1">
           <convert type="ProgressDiskSpaceInfo">UsbInfo</convert>
          </widget>
          <widget source="session.CurrentService" render="Label" position="160,243" size="475,40" zPosition="1" font="Regular; 16" halign="left" valign="center" transparent="1" noWrap="0">
            <convert type="ProgressDiskSpaceInfo">UsbInfo,Full</convert>
          </widget>
          <ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DeviceInfo/images/dev_ram.png" position="80,280" size="48,48" />
          <widget source="session.Event_Now" render="Progress" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DeviceInfo/images/device.png" position="160,288" size="100,15" transparent="1" borderWidth="1" borderColor="grey" zPosition="1">
           <convert type="ProgressDiskSpaceInfo">MemTotal</convert>
          </widget>
           <widget source="session.CurrentService" render="Label" position="284,358" size="210,15" zPosition="1" font="Regular; 14" halign="left" valign="center" transparent="1" noWrap="0">
            <convert type="ProgressDiskSpaceInfo">LoadAvg</convert>
           </widget>
          <widget source="session.CurrentService" render="Label" position="160,313" size="475,40" zPosition="1" font="Regular; 16" halign="left" valign="center" transparent="1" noWrap="0">
           <convert type="ProgressDiskSpaceInfo">MemTotal,Full</convert>
          </widget>
          <widget source="session.Event_Now" render="Progress" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DeviceInfo/images/device.png" position="160,358" size="100,15" transparent="1" borderWidth="1" borderColor="grey" zPosition="1">
           <convert type="ProgressDiskSpaceInfo">SwapTotal</convert>
          </widget>
          <widget source="session.CurrentService" render="Label" position="160,383" size="475,40" zPosition="1" font="Regular; 16" halign="left" valign="center" transparent="1" noWrap="0">
           <convert type="ProgressDiskSpaceInfo">SwapTotal,Full</convert>
          </widget>
          <ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DeviceInfo/images/dev_swap.png" position="80,350" size="48,48" />
          <ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DeviceInfo/images/dev_cf.png" position="80,420" size="48,48" />
          <widget source="session.Event_Now" render="Progress" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DeviceInfo/images/device.png" position="160,428" size="100,15" transparent="1" borderWidth="1" borderColor="grey" zPosition="1">
           <convert type="ProgressDiskSpaceInfo">CFInfo</convert>
          </widget>
          <widget source="session.CurrentService" render="Label" position="160,453" size="475,40" zPosition="1" font="Regular; 16" halign="left" valign="center" transparent="1" noWrap="0">
            <convert type="ProgressDiskSpaceInfo">CFInfo,Full</convert>
          </widget>
        </screen>"""

    def __init__(self, session, args = 0):
        self.skin = DeviceInfo.skin
        self.session = session
        Screen.__init__(self, session)
	self["actions"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"], 
			{
				"cancel": self.close,
				"ok": self.close,
			})		

def PELock():
    try:
        from pe import gettitle
        petitle = gettitle()
        return petitle
    except:
        return False

def startinfo(session, **kwargs):
	if PELock()==False:
		return
	else:
		session.open(DeviceInfo)

def mainconf(menuid):
    if menuid != "information":                                                  
        return [ ]                                                     
    return [(_("Device"), startinfo, "DeviceInfo", None)] 

def Plugins(**kwargs):
	return [PluginDescriptor(name=_("Device Info"), description=_("Information About Devices"), where=PluginDescriptor.WHERE_MENU, fnc=mainconf),
                PluginDescriptor(name=_("Device Info"), description=_("Information About Devices"), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=startinfo)]
