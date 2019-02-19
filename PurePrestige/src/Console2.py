from Screens.Screen import Screen
from enigma import eConsoleAppContainer
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Tools.Directories import copyfile
from enigma import getDesktop
import os
from Screens.Standby import TryQuitMainloop

class PurePrestigeConsole2(Screen):
    global HD_Res
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    if HD_Res == True:
        skin = '\n        \t\n                <screen name="PurePrestigeConsole2" backgroundColor="#380038" position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frametop.png" position="0,0" size="920,600"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frameleft.png" position="0,10" size="10,580"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frameright.png" position="910,10" size="10,580"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framebottom.png" position="0,590" size="920,10"/>\t\n                \n\t\t<widget name="text" position="30,30" size="865,570" font="Regular;22"  transparent="1" zPosition="2"  />\n                </screen>'
    else:
        skin = '\n        \t\n                <screen name="PurePrestigeConsole2" backgroundColor="#380038" position="center,center" size="580,450" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frametop.png" position="0,0" size="580,450"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frameleft.png" position="0,7" size="6,435"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/frameright.png" position="573,7" size="6,435"/>\t\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framebottom.png" position="0,442" size="580,7"/>\t\n                \n\t\t<widget name="text" position="19,22" size="554,427" font="Regular;22"  transparent="1" zPosition="2"  />\n                </screen>'

    def __init__(self, session, title = 'Console', cmdlist = None, finishedCallback = None, closeOnSuccess = False, instr = None, endstr = None):
        Screen.__init__(self, session)
        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self.endstr = endstr
        instr = instr + '\n*************************************\n'
        self['text'] = ScrollLabel(instr)
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'blue': self.restartenigma,
         'ok': self.cancel,
         'back': self.cancel,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown}, -1)
        self.cmdlist = cmdlist
        self.newtitle = title
        self.onShown.append(self.updateTitle)
        self.container = eConsoleAppContainer()
        self.run = 0
        self.container.appClosed.append(self.runFinished)
        self.container.dataAvail.append(self.dataAvail)
        self.onLayoutFinish.append(self.startRun)

    def restartenigmold(self):
        os.system('killall -9 enigma2')

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        print 'Console: executing in run', self.run, ' the command:', self.cmdlist[self.run]
        if self.container.execute(self.cmdlist[self.run]):
            self.runFinished(-1)

    def runFinished(self, retval):
        self.run += 1
        self.setTitle('Execution Finished')
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]):
                self.runFinished(-1)
        else:
            str = self['text'].getText()
            str += '\n' + _('Execution finished!!')
            self['text'].setText(str)
            self['text'].lastPage()
            if self.finishedCallback is not None and not retval:
                self.finishedCallback()
            if not retval and self.closeOnSuccess:
                self.cancel()
            else:
                str += '\n' + _(self.endstr)
                self['text'].setText(str)
                self['text'].lastPage()
        return

    def cancel(self):
        if self.run == len(self.cmdlist):
            self.close()
            self.container.appClosed.remove(self.runFinished)
            self.container.dataAvail.remove(self.dataAvail)

    def dataAvail(self, str):
        self['text'].setText(self['text'].getText() + str)

    def restartenigma(self):
        epgpath = '/media/hdd/epg.dat'
        epgbakpath = '/media/hdd/epg.dat.bak'
        if os.path.exists(epgbakpath):
            os.remove(epgbakpath)
        if os.path.exists(epgpath):
            copyfile(epgpath, epgbakpath)
        self.session.open(TryQuitMainloop, 3)
