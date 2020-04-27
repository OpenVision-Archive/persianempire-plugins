#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.config import config
from Screens.Screen import Screen
from enigma import getDesktop, ePicLoad, eBackgroundFileEraser
from thread import start_new_thread

class AirPlayPicturePlayer(Screen):

    def __init__(self, session, backend, picFile, lastservice = None):
        self.backend = backend
        backend.PictureWindow = self
        self.bgcolor = '#00000000'
        space = 0
        size_w = getDesktop(0).size().width()
        size_h = getDesktop(0).size().height()
        self.skin = '<screen position="0,0" size="' + str(size_w) + ',' + str(size_h) + '" flags="wfNoBorder" >             <eLabel position="0,0" zPosition="0" size="' + str(size_w) + ',' + str(size_h) + '" backgroundColor="' + self.bgcolor + '" />             <widget name="pic" position="' + str(space + 20) + ',' + str(space) + '" size="' + str(size_w - space * 2) + ',' + str(size_h - space * 2) + '" zPosition="1" alphatest="on" />             <widget source="label_update"  transparent="1" render="Label" zPosition="4" position="50,50"  size="250,28" font="Regular;24" backgroundColor="#00aaaaaa" foregroundColor="#00ff0000" />             </screen>'
        print('[AirPlayPicturePlayer] starting PicturePlayer')
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['OkCancelActions', 'MoviePlayerActions'], {'cancel': self.Exit,
         'leavePlayer': self.Exit}, -1)
        self['pic'] = Pixmap()
        self.picFile = picFile
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.finish_decode)
        self.onLayoutFinish.append(self.setPicloadConf)
        self.lastservice = lastservice or self.session.nav.getCurrentlyPlayingServiceReference()
        if config.plugins.airplayer.stopTVOnPicture.value:
            self.session.nav.stopService()

    def getScale(self):
        return AVSwitch().getFramebufferScale()

    def setPicloadConf(self):
        sc = self.getScale()
        self.picload.setPara([self['pic'].instance.size().width(),
         self['pic'].instance.size().height(),
         sc[0],
         sc[1],
         0,
         1,
         self.bgcolor])
        self.start_decode()

    def ShowPicture(self):
        if self.currPic != None:
            self['pic'].instance.setPixmap(self.currPic.__deref__())
        return

    def finish_decode(self, picInfo = ''):
        ptr = self.picload.getData()
        if ptr != None:
            self.currPic = ptr
            self.ShowPicture()
        return

    def start_decode(self):
        self.picload.startDecode(self.picFile)

    def leavePlayer(self):
        self.leavePlayerConfirmed(True)

    def leavePlayerConfirmed(self, answer):
        if answer:
            self.Exit()

    def Exit(self):
        print('[AirPlayPicturePlayer] stopping PicturePlayer')
        del self.picload
        self.backend.PictureWindow = None
        if config.plugins.airplayer.stopTVOnPicture.value and self.lastservice is not None:
            self.session.nav.playService(self.lastservice)
        eBackgroundFileEraser.getInstance().erase(config.plugins.airplayer.path.value + '/' + self.picFile)
        self.close()
        return
