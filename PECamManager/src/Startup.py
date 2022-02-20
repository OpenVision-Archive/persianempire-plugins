#!/usr/bin/python
# -*- coding: utf-8 -*-
from enigma import eTimer
from Components.config import config
from Components.Console import Console
from .Softcam import getcamcmd


class StartCamOnStart:
	def __init__(self):
		self.Console = Console()
		self.Timer = eTimer()
		self.Timer.timeout.get().append(self.__camnotrun)

	def start(self):
		self.Timer.start(2000, False)

	def __camnotrun(self):
		self.Timer.stop()
		self.Console.ePopen("ps", self.checkprocess)

	def checkprocess(self, result, retval, extra_args):
		processes = result.lower()
		camlist = []
		camlist.insert(0, config.plugins.PECam.actcam.value)
		camnot = True
		for cam in camlist:
			if cam in processes:
				camnot = False
				break
		if camnot:
			cmd = getcamcmd(config.plugins.PECam.actcam.value)
			Console().ePopen(cmd)


startcamonstart = StartCamOnStart()
