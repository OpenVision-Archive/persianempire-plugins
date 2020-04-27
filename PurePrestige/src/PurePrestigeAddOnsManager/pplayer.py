# -*- coding: utf-8 -*-
from __future__ import print_function
from Screens.Screen import Screen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from enigma import ePicLoad, eTimer
from twisted.web.client import downloadPage
import os

class PictureScreen(Screen):
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    if HD_Res:
        skin = '\n\t\t<screen name="PictureScreen" position="center,center" size="1280,720" title="Picture Screen" backgroundColor="#002C2C39">\n\t\t\t<widget name="myPic" position="0,0" size="1280,720" zPosition="1" alphatest="on" />\n\t\t        <widget name="info" position="200,100" zPosition="4" size="400,400" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n                </screen>\n\t\t'
    else:
        skin = '\n\t\t<screen name="PictureScreen" position="center,center" size="720,576" title="Picture Screen" backgroundColor="#002C2C39">\n\t\t\t<widget name="myPic" position="0,0" size="720,576" zPosition="1" alphatest="on" />\n\t\t        <widget name="info" position="150,50" zPosition="4" size="400,400" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n                </screen>\n\t\t'

    def __init__(self, session, url = None):
        Screen.__init__(self, session)
        print('[PictureScreen] __init__\n')
        self.url = url
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self['myPic'] = Pixmap()
        self['info'] = Label()
        self['myActionMap'] = ActionMap(['SetupActions'], {'ok': self.cancel,
         'cancel': self.cancel}, -1)
        self['info'].setText('Downloading preview,please wait..\n press exit to cancel')
        self.PicLoad.PictureData.get().append(self.DecodePicture)
        self.timer = eTimer()
        self.timer.callback.append(self.playpicture)
        self.timer.start(100, 1)

    def playpicture(self):
        self.getPicfromUrl()

    def getPicfromUrl(self):
        self.path = '/tmp/bootlogo.jpg'
        self.download()

    def download(self):
        downloadPage(self.url, self.path).addCallback(self.downloadDone).addErrback(self.downloadError)

    def downloadError(self, raw):
        print('[e2Fetcher.fetchPage]: download Error', raw)
        self['info'].setText('Preview Download Failure,No internet connection or server down or preview not available !\n press OK to exit')

    def downloadDone(self, raw):
        self['info'].setText('')
        self.ShowPicture()

    def ShowPicture(self):
        if self.path is not None:
            self.PicLoad.setPara([self['myPic'].instance.size().width(),
             self['myPic'].instance.size().height(),
             self.Scale[0],
             self.Scale[1],
             0,
             1,
             '#002C2C39'])
            self.PicLoad.startDecode(self.path)
        return

    def DecodePicture(self, PicInfo = ''):
        if self.path is not None:
            ptr = self.PicLoad.getData()
            self['myPic'].instance.setPixmap(ptr)
        return

    def cancel(self):
        print('[PictureScreen] - cancel\n')
        try:
            os.remove('/tmp/bootlogo.jpg')
        except:
            pass

        self.close(None)
        return
