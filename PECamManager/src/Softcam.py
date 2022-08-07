# -*- coding: utf-8 -*-
from os import mkdir, path, remove
from Components.config import config
from Components.Console import Console


def getcamcmd(cam):
	camname = cam.lower()
	if getcamscript(camname):
		return config.plugins.PECam.camdir.value + "/" + cam + " start"
	return config.plugins.PECam.camdir.value + "/" + cam


def getcamscript(cam):
	cam = cam.lower()
	if cam[-3:] == ".sh" or cam[:7] == "softcam" or cam[:10] == "cardserver":
		return True
	return False


def stopcam(cam):
	if getcamscript(cam):
		cmd = config.plugins.PECam.camdir.value + "/" + cam + " stop"
	else:
		cmd = "killall -9 " + cam
	Console().ePopen(cmd)
	try:
		remove("/tmp/ecm.info")
	except:
		pass


def __createdir(list):
	dir = ""
	for line in list[1:].split("/"):
		dir += "/" + line
		if not path.exists(dir):
			try:
				mkdir(dir)
			except:
				print("[PE Cam Manager] Failed to mkdir", dir)


def checkconfigdir():
	if not path.exists(config.plugins.PECam.camconfig.value):
		__createdir("/usr/keys")
		config.plugins.PECam.camconfig.value = "/usr/keys"
		config.plugins.PECam.camconfig.save()
	if not path.exists(config.plugins.PECam.camdir.value):
		__createdir("/usr/camd")
		config.plugins.PECam.camdir.value = "/usr/camd"
		config.plugins.PECam.camdir.save()
