# -*- coding: utf-8 -*-
from Components.GUIComponent import GUIComponent
from enigma import ePixmap
from enigma import eTimer


class Spinner(GUIComponent):

    def __init__(self, Bilder):
        GUIComponent.__init__(self)
        self.len = 0
        self.SetBilder(Bilder)
        self.timer = eTimer()
        self.timer.callback.append(self.Invalidate)
        self.timer.start(100)

    def SetBilder(self, Bilder):
        self.Bilder = Bilder

    GUI_WIDGET = ePixmap

    def destroy(self):
        if self.timer:
            self.timer.callback.remove(self.Invalidate)

    def Invalidate(self):
        try:
            if self.instance:
                if self.len >= len(self.Bilder):
                    self.len = 0
                self.instance.setPixmapFromFile(self.Bilder[self.len])
                self.len += 1
        except:
            pass
