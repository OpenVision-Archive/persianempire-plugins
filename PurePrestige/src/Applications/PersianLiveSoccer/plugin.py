# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Tools.LoadPixmap import LoadPixmap
from Components.Label import Label
from Screens.Console import Console
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap, NumberActionMap
from Plugins.Plugin import PluginDescriptor
from Components.About import about
from Plugins.Extensions.PurePrestige.soupparse import *
from Components.ScrollLabel import ScrollLabel
from twisted.web.client import downloadPage, getPage
import urllib2
from threading import Timer
import re
import sys
from urllib2 import URLError
from enigma import eTimer, eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, getDesktop, loadPNG, loadPic
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import config, ConfigDirectory, ConfigSubsection, ConfigSubList, ConfigEnableDisable, ConfigNumber, ConfigText, ConfigSelection, ConfigYesNo, ConfigPassword, getConfigListEntry, configfile
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

config.plugins.Sfootball = ConfigSubsection()
config.plugins.Sfootball.countries = ConfigSubList()
config.plugins.Sfootball.countries_count = ConfigNumber(default=0)
urlpath = 'http://www3.varzesh3.com/livescores.do'
sliderfile = resolveFilename(SCOPE_PLUGINS, 'Extensions/PersianLiveSoccer/images/slider.png')
c7color = 11403055
c2color = 16753920
c1color = 16776960
c3color = 15657130
c5color = 16711680
c4color = 16729344
c6color = 65407
c8color = 13047173
c9color = 13789470


def wfile(st):
    fp = open('/tmp/lf.txt', 'a')
    fp.write('\n' + st)
    fp.close()


def converttime(s, timediff, soccerstand):
    pretime = s
    s = s.replace(' ', '')
    s = s.strip()
    gmt = False
    try:
        thetimezone = config.timezone.val.value
        if '+' not in thetimezone and '-' not in thetimezone:
            gmt = True
        allok = True
        if allok == True:
            time = s
            print(time)
            thetimezone = thetimezone[thetimezone.find('(') + 1:thetimezone.find(')')]
            newtime = int(time[0:2] + time[3:5])
            if gmt == True:
                parts = time.split(':')
                if soccerstand == True:
                    hours = int(parts[0]) - 2
                else:
                    hours = int(parts[0]) + 2
                minutes = int(parts[1])
                if hours > 23:
                    hours = hours - 24
                if minutes > 59:
                    hours = hours + 1
                    minutes = minutes - 60
            if '+' in thetimezone:
                hours = int(time[0:2]) + int(thetimezone[4:thetimezone.find(':')]) - timediff
                if hours > 23:
                    hours = hours - 24
                print('time', time[3:5])
                print('time2', thetimezone[thetimezone.find(':') + 1:9])
                minutes1 = int(time[3:5])
                minutes2 = int(thetimezone[thetimezone.find(':') + 1:9]) + timediff
                minutes = int(time[3:5]) + int(thetimezone[thetimezone.find(':') + 1:9])
                if minutes > 59:
                    hours = hours + 1
                    minutes = minutes - 60
            if '-' in thetimezone:
                hours = int(time[0:2]) - int(thetimezone[4:thetimezone.find(':')]) - timediff
                if hours < 0:
                    hours = hours + 24
                minutes = int(time[3:5]) - int(thetimezone[thetimezone.find(':') + 1:9])
                if minutes < 0:
                    hours = hours - 1
                    minutes = minutes + 60
            if hours < 10:
                hours = '0' + str(hours)
            if minutes < 10:
                minutes = '0' + str(minutes)
            thenewtimezone = str(hours) + ':' + str(minutes)
            s = str(thenewtimezone)
        return s
    except:
        return pretime


class persiansoccerTableScreen(Screen):
    skin = '\n\t\t<screen position="center,center" size="700,520" title="Tables and soccer stats" flags="wfNoBorder" >\n\t\t\t<ePixmap pixmap="~/Applications/PersianLiveSoccer/images/frame.png" position="0,0" size="700,520"/>\n                        <widget name="menu" position="15,15" size="670,490" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n                        <widget name="info" position="0,0" zPosition="4" size="700,520" font="Regular;24" foregroundColor="#ffffff" transparent="1" horizontalAlignment="center" verticalAlignment="center" />\n          \n                </screen>'

    def __init__(self, session, data, rows):
        self.session = session
        self.data = data
        self.rows = rows
        self['menu'] = MenuList([], True, eListboxPythonMultiContent)
        Screen.__init__(self, session)
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions', 'ColorActions'], {'ok': self.close,
         'cancel': self.close}, -1)
        if self.data == 'derror':
            self['info'] = Label('Sorry,No data available,may be internet problem or server down')
            return
        if self.data == 'perror':
            self['info'] = Label('Sorry,data parsing error.....')
            return
        if self.data == 'serror':
            self['info'] = Label('Sorry,no data from the source,try later.....')
            return
        self.onLayoutFinish.append(self.addtitle)
        self.timer = eTimer()
        self.timer.callback.append(self.ListToMulticontenttables)
        self.timer.start(100, 1)

    def addtitle(self):
        self.setTitle('Persian Live Soccer')

    def ListToMulticontenttables(self):
        self['menu'].l.setItemHeight(35)
        self['menu'].l.setFont(0, gFont('Regular', 22))
        res = []
        theevents = []
        for row in self.rows:
            items = row.split('$')
            res = []
            if len(items) < 4:
                title = str(items[1])
                res.append(MultiContentEntryText(pos=(0, 10), size=(0, 25), font=0, flags=RT_HALIGN_RIGHT, text='', color=c1color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(15, 10), size=(670, 25), font=0, flags=RT_HALIGN_CENTER, text=title, color=c1color, color_sel=16777215))
                png = sliderfile
                res.append(MultiContentEntryPixmapAlphaTest(pos=(15, 0), size=(770, 5), png=loadPNG(png)))
            else:
                print(len(items))
                date = str(items[1])
                date = date.replace('&nbsp;&nbsp;&nbsp;&nbsp;', ' ')
                live = str(items[2])
                if len(live) == 2:
                    live = live + "'"
                print(live)
                teamh = str(items[3])
                print(teamh)
                teama = str(items[5])
                print(teama)
                score = str(items[6])
                score = str(items[4])
                print(score)
                res.append(MultiContentEntryText(pos=(5, 10), size=(10, 25), font=0, flags=RT_HALIGN_RIGHT, text='', color=c2color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(10, 10), size=(130, 25), font=0, flags=RT_HALIGN_RIGHT, text=teama, color=c2color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(140, 10), size=(60, 25), font=0, flags=RT_HALIGN_RIGHT, text=score, color=c3color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(200, 10), size=(150, 25), font=0, flags=RT_HALIGN_CENTER, text=teamh, color=c4color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(360, 10), size=(100, 25), font=0, flags=RT_HALIGN_LEFT, text=live, color=c5color, color_sel=16777215))
                res.append(MultiContentEntryText(pos=(470, 10), size=(200, 25), font=0, flags=RT_HALIGN_RIGHT, text=date, color=c6color, color_sel=16777215))
            theevents.append(res)

        self['menu'].l.setList(theevents)
        self['menu'].show()


class psoccerbootlogo(Screen):
    global HD_Res
    try:
        sz_w = getDesktop(0).size().width()
        if sz_w == 1280:
            HD_Res = True
        else:
            HD_Res = False
    except:
        HD_Res = False

    HD_Res = False
    if HD_Res == True:
        skin = '\n        \t\n                <screen name="PurePrestigeAboutScreen" position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="920,600" transparent="1"/>\t\n                <ePixmap pixmap="~/images/teamhd.png" position="15,15" size="890,570"/>\t\n                \n                 </screen>'
    else:
        skin = '\n      \t<screen name="PurePrestigebootlogo" position="center,center" size="700,520" title=""  flags="wfNoBorder" >\n                        <widget name="info" position="0,400" zPosition="4" size="700,120" font="Regular;24" foregroundColor="yellow" transparent="1" horizontalAlignment="center" verticalAlignment="center" />                  \n                <ePixmap pixmap="~/Applications/PersianLiveSoccer/images/persianlogo.png" position="0,0" size="700,520"/>\n                        <widget name="infol" position="15,20" zPosition="4" size="335,30" font="Regular;20" foregroundColor="#ffffff" transparent="1" horizontalAlignment="center" verticalAlignment="center" />                                  \n                        <widget name="infor" position="350,20" zPosition="4" size="335,30" font="Regular;20" foregroundColor="#ffffff" transparent="1" horizontalAlignment="center" verticalAlignment="center" />                  \n \n\t\n                </screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        self['infol'] = Label('http://dreamoem.com')
        self['infor'] = Label('http://persianpros.org')
        self['info'] = Label('version 1.1-mfaraj57\nDownloading data,please wait...')
        self.data = ''
        self.session = session
        self.rows = []
        self.html = ''
        self['actions'] = ActionMap(['SetupActions'], {'cancel': self.disappear}, -1)
        self.timer = eTimer()
        self.timer.callback.append(self.downloadurl)
        self.timer.start(100, True)

    def exit(self):
        sys.stop()
        self.disappear()

    def handler(self, fh=None):
        url = 'http://www3.varzesh3.com/livescores.do'
        fh.close
        fh = urlopen(url)
        t = Timer(20.0, self.handler, [fh])
        t.start()
        data = fh.read()
        t.cancel()
        return data

    def downloadurl(self):
        data = ''
        try:
            fp = urllib2.urlopen(urlpath)
            self.data = ''
            while True:
                s = fp.readline()
                if len(s) > 1:
                    data = data + '\n' + s
                if not s:
                    break

            fp.close()
            self.html = data
            self.processtables()
        except:
            self.data = 'derror'
            self.disappear()
            return

    def processtables(self):
        html = self.html
        if html == '':
            self.data = 'derror'
            self.disappear()
            return
        soup = BeautifulSoup(''.join(html))
        tables = soup.findAll('table')
        print(len(tables))
        t = -1
        rowslist = []
        for table in tables:
            t = t + 1
            print('********************************')
            print('table:', t)
            print('********************************')
            try:
                rows = table.findAll('tr')
            except:
                print('perror')
                self.data = 'perror'
                self.disappear()
                return

            self.rows = []
            for tr in rows:
                cols = tr.findAll('td')
                itemstr = 'info'
                for td in cols:
                    txt = ''.join(td.text)
                    itemstr = itemstr + '$' + txt

                self.rows.append(itemstr)

            continue

        if len(self.rows) == 0:
            self.data = 'serror'
            self.disappear()
            return
        self.data = 'ok'
        self.disappear()

    def disappear(self):
        self.session.openWithCallback(self.close, persiansoccerTableScreen, self.data, self.rows)


def main(session, **kwargs):
    session.open(psoccerbootlogo)


def Plugins(**kwargs):
    return PluginDescriptor(name='PersianLiveSoccer', description=_('Persian live soccer'), where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], icon='PersianLiveSoccer.png', fnc=main)
