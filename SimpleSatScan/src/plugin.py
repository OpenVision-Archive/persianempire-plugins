#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigYesNo, ConfigInteger, getConfigListEntry, ConfigEnableDisable
from Components.ActionMap import NumberActionMap, ActionMap
from Components.ConfigList import ConfigListScreen
from Components.NimManager import nimmanager, getConfigSatlist
from Components.Label import Label
from Screens.MessageBox import MessageBox
from enigma import eTimer, eDVBFrontendParametersSatellite, eComponentScan, eDVBResourceManager
from Components.Sources.FrontendStatus import FrontendStatus
from Components.TuneTest import Tuner
from ServiceScan import SimpleServiceScan


class SimpleSatScan(ConfigListScreen, Screen):
	skin = """
	<screen position="center,center" size="520,480" title="Simple satellite scan">
		<!-- little tune status -->
		<eLabel name="pos" text="Current position:" position="10,10" size="210,20" font="Regular;19" halign="right" transparent="1" />
		<widget name="status" position="230,10" size="260,20" font="Console;19" valign="center" foregroundColor="#f8f711" transparent="1" />
		<!-- dB -->
		<!--widget source="Frontend" render="Label" position="190,10" zPosition="2" size="260,20" font="Regular;19" foregroundColor="#02f408" halign="center" valign="center" transparent="1"-->
		<widget source="Frontend" render="Label" position="190,35" zPosition="2" size="260,20" font="Regular;19" halign="center" valign="center" transparent="1">
			<convert type="FrontendInfo">SNRdB</convert>
		</widget>
		<!-- SNR -->
		<eLabel name="snr" text="SNR:" position="120,35" size="60,22" font="Regular;21" halign="right" transparent="1" />
		<widget source="Frontend" render="Progress" position="190,35" size="260,20" pixmap="bar_snr.png" borderWidth="2" borderColor="#cccccc">
			<convert type="FrontendInfo">SNR</convert>
		</widget>
		<widget source="Frontend" render="Label" position="460,35" size="60,22" font="Regular;21">
			<convert type="FrontendInfo">SNR</convert>
		</widget>
		<!-- Lock -->
		<eLabel name="lock" text="LOCK:" position="10,35" size="60,22" font="Regular;21" halign="right" transparent="1" />
		<widget source="Frontend" render="Pixmap" pixmap="icons/lock_on.png" position="80,32" zPosition="1" size="38,31" alphatest="on">
			<convert type="FrontendInfo">LOCK</convert>
			<convert type="ConditionalShowHide" />
		</widget>
		<widget source="Frontend" render="Pixmap" pixmap="icons/lock_off.png" position="80,32" zPosition="1" size="38,31" alphatest="on">
			<convert type="FrontendInfo">LOCK</convert>
			<convert type="ConditionalShowHide">Invert</convert>
		</widget>
		<!-- AGC -->
		<eLabel name="agc" text="AGC:" position="120,60" size="60,22" font="Regular;21" halign="right" transparent="1" />
		<widget source="Frontend" render="Progress" position="190,60" size="260,20" pixmap="bar_snr.png" borderWidth="2" borderColor="#cccccc">
			<convert type="FrontendInfo">AGC</convert>
		</widget>
		<widget source="Frontend" render="Label" position="460,60" size="60,22" font="Regular;21">
			<convert type="FrontendInfo">AGC</convert>
		</widget>
		<!-- BER -->
		<eLabel name="ber" text="BER:" position="120,85" size="60,22" font="Regular;21" halign="right" transparent="1" />
		<widget source="Frontend" render="Progress" position="190,85" size="260,20" pixmap="bar_ber.png" borderWidth="2" borderColor="#cccccc">
			<convert type="FrontendInfo">BER</convert>
		</widget>
		<widget source="Frontend" render="Label" position="460,85" size="60,22" font="Regular;21">
			<convert type="FrontendInfo">BER</convert>
		</widget>
		<!-- config -->
		<widget name="config" position="10,120" size="500,320" scrollbarMode="showOnDemand" transparent="1" />
		<widget name="introduction" position="10,450" size="500,25" font="Regular;20" halign="center" valign="center" />
	</screen>"""

	def __init__(self, session):
		self.skin = SimpleSatScan.skin
		Screen.__init__(self, session)

		self.initcomplete = False
		self.frontend = None
		self.prev_ref = False
		self.oldref = None
		self.updateSatList()
		self.service = session and session.nav.getCurrentService()
		self.feinfo = None
		frontendData = None
		if self.service is not None:
			self.feinfo = self.service.frontendInfo()
			frontendData = self.feinfo and self.feinfo.getAll(True)

		self.createConfig(frontendData)

		del self.feinfo
		del self.service
		self["Frontend"] = FrontendStatus(frontend_source=lambda: self.frontend, update_interval=100)
		self["actions"] = NumberActionMap(["SetupActions"],
		{
			"ok": self.keyGo,
			"cancel": self.keyCancel,
		}, -2)

		self.list = []
		self.tpslist = []
		self.tpslist_idx = 0
		self.tuneTimer = eTimer()
		self.tuneTimer.callback.append(self.updateTuneStatus)

		ConfigListScreen.__init__(self, self.list)
		if not self.scan_nims.value == "":
			self.createSetup()
			self.feid = int(self.scan_nims.value)
			orbpos = "??"
			if len(self.satList) > self.feid and len(self.scan_satselection) > self.feid and len(self.satList[self.feid]):
				orbpos = self.OrbToStr(self.satList[self.feid][self.scan_satselection[self.feid].index][0])
			self["status"] = Label(orbpos + ": " + str(self.scan_sat.frequency.value) + " " + self.PolToStr(self.scan_sat.polarization.value))
			self["introduction"] = Label(_("Press OK to start the scan."))
		else:
			self["introduction"] = Label(_("Nothing to scan!\nPlease setup your tuner settings before you start a service scan."))
			self["status"] = Label("")
			self.feid = None

		self.initFrontend()
		self.initcomplete = self.feid != None

	def openFrontend(self):
		res_mgr = eDVBResourceManager.getInstance()
		if res_mgr:
			self.raw_channel = res_mgr.allocateRawChannel(self.feid)
			if self.raw_channel:
				self.frontend = self.raw_channel.getFrontend()
				if self.frontend:
					return True
		return False

	def initFrontend(self):
		if self.oldref is None:
			self.oldref = self.session.nav.getCurrentlyPlayingServiceReference()
		if not self.openFrontend():
			self.prev_ref = True
			self.session.nav.stopService()
			if not self.openFrontend():
				if self.session.pipshown:
					self.session.pipshown = False
					del self.session.pip
					if not self.openFrontend():
						self.frontend = None
		self.tuner = Tuner(self.frontend)
		self.retune(None)

	def deInitFrontend(self):
		if self.frontend:
			self.frontend = None
			del self.raw_channel

	def updateTuneStatus(self):
		if not self.frontend:
			return
		stop = False
		dict = {}
		self.frontend.getFrontendStatus(dict)
		if dict["tuner_state"] == "TUNING":
			self.tuneTimer.start(100, True)
		else:
			if dict["tuner_state"] == "LOSTLOCK" or dict["tuner_state"] == "FAILED":
				self.tpslist_idx += 1
				if self.tpslist_idx >= len(self.tpslist):
					stop = True
					self["status"].setText("Search failed!")
					self.tpslist_idx = 0
			elif dict["tuner_state"] == "LOCKED":
				stop = True

			if not stop:
				self["status"].setText(self.OrbToStr(self.tpslist[self.tpslist_idx][5]) + ": " + str(self.tpslist[self.tpslist_idx][0]) + " " + self.PolToStr(self.tpslist[self.tpslist_idx][2]))
				self.tune(self.tpslist[self.tpslist_idx])
				self.tuneTimer.start(100, True)

	def tune(self, transponder):
		if self.initcomplete:
			if transponder is not None and self.tuner is not None:
				self.tuner.tune(transponder)

	def retune(self, configElement):
		self.tuneTimer.stop()
		if self.scan_nims == []:
			return
		if self.scan_nims.value == "":
			return
		self.tpslist_idx = 0
		tpslist = []
		status_text = ""
		multi_tune = False
		index_to_scan = int(self.scan_nims.value)
		if len(self.satList) <= index_to_scan:
			return
		if len(self.scan_satselection) <= index_to_scan:
			return

		nim = nimmanager.nim_slots[index_to_scan]
		if not nim.isCompatible("DVB-S"):
			return

		nimsats = self.satList[index_to_scan]
		selsatidx = self.scan_satselection[index_to_scan].index
		if self.scan_type.value == "single_transponder":
			if len(nimsats):
				orbpos = nimsats[selsatidx][0]
				if self.scan_sat.system.value == eDVBFrontendParametersSatellite.System_DVB_S:
					fec = self.scan_sat.fec.value
				else:
					fec = self.scan_sat.fec_s2.value
				tpslist.append((self.scan_sat.frequency.value,
						self.scan_sat.symbolrate.value,
						self.scan_sat.polarization.value,
						fec,
						self.scan_sat.inversion.value,
						orbpos,
						self.scan_sat.system.value,
						self.scan_sat.modulation.value,
						self.scan_sat.rolloff.value,
						self.scan_sat.pilot.value))
		elif self.scan_type.value == "predefined_transponder":
			if len(nimsats):
				orbpos = nimsats[selsatidx][0]
				index = self.scan_transponders.index
				if configElement and configElement._value == str(orbpos):
					index = 0
				tps = nimmanager.getTransponders(orbpos)
				if len(tps) > index:
					x = tps[index]
					tpslist.append((x[1] / 1000, x[2] / 1000, x[3], x[4], x[7], orbpos, x[5], x[6], x[8], x[9]))
		elif self.scan_type.value == "single_satellite":
			if len(nimsats):
				multi_tune = True
				orbpos = nimsats[selsatidx][0]
				tps = nimmanager.getTransponders(orbpos)
				for x in tps:
					if x[0] == 0:
						tpslist.append((x[1] / 1000, x[2] / 1000, x[3], x[4], x[7], orbpos, x[5], x[6], x[8], x[9]))
		elif self.scan_type.value == "multisat":
			if len(self.multiscanlist):
				for sat in self.multiscanlist:
					if sat[1].value or len(tpslist) == 0:
						if len(tpslist):
							del tpslist[:]
						tps = nimmanager.getTransponders(sat[0])
						for x in tps:
							if x[0] == 0:
								tpslist.append((x[1] / 1000, x[2] / 1000, x[3], x[4], x[7], sat[0], x[5], x[6], x[8], x[9]))
						if sat[1].value:
							multi_tune = True
							break
			else:
				status_text = "Multiscanlist empty!"
				SatList = nimmanager.getSatListForNim(index_to_scan)
				for sat in SatList:
					tps = nimmanager.getTransponders(sat[0])
					for x in tps:
						if x[0] == 0:
							tpslist.append((x[1] / 1000, x[2] / 1000, x[3], x[4], x[7], sat[0], x[5], x[6], x[8], x[9]))
					if len(tpslist):
						break

		self.tpslist = tpslist
		if len(self.tpslist):
			status_text = self.OrbToStr(self.tpslist[self.tpslist_idx][5]) + ": " + str(self.tpslist[self.tpslist_idx][0]) + " " + self.PolToStr(self.tpslist[self.tpslist_idx][2])
			self.tune(self.tpslist[self.tpslist_idx])
			if multi_tune:
				self.tuneTimer.start(100, True)
		self["status"].setText(status_text)

	def OrbToStr(self, orbpos=-1):
		if orbpos == -1 or orbpos > 3600:
			return "??"
		if orbpos > 1800:
			return "%d.%dW" % ((3600 - orbpos) / 10, (3600 - orbpos) % 10)
		else:
			return "%d.%dE" % (orbpos / 10, orbpos % 10)

	def PolToStr(self, pol):
		return (pol == 0 and "H") or (pol == 1 and "V") or (pol == 2 and "L") or (pol == 3 and "R") or "??"

	def FecToStr(self, fec):
		return (fec == 0 and "Auto") or (fec == 1 and "1/2") or (fec == 2 and "2/3") or (fec == 3 and "3/4") or \
			(fec == 4 and "5/6") or (fec == 5 and "7/8") or (fec == 6 and "8/9") or (fec == 7 and "3/5") or \
			(fec == 8 and "4/5") or (fec == 9 and "9/10") or (fec == 15 and "None") or "Unknown"

	def updateTranspondersList(self, orbpos):
		if orbpos is not None:
			index = 0
			list = []
			tps = nimmanager.getTransponders(orbpos)
			for x in tps:
				if x[0] == 0:
					s = str(x[1] / 1000) + " " + self.PolToStr(x[3]) + " / " + str(x[2] / 1000) + " / " + self.FecToStr(x[4])
					list.append((str(index), s))
					index += 1
			self.scan_transponders = ConfigSelection(choices=list, default="0")
			self.scan_transponders.addNotifier(self.retune, initial_call=False)

	def updateSatList(self):
		self.satList = []
		for slot in nimmanager.nim_slots:
			if slot.isCompatible("DVB-S"):
				self.satList.append(nimmanager.getSatListForNim(slot.slot))

	def createSetup(self):
		self.tuneTimer.stop()
		self.list = []
		self.multiscanlist = []
		index_to_scan = int(self.scan_nims.value)

		self.tunerEntry = getConfigListEntry(_("Tuner"), self.scan_nims)
		self.list.append(self.tunerEntry)

		if self.scan_nims == []:
			return

		self.typeOfScanEntry = None
		self.systemEntry = None
		self.satelliteEntry = None
		self.modulationEntry = None
		self.scan_networkScan.value = False
		nim = nimmanager.nim_slots[index_to_scan]
		if nim.isCompatible("DVB-S"):
			self.typeOfScanEntry = getConfigListEntry(_("Type of scan"), self.scan_type)
			self.list.append(self.typeOfScanEntry)

			if self.scan_type.value == "single_transponder":
				self.updateSatList()
				sat = self.satList[index_to_scan][self.scan_satselection[index_to_scan].index]
				self.updateTranspondersList(sat[0])
				if nim.isCompatible("DVB-S2"):
					self.systemEntry = getConfigListEntry(_('System'), self.scan_sat.system)
					self.list.append(self.systemEntry)
				else:
					self.scan_sat.system.value = eDVBFrontendParametersSatellite.System_DVB_S
				self.list.append(getConfigListEntry(_('Satellite'), self.scan_satselection[index_to_scan]))
				self.list.append(getConfigListEntry(_('Frequency'), self.scan_sat.frequency))
				self.list.append(getConfigListEntry(_('Inversion'), self.scan_sat.inversion))
				self.list.append(getConfigListEntry(_('Symbol rate'), self.scan_sat.symbolrate))
				self.list.append(getConfigListEntry(_("Polarity"), self.scan_sat.polarization))
				if self.scan_sat.system.value == eDVBFrontendParametersSatellite.System_DVB_S:
					self.list.append(getConfigListEntry(_("FEC"), self.scan_sat.fec))
				elif self.scan_sat.system.value == eDVBFrontendParametersSatellite.System_DVB_S2:
					self.list.append(getConfigListEntry(_("FEC"), self.scan_sat.fec_s2))
					self.modulationEntry = getConfigListEntry(_('Modulation'), self.scan_sat.modulation)
					self.list.append(self.modulationEntry)
					self.list.append(getConfigListEntry(_('Rolloff'), self.scan_sat.rolloff))
					self.list.append(getConfigListEntry(_('Pilot'), self.scan_sat.pilot))
			elif self.scan_type.value == "predefined_transponder":
				self.updateSatList()
				self.satelliteEntry = getConfigListEntry(_('Satellite'), self.scan_satselection[index_to_scan])
				self.list.append(self.satelliteEntry)
				sat = self.satList[index_to_scan][self.scan_satselection[index_to_scan].index]
				self.updateTranspondersList(sat[0])
				self.list.append(getConfigListEntry(_('Transponder'), self.scan_transponders))
			elif self.scan_type.value == "single_satellite":
				self.updateSatList()
				sat = self.satList[index_to_scan][self.scan_satselection[index_to_scan].index]
				self.updateTranspondersList(sat[0])
				print(self.scan_satselection[index_to_scan])
				self.list.append(getConfigListEntry(_("Satellite"), self.scan_satselection[index_to_scan]))
				self.scan_networkScan.value = True
			elif self.scan_type.value == "multisat":
				tlist = []
				SatList = nimmanager.getSatListForNim(index_to_scan)
				for x in SatList:
					if self.Satexists(tlist, x[0]) == 0:
						tlist.append(x[0])
						sat = ConfigEnableDisable(default=self.scan_type.value.find("_yes") != -1 and True or False)
						configEntry = getConfigListEntry(nimmanager.getSatDescription(x[0]), sat)
						self.list.append(configEntry)
						self.multiscanlist.append((x[0], sat))
						sat.addNotifier(self.retune, initial_call=False)
				self.scan_networkScan.value = True

		self.list.append(getConfigListEntry(_("Network scan"), self.scan_networkScan))
		self.list.append(getConfigListEntry(_("Clear before scan"), self.scan_clearallservices))
		self.list.append(getConfigListEntry(_("Only Free scan"), self.scan_onlyfree))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def Satexists(self, tlist, pos):
		for x in tlist:
			if x == pos:
				return 1
		return 0

	def newConfig(self):
		cur = self["config"].getCurrent()
		if cur == self.typeOfScanEntry or \
			cur == self.tunerEntry or \
			cur == self.systemEntry or \
			cur == self.satelliteEntry or \
			(self.modulationEntry and self.systemEntry[1].value == eDVBFrontendParametersSatellite.System_DVB_S2 and cur == self.modulationEntry):
			self.createSetup()

	def createConfig(self, frontendData):
		defaultSat = {
			"orbpos": 192,
			"system": eDVBFrontendParametersSatellite.System_DVB_S,
			"frequency": 11836,
			"inversion": eDVBFrontendParametersSatellite.Inversion_Unknown,
			"symbolrate": 27500,
			"polarization": eDVBFrontendParametersSatellite.Polarisation_Horizontal,
			"fec": eDVBFrontendParametersSatellite.FEC_Auto,
			"fec_s2": eDVBFrontendParametersSatellite.FEC_9_10,
			"modulation": eDVBFrontendParametersSatellite.Modulation_QPSK}

		if frontendData is not None:
			ttype = frontendData.get("tuner_type", "UNKNOWN")
			if ttype == "DVB-S":
				defaultSat["system"] = frontendData.get("system", eDVBFrontendParametersSatellite.System_DVB_S)
				defaultSat["frequency"] = frontendData.get("frequency", 0) / 1000
				defaultSat["inversion"] = frontendData.get("inversion", eDVBFrontendParametersSatellite.Inversion_Unknown)
				defaultSat["symbolrate"] = frontendData.get("symbol_rate", 0) / 1000
				defaultSat["polarization"] = frontendData.get("polarization", eDVBFrontendParametersSatellite.Polarisation_Horizontal)
				if defaultSat["system"] == eDVBFrontendParametersSatellite.System_DVB_S2:
					defaultSat["fec_s2"] = frontendData.get("fec_inner", eDVBFrontendParametersSatellite.FEC_Auto)
					defaultSat["rolloff"] = frontendData.get("rolloff", eDVBFrontendParametersSatellite.RollOff_alpha_0_35)
					defaultSat["pilot"] = frontendData.get("pilot", eDVBFrontendParametersSatellite.Pilot_Unknown)
				else:
					defaultSat["fec"] = frontendData.get("fec_inner", eDVBFrontendParametersSatellite.FEC_Auto)
				defaultSat["modulation"] = frontendData.get("modulation", eDVBFrontendParametersSatellite.Modulation_QPSK)
				defaultSat["orbpos"] = frontendData.get("orbital_position", 0)

		self.scan_sat = ConfigSubsection()

		self.scan_type = ConfigSelection(default="single_transponder", choices=[("single_transponder", _("Single transponder")), ("predefined_transponder", _("Predefined transponder")), ("single_satellite", _("Single satellite")), ("multisat", _("Multisat"))])
		self.scan_transponders = None
		self.scan_clearallservices = ConfigSelection(default="no", choices=[("no", _("No")), ("yes", _("Yes")), ("yes_hold_feeds", _("Yes (keep feeds)"))])
		self.scan_onlyfree = ConfigYesNo(default=False)
		self.scan_networkScan = ConfigYesNo(default=False)

		nim_list = []
		for n in nimmanager.nim_slots:
			if n.config_mode == "nothing":
				continue
			if n.config_mode == "advanced" and len(nimmanager.getSatListForNim(n.slot)) < 1:
				continue
			if n.config_mode in ("loopthrough", "satposdepends"):
				root_id = nimmanager.sec.getRoot(n.slot_id, int(n.config.connectedTo.value))
				if n.type == nimmanager.nim_slots[root_id].type:
					continue
			if n.isCompatible("DVB-S"):
				nim_list.append((str(n.slot), n.friendly_full_description))

		self.scan_nims = ConfigSelection(choices=nim_list)

		self.scan_sat.system = ConfigSelection(default=defaultSat["system"], choices=[
			(eDVBFrontendParametersSatellite.System_DVB_S, _("DVB-S")),
			(eDVBFrontendParametersSatellite.System_DVB_S2, _("DVB-S2"))])
		self.scan_sat.frequency = ConfigInteger(default=defaultSat["frequency"], limits=(1, 99999))
		self.scan_sat.inversion = ConfigSelection(default=defaultSat["inversion"], choices=[
			(eDVBFrontendParametersSatellite.Inversion_Off, _("off")),
			(eDVBFrontendParametersSatellite.Inversion_On, _("on")),
			(eDVBFrontendParametersSatellite.Inversion_Unknown, _("Auto"))])
		self.scan_sat.symbolrate = ConfigInteger(default=defaultSat["symbolrate"], limits=(1, 99999))
		self.scan_sat.polarization = ConfigSelection(default=defaultSat["polarization"], choices=[
			(eDVBFrontendParametersSatellite.Polarisation_Horizontal, _("horizontal")),
			(eDVBFrontendParametersSatellite.Polarisation_Vertical, _("vertical")),
			(eDVBFrontendParametersSatellite.Polarisation_CircularLeft, _("circular left")),
			(eDVBFrontendParametersSatellite.Polarisation_CircularRight, _("circular right"))])
		self.scan_sat.fec = ConfigSelection(default=defaultSat["fec"], choices=[
			(eDVBFrontendParametersSatellite.FEC_Auto, _("Auto")),
			(eDVBFrontendParametersSatellite.FEC_1_2, "1/2"),
			(eDVBFrontendParametersSatellite.FEC_2_3, "2/3"),
			(eDVBFrontendParametersSatellite.FEC_3_4, "3/4"),
			(eDVBFrontendParametersSatellite.FEC_5_6, "5/6"),
			(eDVBFrontendParametersSatellite.FEC_7_8, "7/8"),
			(eDVBFrontendParametersSatellite.FEC_None, _("None"))])
		self.scan_sat.fec_s2 = ConfigSelection(default=defaultSat["fec_s2"], choices=[
			(eDVBFrontendParametersSatellite.FEC_1_2, "1/2"),
			(eDVBFrontendParametersSatellite.FEC_2_3, "2/3"),
			(eDVBFrontendParametersSatellite.FEC_3_4, "3/4"),
			(eDVBFrontendParametersSatellite.FEC_3_5, "3/5"),
			(eDVBFrontendParametersSatellite.FEC_4_5, "4/5"),
			(eDVBFrontendParametersSatellite.FEC_5_6, "5/6"),
			(eDVBFrontendParametersSatellite.FEC_6_7, "6/7"),
			(eDVBFrontendParametersSatellite.FEC_7_8, "7/8"),
			(eDVBFrontendParametersSatellite.FEC_8_9, "8/9"),
			(eDVBFrontendParametersSatellite.FEC_9_10, "9/10")])
		self.scan_sat.modulation = ConfigSelection(default=defaultSat["modulation"], choices=[
			(eDVBFrontendParametersSatellite.Modulation_QPSK, "QPSK"),
			(eDVBFrontendParametersSatellite.Modulation_8PSK, "8PSK")])
		self.scan_sat.rolloff = ConfigSelection(default=defaultSat.get("rolloff", eDVBFrontendParametersSatellite.RollOff_alpha_0_35), choices=[
			(eDVBFrontendParametersSatellite.RollOff_alpha_0_35, "0.35"),
			(eDVBFrontendParametersSatellite.RollOff_alpha_0_25, "0.25"),
			(eDVBFrontendParametersSatellite.RollOff_alpha_0_20, "0.20")])
		self.scan_sat.pilot = ConfigSelection(default=defaultSat.get("pilot", eDVBFrontendParametersSatellite.Pilot_Unknown), choices=[
			(eDVBFrontendParametersSatellite.Pilot_Off, _("off")),
			(eDVBFrontendParametersSatellite.Pilot_On, _("on")),
			(eDVBFrontendParametersSatellite.Pilot_Unknown, _("Auto"))])

		self.scan_scansat = {}
		for sat in nimmanager.satList:
			self.scan_scansat[sat[0]] = ConfigYesNo(default=False)

		self.scan_satselection = []
		for slot in nimmanager.nim_slots:
			if slot.isCompatible("DVB-S"):
				x = getConfigSatlist(defaultSat["orbpos"], self.satList[slot.slot])
				x.addNotifier(self.retune, initial_call=False)
				self.scan_satselection.append(x)
			else:
				self.scan_satselection.append(None)

		for x in (self.scan_nims, self.scan_type, self.scan_sat.frequency,
			self.scan_sat.inversion, self.scan_sat.symbolrate,
			self.scan_sat.polarization, self.scan_sat.fec, self.scan_sat.pilot,
			self.scan_sat.fec_s2, self.scan_sat.fec, self.scan_sat.modulation,
			self.scan_sat.rolloff, self.scan_sat.system):
			x.addNotifier(self.retune, initial_call=False)

		return True

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.newConfig()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.newConfig()

	def addSatTransponder(self, tlist, frequency, symbol_rate, polarisation, fec, inversion, orbital_position, system, modulation, rolloff, pilot):
		print("Add Sat: frequ: " + str(frequency) + " symbol: " + str(symbol_rate) + " pol: " + str(polarisation) + " fec: " + str(fec) + " inversion: " + str(inversion) + " modulation: " + str(modulation) + " system: " + str(system) + " rolloff" + str(rolloff) + " pilot" + str(pilot))
		print("orbpos: " + str(orbital_position))
		parm = eDVBFrontendParametersSatellite()
		parm.modulation = modulation
		parm.system = system
		parm.frequency = frequency * 1000
		parm.symbol_rate = symbol_rate * 1000
		parm.polarisation = polarisation
		parm.fec = fec
		parm.inversion = inversion
		parm.orbital_position = orbital_position
		parm.rolloff = rolloff
		parm.pilot = pilot
		tlist.append(parm)

	def getInitialTransponderList(self, tlist, pos):
		list = nimmanager.getTransponders(pos)
		for x in list:
			if x[0] == 0:
				parm = eDVBFrontendParametersSatellite()
				parm.frequency = x[1]
				parm.symbol_rate = x[2]
				parm.polarisation = x[3]
				parm.fec = x[4]
				parm.inversion = x[7]
				parm.orbital_position = pos
				parm.system = x[5]
				parm.modulation = x[6]
				parm.rolloff = x[8]
				parm.pilot = x[9]
				tlist.append(parm)

	def keyGo(self):
		if self.scan_nims.value == "":
			return
		self.tuneTimer.stop()
		self.deInitFrontend()
		index_to_scan = int(self.scan_nims.value)
		self.feid = index_to_scan
		tlist = []
		flags = None
		startScan = True
		removeAll = True
		self.prev_ref = True
		if self.scan_nims == []:
			self.session.open(MessageBox, _("No tuner is enabled!\nPlease setup your tuner settings before you start a service scan."), MessageBox.TYPE_ERROR)
			return

		nim = nimmanager.nim_slots[index_to_scan]
		if not nim.isCompatible("DVB-S"):
			return
		if self.scan_type.value.find("_transponder") != -1:
			assert len(self.satList) > index_to_scan
			assert len(self.scan_satselection) > index_to_scan

			nimsats = self.satList[index_to_scan]
			selsatidx = self.scan_satselection[index_to_scan].index

			if len(nimsats):
				orbpos = nimsats[selsatidx][0]
				if self.scan_type.value == "single_transponder":
					if self.scan_sat.system.value == eDVBFrontendParametersSatellite.System_DVB_S:
						fec = self.scan_sat.fec.value
					else:
						fec = self.scan_sat.fec_s2.value
					self.addSatTransponder(tlist, self.scan_sat.frequency.value,
								self.scan_sat.symbolrate.value,
								self.scan_sat.polarization.value,
								fec,
								self.scan_sat.inversion.value,
								orbpos,
								self.scan_sat.system.value,
								self.scan_sat.modulation.value,
								self.scan_sat.rolloff.value,
								self.scan_sat.pilot.value)
				elif self.scan_type.value == "predefined_transponder":
					tps = nimmanager.getTransponders(orbpos)
					if len(tps) > self.scan_transponders.index:
						x = tps[self.scan_transponders.index]
						self.addSatTransponder(tlist, x[1] / 1000, x[2] / 1000, x[3], x[4], x[7], orbpos, x[5], x[6], x[8], x[9])
			removeAll = False
		elif self.scan_type.value == "single_satellite":
			sat = self.satList[index_to_scan][self.scan_satselection[index_to_scan].index]
			self.getInitialTransponderList(tlist, sat[0])
		elif self.scan_type.value.find("multisat") != -1:
			SatList = nimmanager.getSatListForNim(index_to_scan)
			for x in self.multiscanlist:
				if x[1].value:
					print("   " + str(x[0]))
					self.getInitialTransponderList(tlist, x[0])

		flags = self.scan_networkScan.value and eComponentScan.scanNetworkSearch or 0

		tmp = self.scan_clearallservices.value
		if tmp == "yes":
			flags |= eComponentScan.scanRemoveServices
		elif tmp == "yes_hold_feeds":
			flags |= eComponentScan.scanRemoveServices
			flags |= eComponentScan.scanDontRemoveFeeds

		if tmp != "no" and not removeAll:
			flags |= eComponentScan.scanDontRemoveUnscanned

		if self.scan_onlyfree.value:
			flags |= eComponentScan.scanOnlyFree

		for x in self["config"].list:
			x[1].save()

		if startScan:
			self.startScan(tlist, flags, index_to_scan)

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		if self.oldref and self.prev_ref:
			self.session.openWithCallback(self.restartPrevService, MessageBox, _("Zap back to service before a service scan?"), MessageBox.TYPE_YESNO, timeout=5)
		else:
			self.close()

	def restartPrevService(self, answer):
		if answer:
			self.tuneTimer.stop()
			self.deInitFrontend()
			if self.oldref:
				self.session.nav.playService(self.oldref)
		self.close()

	def startScan(self, tlist, flags, feid):
		if len(tlist):
			self.session.openWithCallback(self.serviceScanFinished, SimpleServiceScan, [{"transponders": tlist, "feid": feid, "flags": flags}])
		else:
			self.session.open(MessageBox, _("Nothing to scan!\nPlease setup your tuner settings before you start a service scan."), MessageBox.TYPE_ERROR)
			self.keyCancel()

	def serviceScanFinished(self):
		self.session.openWithCallback(self.restartSimpleSatScan, MessageBox, _("Do you want to scan another transponder/satellite?"), MessageBox.TYPE_YESNO, timeout=10)

	def restartSimpleSatScan(self, answer):
		if answer:
			self.frontend = None
			self.initFrontend()
			self.retune(None)
		else:
			self.keyCancel()


def SimpleSatScanMain(session, **kwargs):
	nimList = nimmanager.getNimListOfType("DVB-S")
	if len(nimList) == 0:
		session.open(MessageBox, _("No satellite frontend found!"), MessageBox.TYPE_ERROR)
	else:
		if session.nav.RecordTimer.isRecording():
			session.open(MessageBox, _("A recording is currently running. Please stop the recording before trying to start a service scan."), MessageBox.TYPE_ERROR)
		else:
			session.open(SimpleSatScan)


def SimpleSatScanStart(menuid, **kwargs):
	if menuid == "scan":
		return [(_("Simple satellite scan"), SimpleSatScanMain, "simple_sat_scan", None)]
	else:
		return []


def Plugins(**kwargs):
	if (nimmanager.hasNimType("DVB-S")):
		return PluginDescriptor(name=_("Simple satellite scan"), description="simple satellite scan", where=PluginDescriptor.WHERE_MENU, fnc=SimpleSatScanStart)
	else:
		return []
