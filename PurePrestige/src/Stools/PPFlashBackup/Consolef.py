#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from enigma import eConsoleAppContainer
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel


class Consolef(Screen):
    skin = '\n\t\t<screen position="70,70" size="300,0" title="Command execution..." >\n\t\t\t<widget name="text" position="0,0" size="550,400" font="Console;14" />\n\t\t</screen>'

    def __init__(self, session, title='Console', cmdlist=None, finishedCallback=None, closeOnSuccess=False):
        Screen.__init__(self, session)
        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self['text'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.cancel,
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

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        self['text'].setText(_('Execution Progress:') + '\n\n')
        print('Console: executing in run', self.run, ' the command:', self.cmdlist[self.run])
        if self.container.execute(self.cmdlist[self.run]):
            self.runFinished(-1)

    def runFinished(self, retval):
        self.run += 1
        self.setTitle('Finished backup-press OK to exit')
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]):
                self.runFinished(-1)
        else:
            str = self['text'].getText()
            str += _('Execution finished!!')
            self['text'].setText(str)
            self['text'].lastPage()
            if self.finishedCallback is not None:
                self.finishedCallback()
                try:
                    self.cancel()
                except:
                    pass

            if not retval and self.closeOnSuccess:
                self.cancel()
        return

    def cancel(self):
        try:
            if self.run == len(self.cmdlist):
                self.close()
                self.container.appClosed.remove(self.runFinished)
                self.container.dataAvail.remove(self.dataAvail)
        except:
            pass

    def dataAvail(self, str):
        self['text'].setText(self['text'].getText() + str)
