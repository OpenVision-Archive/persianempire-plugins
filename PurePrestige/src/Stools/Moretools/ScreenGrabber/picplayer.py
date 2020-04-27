# -*- coding: utf-8 -*-
from __future__ import print_function
from enigma import ePicLoad, eTimer, getDesktop
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, pathExists, SCOPE_MEDIA
from Components.Pixmap import Pixmap, MovingPixmap
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.StaticText import StaticText
from Components.FileList import FileList
from Components.AVSwitch import AVSwitch
from Components.Sources.List import List
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import config, ConfigSubsection, ConfigInteger, ConfigSelection, ConfigText, ConfigEnableDisable, KEY_LEFT, KEY_RIGHT, KEY_0, getConfigListEntry

def getScale():
    return AVSwitch().getFramebufferScale()


config.pic1 = ConfigSubsection()
config.pic1.framesize = ConfigInteger(default=30, limits=(5, 99))
config.pic1.slidetime = ConfigInteger(default=10, limits=(1, 60))
config.pic1.resize = ConfigSelection(default='1', choices=[('0', _('simple')), ('1', _('better'))])
config.pic1.cache = ConfigEnableDisable(default=True)
config.pic1.lastDir = ConfigText(default=resolveFilename(SCOPE_MEDIA))
config.pic1.infoline = ConfigEnableDisable(default=True)
config.pic1.loop = ConfigEnableDisable(default=True)
config.pic1.bgcolor = ConfigSelection(default='#00000000', choices=[('#00000000', _('black')),
 ('#009eb9ff', _('blue')),
 ('#00ff5a51', _('red')),
 ('#00ffe875', _('yellow')),
 ('#0038FF48', _('green'))])
config.pic1.textcolor = ConfigSelection(default='#0038FF48', choices=[('#00000000', _('black')),
 ('#009eb9ff', _('blue')),
 ('#00ff5a51', _('red')),
 ('#00ffe875', _('yellow')),
 ('#0038FF48', _('green'))])
T_INDEX = 0
T_FRAME_POS = 1
T_PAGE = 2
T_NAME = 3
T_FULL = 4

class grabberPic_Thumb(Screen):

    def __init__(self, session, piclist, lastindex, path):
        self.textcolor = config.pic1.textcolor.value
        self.color = config.pic1.bgcolor.value
        textsize = 20
        self.spaceX = 35
        self.picX = 190
        self.spaceY = 30
        self.picY = 200
        size_w = getDesktop(0).size().width()
        size_h = getDesktop(0).size().height()
        self.thumbsX = size_w / (self.spaceX + self.picX)
        self.thumbsY = size_h / (self.spaceY + self.picY)
        self.thumbsC = self.thumbsX * self.thumbsY
        self.positionlist = []
        skincontent = ''
        posX = -1
        for x in range(self.thumbsC):
            posY = x / self.thumbsX
            posX += 1
            if posX >= self.thumbsX:
                posX = 0
            absX = self.spaceX + posX * (self.spaceX + self.picX)
            absY = self.spaceY + posY * (self.spaceY + self.picY)
            self.positionlist.append((absX, absY))
            skincontent += '<widget source="label' + str(x) + '" render="Label" position="' + str(absX + 5) + ',' + str(absY + self.picY - textsize) + '" size="' + str(self.picX - 10) + ',' + str(textsize) + '" font="Regular;14" zPosition="2" transparent="1" noWrap="1" foregroundColor="' + self.textcolor + '" />'
            skincontent += '<widget name="thumb' + str(x) + '" position="' + str(absX + 5) + ',' + str(absY + 5) + '" size="' + str(self.picX - 10) + ',' + str(self.picY - textsize * 2) + '" zPosition="2" transparent="1" alphatest="on" />'

        self.skin = '<screen position="0,0" size="' + str(size_w) + ',' + str(size_h) + '" flags="wfNoBorder" > \t\t\t<eLabel position="0,0" zPosition="0" size="' + str(size_w) + ',' + str(size_h) + '" backgroundColor="' + self.color + '" /><widget name="frame" position="35,30" size="190,200" pixmap="pic_frame.png" zPosition="1" alphatest="on" />' + skincontent + '</screen>'
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions',
         'DirectionActions',
         'MovieSelectionActions'], {'cancel': self.Exit,
         'ok': self.KeyOk,
         'left': self.key_left,
         'right': self.key_right,
         'up': self.key_up,
         'down': self.key_down}, -1)
        self['frame'] = MovingPixmap()
        for x in range(self.thumbsC):
            self['label' + str(x)] = StaticText()
            self['thumb' + str(x)] = Pixmap()

        self.Thumbnaillist = []
        self.filelist = []
        self.currPage = -1
        self.dirlistcount = 0
        self.path = path
        index = 0
        framePos = 0
        Page = 0
        for x in piclist:
            if x:
                self.filelist.append((index,
                 framePos,
                 Page,
                 x,
                 path + x))
                index += 1
                framePos += 1
                if framePos > self.thumbsC - 1:
                    framePos = 0
                    Page += 1
            else:
                self.dirlistcount += 1

        self.maxentry = len(self.filelist) - 1
        self.index = lastindex - self.dirlistcount
        if self.index < 0:
            self.index = 0
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.showPic)
        self.onLayoutFinish.append(self.setPicloadConf)
        self.ThumbTimer = eTimer()
        self.ThumbTimer.callback.append(self.showPic)

    def setPicloadConf(self):
        sc = getScale()
        self.picload.setPara([self['thumb0'].instance.size().width(),
         self['thumb0'].instance.size().height(),
         sc[0],
         sc[1],
         config.pic1.cache.value,
         int(config.pic1.resize.value),
         self.color])
        self.paintFrame()

    def paintFrame(self):
        if self.maxentry < self.index or self.index < 0:
            return
        pos = self.positionlist[self.filelist[self.index][T_FRAME_POS]]
        self['frame'].moveTo(pos[0], pos[1], 1)
        self['frame'].startMoving()
        if self.currPage != self.filelist[self.index][T_PAGE]:
            self.currPage = self.filelist[self.index][T_PAGE]
            self.newPage()

    def newPage(self):
        self.Thumbnaillist = []
        for x in range(self.thumbsC):
            self['label' + str(x)].setText('')
            self['thumb' + str(x)].hide()

        for x in self.filelist:
            if x[T_PAGE] == self.currPage:
                self['label' + str(x[T_FRAME_POS])].setText('(' + str(x[T_INDEX] + 1) + ') ' + x[T_NAME])
                self.Thumbnaillist.append([0, x[T_FRAME_POS], x[T_FULL]])

        self.showPic()

    def showPic(self, picInfo = ''):
        for x in range(len(self.Thumbnaillist)):
            if self.Thumbnaillist[x][0] == 0:
                if self.picload.getThumbnail(self.Thumbnaillist[x][2]) == 1:
                    self.ThumbTimer.start(500, True)
                else:
                    self.Thumbnaillist[x][0] = 1
                break
            elif self.Thumbnaillist[x][0] == 1:
                self.Thumbnaillist[x][0] = 2
                ptr = self.picload.getData()
                if ptr != None:
                    self['thumb' + str(self.Thumbnaillist[x][1])].instance.setPixmap(ptr.__deref__())
                    self['thumb' + str(self.Thumbnaillist[x][1])].show()

        return

    def key_left(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.maxentry
        self.paintFrame()

    def key_right(self):
        self.index += 1
        if self.index > self.maxentry:
            self.index = 0
        self.paintFrame()

    def key_up(self):
        self.index -= self.thumbsX
        if self.index < 0:
            self.index = self.maxentry
        self.paintFrame()

    def key_down(self):
        self.index += self.thumbsX
        if self.index > self.maxentry:
            self.index = 0
        self.paintFrame()

    def KeyOk(self):
        if self.maxentry < 0:
            return
        self.old_index = self.index
        self.session.openWithCallback(self.callbackView, grabberPic_Full_View, self.filelist, self.index, self.path)

    def callbackView(self, val = 0):
        self.index = val
        if self.old_index != self.index:
            self.paintFrame()

    def Exit(self):
        del self.picload
        self.close(self.index + self.dirlistcount)


class grabberPic_Full_View(Screen):

    def __init__(self, session, filelist, index, path):
        self.textcolor = config.pic1.textcolor.value
        self.bgcolor = config.pic1.bgcolor.value
        space = config.pic1.framesize.value
        size_w = getDesktop(0).size().width()
        size_h = getDesktop(0).size().height()
        self.skin = '<screen position="0,0" size="' + str(size_w) + ',' + str(size_h) + '" flags="wfNoBorder" > \t\t\t<eLabel position="0,0" zPosition="0" size="' + str(size_w) + ',' + str(size_h) + '" backgroundColor="' + self.bgcolor + '" /><widget name="pic" position="' + str(space) + ',' + str(space) + '" size="' + str(size_w - space * 2) + ',' + str(size_h - space * 2) + '" zPosition="1" alphatest="on" /> \t\t\t<widget name="point" position="' + str(space + 5) + ',' + str(space + 2) + '" size="20,20" zPosition="2" pixmap="icons/record.png" alphatest="on" /> \t\t\t<widget name="play_icon" position="' + str(space + 25) + ',' + str(space + 2) + '" size="20,20" zPosition="2" pixmap="icons/ico_mp_play.png"  alphatest="on" /> \t\t\t<widget source="file" render="Label" position="' + str(space + 45) + ',' + str(space) + '" size="' + str(size_w - space * 2 - 50) + ',25" font="Regular;20"   halign="left" foregroundColor="' + self.textcolor + '" zPosition="2" noWrap="1" transparent="1" /></screen>'
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions',
         'DirectionActions',
         'MovieSelectionActions'], {'cancel': self.Exit,
         'green': self.PlayPause,
         'yellow': self.PlayPause,
         'blue': self.nextPic,
         'red': self.prevPic,
         'left': self.prevPic,
         'right': self.nextPic}, -1)
        self['point'] = Pixmap()
        self['pic'] = Pixmap()
        self['play_icon'] = Pixmap()
        self['file'] = StaticText(_('please wait, loading picture...'))
        self.old_index = 0
        self.filelist = []
        self.lastindex = index
        self.currPic = []
        self.shownow = True
        self.dirlistcount = 0
        for x in filelist:
            if len(filelist[0]) == 3:
                if x[0][1] == False:
                    self.filelist.append(path + x[0][0])
                else:
                    self.dirlistcount += 1
            elif len(filelist[0]) == 2:
                if x[0][1] == False:
                    self.filelist.append(x[0][0])
                else:
                    self.dirlistcount += 1
            else:
                self.filelist.append(x[T_FULL])

        self.maxentry = len(self.filelist) - 1
        self.index = index - self.dirlistcount
        if self.index < 0:
            self.index = 0
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.finish_decode)
        self.slideTimer = eTimer()
        self.slideTimer.callback.append(self.slidePic)
        if self.maxentry >= 0:
            self.onLayoutFinish.append(self.setPicloadConf)

    def setPicloadConf(self):
        sc = getScale()
        self.picload.setPara([self['pic'].instance.size().width(),
         self['pic'].instance.size().height(),
         sc[0],
         sc[1],
         0,
         int(config.pic1.resize.value),
         self.bgcolor])
        self['play_icon'].hide()
        if config.pic1.infoline.value == False:
            self['file'].setText('')
        self.start_decode()

    def ShowPicture(self):
        if self.shownow and len(self.currPic):
            self.shownow = False
            self['file'].setText(self.currPic[0])
            self.lastindex = self.currPic[1]
            self['pic'].instance.setPixmap(self.currPic[2].__deref__())
            self.currPic = []
            self.next()
            self.start_decode()

    def finish_decode(self, picInfo = ''):
        self['point'].hide()
        ptr = self.picload.getData()
        if ptr != None:
            text = ''
            try:
                text = picInfo.split('\n', 1)
                text = '(' + str(self.index + 1) + '/' + str(self.maxentry + 1) + ') ' + text[0].split('/')[-1]
            except:
                pass

            self.currPic = []
            self.currPic.append(text)
            self.currPic.append(self.index)
            self.currPic.append(ptr)
            self.ShowPicture()
        return

    def start_decode(self):
        self.picload.startDecode(self.filelist[self.index])
        self['point'].show()

    def next(self):
        self.index += 1
        if self.index > self.maxentry:
            self.index = 0

    def prev(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.maxentry

    def slidePic(self):
        print('slide to next Picture index=' + str(self.lastindex))
        if config.pic1.loop.value == False and self.lastindex == self.maxentry:
            self.PlayPause()
        self.shownow = True
        self.ShowPicture()

    def PlayPause(self):
        if self.slideTimer.isActive():
            self.slideTimer.stop()
            self['play_icon'].hide()
        else:
            self.slideTimer.start(config.pic1.slidetime.value * 1000)
            self['play_icon'].show()
            self.nextPic()

    def prevPic(self):
        self.currPic = []
        self.index = self.lastindex
        self.prev()
        self.start_decode()
        self.shownow = True

    def nextPic(self):
        self.shownow = True
        self.ShowPicture()

    def Exit(self):
        del self.picload
        self.close(self.lastindex + self.dirlistcount)
