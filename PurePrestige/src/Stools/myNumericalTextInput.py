#!/usr/bin/python
# -*- coding: utf-8 -*-
from enigma import eTimer
from Components.Language import language

class myNumericalTextInput:

    def __init__(self, nextFunc = None, handleTimeout = True, search = False):
        self.mapping = []
        self.lang = language.getLanguage()
        self.useableChars = None
        self.nextFunction = nextFunc
        if handleTimeout:
            self.timer = eTimer()
            self.timer.callback.append(self.timeout)
        else:
            self.timer = None
        self.lastKey = -1
        self.pos = -1
        if search:
            self.mapping.append(u'%_0')
            self.mapping.append(u' 1')
            self.mapping.append(u'abc2')
            self.mapping.append(u'def3')
            self.mapping.append(u'ghi4')
            self.mapping.append(u'jkl5')
            self.mapping.append(u'mno6')
            self.mapping.append(u'pqrs7')
            self.mapping.append(u'tuv8')
            self.mapping.append(u'wxyz9')
            return
        else:
            if self.lang == 'de_DE':
                self.mapping.append(u'.,?\'+"0-()@/:_$!')
                self.mapping.append(u' 1#')
                self.mapping.append(u'a\xe4bc2A\xc4BC')
                self.mapping.append(u'def3DEF')
                self.mapping.append(u'ghi4GHI')
                self.mapping.append(u'jkl5JKL')
                self.mapping.append(u'mno\xf66MNO\xd6')
                self.mapping.append(u'pqrs\xdf7PQRS\xdf')
                self.mapping.append(u'tu\xfcv8TU\xdcV')
                self.mapping.append(u'wxyz9WXYZ')
            elif self.lang == 'es_ES':
                self.mapping.append(u'.,?\'+"0-()@/:_$!')
                self.mapping.append(u' 1#')
                self.mapping.append(u'abc\xe1\xe02ABC\xc1\xc0')
                self.mapping.append(u'de\xe9\xe8f3DEF\xc9\xc8')
                self.mapping.append(u'ghi\xed\xec4GHI\xcd\xcc')
                self.mapping.append(u'jkl5JKL')
                self.mapping.append(u'mn\xf1o\xf3\xf26MN\xd1O\xd3\xd2')
                self.mapping.append(u'pqrs7PQRS')
                self.mapping.append(u'tuv\xfa\xf98TUV\xda\xd9')
                self.mapping.append(u'wxyz9WXYZ')
            if self.lang in ('sv_SE', 'fi_FI'):
                self.mapping.append(u'.,?\'+"0-()@/:_$!')
                self.mapping.append(u' 1#')
                self.mapping.append(u'abc\xe5\xe42ABC\xc5\xc4')
                self.mapping.append(u'def\xe93DEF\xc9')
                self.mapping.append(u'ghi4GHI')
                self.mapping.append(u'jkl5JKL')
                self.mapping.append(u'mno\xf66MNO\xd6')
                self.mapping.append(u'pqrs7PQRS')
                self.mapping.append(u'tuv8TUV')
                self.mapping.append(u'wxyz9WXYZ')
            else:
                self.mapping.append(u'.,?\'+"0-()@/:_$!')
                self.mapping.append(u' 1#')
                self.mapping.append(u'abc2ABC')
                self.mapping.append(u'def3DEF')
                self.mapping.append(u'ghi4GHI')
                self.mapping.append(u'jkl5JKL')
                self.mapping.append(u'mno6MNO')
                self.mapping.append(u'pqrs7PQRS')
                self.mapping.append(u'tuv8TUV')
                self.mapping.append(u'wxyz9WXYZ')
            return

    def setUseableChars(self, useable):
        self.useableChars = useable

    def getKey(self, num):
        cnt = 0
        if self.lastKey != num:
            if self.lastKey != -1:
                self.nextChar()
            self.lastKey = num
            self.pos = -1
        if self.timer is not None:
            self.timer.start(1000, True)
        while True:
            self.pos += 1
            if len(self.mapping[num]) <= self.pos:
                self.pos = 0
            if self.useableChars:
                pos = self.useableChars.find(self.mapping[num][self.pos])
                if pos == -1:
                    cnt += 1
                    if cnt < len(self.mapping[num]):
                        continue
                    else:
                        return
            break

        return self.mapping[num][self.pos]

    def nextKey(self):
        if self.timer is not None:
            self.timer.stop()
        self.lastKey = -1
        return

    def nextChar(self):
        self.nextKey()
        if self.nextFunction:
            self.nextFunction()

    def timeout(self):
        if self.lastKey != -1:
            self.nextChar()
