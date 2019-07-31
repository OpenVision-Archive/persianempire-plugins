from Screens.Screen import Screen
from Components.ServiceScan import ServiceScan as SimpleCScan
from Components.ProgressBar import ProgressBar
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.FIFOList import FIFOList
from Components.Sources.FrontendInfo import FrontendInfo
from enigma import eServiceCenter

class SimpleServiceScanSummary(Screen):
	skin = """
	<screen position="0,0" size="132,64">
		<widget name="Title" position="6,4" size="120,42" font="Regular;16" transparent="1" />
		<widget name="scan_progress" position="6,50" zPosition="1" borderWidth="1" size="56,12" backgroundColor="dark" />
		<widget name="Service" position="6,22" size="120,26" font="Regular;12" transparent="1" />
	</screen>"""

	def __init__(self, session, parent, showStepSlider = True):
		Screen.__init__(self, session, parent)

		self["Title"] = Label(parent.title or _("Service scan"))
		self["Service"] = Label(_("No service"))
		self["scan_progress"] = ProgressBar()

	def updateProgress(self, value):
		self["scan_progress"].setValue(value)

	def updateService(self, name):
		self["Service"].setText(name)

class SimpleServiceScan(Screen):
	skin = """
		<screen name="SimpleServiceScan" position="340,134" size="600,502" title="Simple service scan">
			<widget source="FrontendInfo" render="Pixmap" pixmap="icons/scan-s.png" position="15,15" size="64,64" transparent="1" alphatest="on">
				<convert type="FrontendInfo">TYPE</convert>
				<convert type="ValueRange">0,0</convert>
				<convert type="ConditionalShowHide" />
			</widget>
			<widget source="FrontendInfo" render="Pixmap" pixmap="icons/scan-c.png" position="15,15" size="64,64" transparent="1" alphatest="on">
				<convert type="FrontendInfo">TYPE</convert>
				<convert type="ValueRange">1,1</convert>
				<convert type="ConditionalShowHide" />
			</widget>
			<widget source="FrontendInfo" render="Pixmap" pixmap="icons/scan-t.png" position="15,15" size="64,64" transparent="1" alphatest="on">
				<convert type="FrontendInfo">TYPE</convert>
				<convert type="ValueRange">2,2</convert>
				<convert type="ConditionalShowHide" />
			</widget>
			<widget name="network" position="100,25" size="430,25" font="Regular;22" />
			<widget name="transponder" position="100,55" size="430,25" font="Regular;22" />
			<widget name="scan_state" position="20,105" size="560,25" zPosition="2" font="Regular;22" />
			<widget name="pass" position="20,105" size="560,25" font="Regular;22" />
			<widget name="scan_progress" position="20,140" size="560,20" pixmap="progress_big.png" borderWidth="1" borderColor="uncccccc" />
			<!--widget name="servicelist" position="20,175" size="560,300" scrollbarMode="showOnDemand" /-->
			<widget name="servicelist" position="20,175" size="560,300" />
		</screen>"""

	def ok(self):
		print "ok"
		if self["scan"].isDone():
			if `self.currentInfobar`.endswith(".InfoBar'>"):
				if self.currentServiceList is not None:
					self.currentServiceList.setTvMode()
					bouquets = self.currentServiceList.getBouquetList()
					for x in bouquets:
						if x[0] == 'Last Scanned':
							self.currentServiceList.setRoot(x[1])
							services = eServiceCenter.getInstance().list(self.currentServiceList.servicelist.getRoot())
							channels = services and services.getContent("R", True)
							if channels:
								self.session.postScanService = channels[0]
								self.currentServiceList.addToHistory(channels[0])
			self.close()

	def cancel(self):
		self.close()

	def __init__(self, session, scanList):
		self.skin = SimpleServiceScan.skin
		Screen.__init__(self, session)

		self.scanList = scanList

		if hasattr(session, 'infobar'):
			self.currentInfobar = session.infobar
			self.currentServiceList = self.currentInfobar.servicelist
			if self.session.pipshown and self.currentServiceList:
				if self.currentServiceList.dopipzap:
					self.currentServiceList.togglePipzap()
				del self.session.pip
				self.session.pipshown = False
		else:
			self.currentInfobar = None

		self.session.nav.stopService()

		self["scan_progress"] = ProgressBar()
		self["scan_state"] = Label(_("Scan state"))
		self["network"] = Label()
		self["transponder"] = Label()

		self["pass"] = Label("")
		self["servicelist"] = FIFOList(len=15000)
		self["FrontendInfo"] = FrontendInfo()

		self["actions"] = ActionMap(["DirectionActions", "OkCancelActions"],
		{
			"cancel": self.cancel,
			"ok": self.ok,
			"left": self["servicelist"].pageUp,
			"right": self["servicelist"].pageDown,
			"up": self["servicelist"].pageUp,
			"down": self["servicelist"].pageDown,
			"pageUp": self["servicelist"].pageUp,
			"pageDown": self["servicelist"].pageDown
		}, -2)

		self.onFirstExecBegin.append(self.doServiceScan)

	def doServiceScan(self):
		self["scan"] = SimpleCScan(self["scan_progress"], self["scan_state"], self["servicelist"], self["pass"], self.scanList, self["network"], self["transponder"], self["FrontendInfo"], self.session.summary)

	def createSummary(self):
		print "SimpleServiceScanCreateSummary"
		return SimpleServiceScanSummary