# -*- coding: utf-8 -*-
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.config import config, ConfigBoolean, ConfigFloat, ConfigInteger, ConfigSelection, ConfigText, ConfigYesNo, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.FileList import FileList
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.NimManager import nimmanager, getConfigSatlist
from Components.Pixmap import Pixmap
from enigma import eListbox, gFont, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, RT_VALIGN_TOP, RT_WRAP, eRect, eTimer
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from time import strftime, time, localtime, mktime
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from enigma import eTimer, eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, getDesktop, loadPNG, loadPic
import os
import time
try:
	import thread
except:
	import _thread as thread
import urllib2
import xml.etree.cElementTree
from . import satellite
from .ServiceEditor.plugin import PrestigePanelServicesEditor
from Plugins.Extensions.PurePrestige.Stools.setloader import PurePrestigesettingsserver


class PrestigePanelSatelliteImport(Screen):
    modeToggle = 0
    modeSelect = 1
    modeUnSelect = 2
    skin = '\n\n                <screen name="PrestigePanelSatelliteImport" position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\n\t\t<widget name="list" position="15,20" size="610,415" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<widget name="head" position="15,40" size="610,24" scrollbarMode="showNever" />\n\t\t<widget name="fspace" position="0,435" zPosition="4" size="560,85" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />\n                </screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        self.skin = PrestigePanelSatelliteImport.skin
        self['actions'] = ActionMap(['SatellitesEditorActions'], {'nextPage': self.nextPage,
         'prevPage': self.prevPage,
         'select': self.editTransponders,
         'exit': self.exitSatelliteImport,
         'left': self.left,
         'right': self.right,
         'upUp': self.upUp,
         'up': self.up,
         'upRepeated': self.upRepeated,
         'upUp': self.upUp,
         'down': self.down,
         'downUp': self.downUp,
         'downRepeated': self.downRepeated}, -1)
        self['head'] = Head()
        self['list'] = SatelliteList()
        self['fspace'] = Label('connecting..please wait')
        self.onLayoutFinish.append(self.layoutFinished)
        self.currentSelectedColumn = 0
        self.row = [['name', _('Satellites'), False], ['position', _('Pos'), False]]
        self.satelliteslist = []
        self.getSatellites_state = self.thread_is_off
        self.satTimer = eTimer()
        self.satTimer.callback.append(self.pollSatellites)
        self.getTransponders_state = self.thread_is_off
        self.tpTimer = eTimer()
        self.tpTimer.callback.append(self.pollTransponders)
        self.requestSatelliteslistRefresh = False

    def editTransponders(self):
        print('editTransponders')
        if not len(self.satelliteslist):
            return
        cur_idx = self['list'].getSelectedIndex()
        if len(self.satelliteslist[cur_idx]) == 1:
            self.satelliteslist[cur_idx][0].update({'selected': True})
            self.pollTransponders()
        else:
            self.session.openWithCallback(self.finishedTranspondersEdit, TranspondersEditor, self.satelliteslist[cur_idx])
        self['list'].setEntries(self.satelliteslist)

    def exitSatelliteImport(self):
        pass

    def doNothing(self):
        pass

    def left(self):
        print('left')
        if self.currentSelectedColumn:
            self.currentSelectedColumn -= 1
            data = self['head'].l.getCurrentSelection()
            if data is None:
                return
            data = data[self.currentSelectedColumn + 1]
            self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)
        return

    def right(self):
        print('right')
        if self.currentSelectedColumn < len(self.row) - 1:
            self.currentSelectedColumn += 1
            data = self['head'].l.getCurrentSelection()
            if data is None:
                return
            data = data[self.currentSelectedColumn + 1]
            self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)
        return

    def nextPage(self):
        self['list'].pageUp()
        self.lastSelectedIndex = self['list'].getSelectedIndex()
        self.updateSelection()

    def prevPage(self):
        self['list'].pageDown()
        self.lastSelectedIndex = self['list'].getSelectedIndex()
        self.updateSelection()

    def up(self):
        self['list'].up()
        self.lastSelectedIndex = self['list'].getSelectedIndex()
        self.updateSelection()

    def down(self):
        self['list'].down()
        self.lastSelectedIndex = self['list'].getSelectedIndex()
        self.updateSelection()

    def upUp(self):
        cur_idx = self['list'].getSelectedIndex()
        if self.lastSelectedIndex != cur_idx:
            self.lastSelectedIndex = cur_idx

    def downUp(self):
        cur_idx = self['list'].getSelectedIndex()
        if self.lastSelectedIndex != cur_idx:
            self.lastSelectedIndex = cur_idx

    def upRepeated(self):
        self['list'].up()
        self.updateSelection()

    def downRepeated(self):
        self['list'].down()
        self.updateSelection()

    def updateSelection(self):
        row = self['list'].l.getCurrentSelection()
        if row is None:
            return
        else:
            firstColumn = row[1]
            lastColumn = row[len(row) - 1]
            self['list'].l.setSelectionClip(eRect(firstColumn[1], firstColumn[0], lastColumn[1] + lastColumn[3], lastColumn[4]), True)
            return

    def finishedTranspondersEdit(self, result):
        print('finishedTranspondersEdit')
        if result is None:
            return
        else:
            cur_idx = self['list'].getSelectedIndex()
            self.satelliteslist[cur_idx][1] = result
            return

    def importTransponders(self):
        print('importTransponders')
        self.pollTransponders()
        self.exitSatelliteImport()

    def pollSatellites(self):
        if self.getSatellites_state:
            if self.getSatellites_state == self.thread_is_running:
                if self.requestSatelliteslistRefresh:
                    self.requestSatelliteslistRefresh = False
                    self['list'].setEntries(self.satelliteslist)
            elif self.getSatellites_state == self.thread_is_done:
                self.satTimer.stop()
                self.getSatellites_state = self.thread_is_off
                self.requestSatelliteslistRefresh = False
                self['list'].setEntries(self.satelliteslist)
                row = self['list'].getCurrent()
                if row is None:
                    return
                head = []
                for x in range(1, len(row)):
                    head.append([row[x][1], row[x][3], ''])

                head[0][2] = self.row[0][1]
                head[1][2] = self.row[1][1]
                self['head'].setEntries(head)
                data = self['head'].l.getCurrentSelection()
                data = data[self.currentSelectedColumn + 1]
                self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)
                self.updateSelection()
        else:
            self.getSatellites_state = self.thread_is_running
            thread.start_new_thread(self.getSatellites, (None,))
        return

    def getTransponders(self, dummy=None):
        pass

    def pollTransponders(self):
        if self.getTransponders_state:
            if self.getTransponders_state == self.thread_is_running:
                if self.requestSatelliteslistRefresh:
                    self.requestSatelliteslistRefresh = False
                    self['list'].setEntries(self.satelliteslist)
            elif self.getTransponders_state == self.thread_is_done:
                self.tpTimer.stop()
                self.getTransponders_state = self.thread_is_off
                self['list'].setEntries(self.satelliteslist)
        else:
            self.getTransponders_state = self.thread_is_running
            thread.start_new_thread(self.getTransponders, (None,))
            self.tpTimer.start(1000)
        return None

    def compareFrequency(self, a):
        return int(a.get('frequency'))

    def layoutFinished(self):
        self.satTimer.start(1000)

    def selectSatellite(self):
        self.satelliteSelection(mode=self.modeSelect)

    def unSelectSatellite(self):
        self.satelliteSelection(mode=self.modeUnSelect)

    def selectSatelliteRepeated(self):
        self.down()
        self.satelliteSelection(mode=self.modeSelect, update=False)

    def unSelectSatelliteRepeated(self):
        self.down()
        self.satelliteSelection(mode=self.modeUnSelect, update=False)

    def selectSatelliteFinish(self):
        self['list'].down()
        self['list'].setEntries(self.satelliteslist)

    def satelliteSelection(self, mode=modeToggle, update=True):
        if len(self.satelliteslist):
            cur_idx = self['list'].getSelectedIndex()
            if mode == self.modeToggle:
                selected = self.satelliteslist[cur_idx][0].get('selected', False)
                if selected == False:
                    selected = True
                else:
                    selected = False
            elif mode == self.modeSelect:
                selected = True
            else:
                selected = False
            self.satelliteslist[cur_idx][0].update({'selected': selected})
            if update:
                self['list'].setEntries(self.satelliteslist)

    def getSatellites(self, dummy):
        pass


class SatcoDX(PrestigePanelSatelliteImport):
    thread_is_off = 0
    thread_is_running = 1
    thread_is_done = 2
    transFec = {'1/2': '1',
     '2/3': '2',
     '3/4': '3',
     '5/6': '4',
     '7/8': '5',
     '8/9': '6',
     '3/5': '7',
     '4/5': '8',
     '9/10': '9'}
    listFec2 = ('8/9', '3/5', '4/5', '9/10')
    listFec = ('1/2', '2/3', '3/4', '4/5', '5/6', '7/8', '?')
    listFecAll = ('1/2', '2/3', '3/4', '4/5', '5/6', '7/8', '8/9', '3/5', '4/5', '9/10', '?')

    def __init__(self, session):
        PrestigePanelSatelliteImport.__init__(self, session)
        self.mainTitle = 'SatcoDX Import (www.satcodx.com)'
        self.urlRegions = ('http://www.satcodx1.com', 'http://www.satcodx2.com', 'http://www.satcodx3.com', 'http://www.satcodx4.com', 'http://www.satcodx5.com', 'http://www.satcodx6.com', 'http://www.satcodx7.com', 'http://www.satcodx8.com', 'http://www.satcodx9.com')
        self.siteLanguages = ('eng', 'deu')

    def getTransponders(self, dummy=None):
        print('getTransponders')
        transSystem = {'dvb-s': '0',
         'dvb-s2': '1'}
        transPolarisation = {'h': '0',
         'v': '1',
         'l': '2',
         'r': '3'}
        transModulation = {'dvb-s': '1',
         'dvb-s2': '2'}
        idle = False
        while idle != True:
            idle = True
            for satellite in self.satelliteslist:
                if satellite[0].get('selected', False):
                    idle = False
                    if len(satellite) == 1:
                        url = satellite[0].get('url', '')
                        try:
                            f = urllib2.urlopen(url)
                        except:
                            print('connection failed:', url)
                            return

                        self.setTitle(_('get %s') % url)
                        print('get:', url)
                        state = False
                        td_state = False
                        l = []
                        for row in f.readlines():
                            if state == False:
                                if row.lower().find('<th') != -1:
                                    state = True
                                    td_state = False
                                    l.append(row.lower().replace('<br>', '').replace('<b>', '').replace('</b>', '').replace('</th>', '').replace('</td>', ''))
                                elif td_state == False:
                                    if row.lower().find('<td') != -1:
                                        if row.lower().find('</td') == -1:
                                            td_state = True
                                        l.append(row.lower().replace('<br>', '').replace('<b>', '').replace('</b>', '').replace('</th>', '').replace('</td>', ''))
                                else:
                                    if row.lower().find('td>') != -1:
                                        td_state = False
                                    l.append(row.lower().replace('<br>', '').replace('<b>', '').replace('</b>', '').replace('</th>', '').replace('</td>', ''))
                            else:
                                if row.lower().find('th>') != -1:
                                    state = False
                                if row.lower().find('<th') != -1:
                                    state = False
                                l.append(row.lower().replace('<br>', '').replace('<b>', '').replace('</b>', '').replace('</th>', '').replace('</td>', ''))

                        f.close()
                        tp = {}
                        for x in range(0, len(l) - 5):
                            try:
                                freq = str(int(float(l[x + 1].split()[0]) * 1000000))
                            except:
                                continue

                            href = None
                            fec = None
                            pol = l[x + 2].split()[0]
                            if pol not in ('v', 'h', 'l', 'r'):
                                continue
                            if l[x].find('dvb') != -1:
                                sym = l[x + 3].split()[0]
                                if not sym.isdigit():
                                    print('fail 6')
                                    continue
                                sys = l[x].split()[0]
                                href_raw = l[x + 5].split()
                                href = None
                                for y in href_raw:
                                    if y.find('href=') != -1:
                                        href = y.replace('href=', '').replace('"', '')

                            else:
                                print('keine DVB Kennung')
                                sys = 'dvb-s'
                                if l[x + 6].find('tv-dig') != -1 or l[x + 6].find('r-dig') != -1 or l[x + 6].find('data') != -1 or l[x + 6].find('tv-hd') != -1:
                                    print('offset 6')
                                    fec = l[x + 18].strip()
                                    if l[x + 13].find('mpeg-2') != -1:
                                        sym = l[x + 17].split('>')
                                        sym = sym[len(sym) - 1].strip()
                                        if not sym.isdigit():
                                            print('fail 1')
                                            continue
                                    elif l[x + 8].find('mpeg-2') != -1:
                                        sym = l[x + 12].split('>')
                                        sym = sym[len(sym) - 1].strip()
                                        if not sym.isdigit():
                                            print('fail 5')
                                            continue
                                        fec = l[x + 13].strip()
                                    elif fec in ('1/2', '2/3', '3/4', '4/5', '5/6', '7/8'):
                                        sym = l[x + 17].split('>')
                                        sym = sym[len(sym) - 1].strip()
                                        if not sym.isdigit():
                                            print('fail 2')
                                            continue
                                    else:
                                        fec = l[x + 13].strip()
                                        if fec in ('1/2', '2/3', '3/4', '4/5', '5/6', '7/8'):
                                            sym = l[x + 12].split('>')
                                            sym = sym[len(sym) - 1].strip()
                                            if not sym.isdigit():
                                                print('fail 3')
                                                continue
                                        else:
                                            sym = l[x + 18].split('>')
                                            sym = sym[len(sym) - 1].strip()
                                            if not sym.isdigit():
                                                sym = l[x + 17].split('>')
                                                sym = sym[len(sym) - 1].strip()
                                                if not sym.isdigit():
                                                    print('fail 4')
                                                    continue
                                    href_raw = l[x + 4].split()
                                    for y in href_raw:
                                        if y.find('href=') != -1:
                                            href = y.replace('href=', '').replace('"', '')

                                elif l[x + 5].find('tv-dig') != -1 or l[x + 5].find('r-dig') != -1 or l[x + 5].find('data') != -1:
                                    print('offset 5')
                                    fec = l[x + 17].strip()
                                    sym = l[x + 16].split('>')
                                    sym = sym[len(sym) - 1].strip()
                                    if not sym.isdigit():
                                        continue
                                    if fec in ('1/2', '2/3', '3/4', '4/5', '5/6', '7/8'):
                                        pass
                                    elif l[x + 12].find('mpeg-2') != -1:
                                        pass
                                    else:
                                        continue
                                    print('old Format ???')
                                    sys = 'dvb-s'
                                    print('sym', sym)
                                    print('fec', fec)
                                elif l[x - 1].find('tv-dig') != -1 or l[x - 1].find('r-dig') != -1 or l[x - 1].find('data') != -1:
                                    print('offset -1')
                                    fec = l[x + 11].strip()
                                    sym = l[x + 10].split('>')
                                    sym = sym[len(sym) - 1].strip()
                                    if not sym.isdigit():
                                        continue
                                    if l[x + 7].find('mpeg-2') != -1:
                                        pass
                                    elif fec in ('1/2', '2/3', '3/4', '4/5', '5/6', '7/8'):
                                        pass
                                    else:
                                        continue
                                    print('very old Format ???')
                                    sys = 'dvb-s'
                                    print('sym', sym)
                                    print('fec', fec)
                                    href_raw = l[x + 5].split()
                                    for y in href_raw:
                                        if y.find('src=') != -1:
                                            href = y.replace('src=', '').replace('"', '').replace('.gif', '.jpg')

                                else:
                                    continue
                            try:
                                sym = str(int(sym) * 1000)
                            except:
                                for xx in range(0, 25):
                                    print('%d' % xx, l[x + xx])

                            tp.update({freq + transPolarisation.get(pol): {'frequency': freq,
                                                                 'system': transSystem.get(sys, '0'),
                                                                 'polarization': transPolarisation.get(pol),
                                                                 'symbol_rate': sym,
                                                                 'modulation': transModulation.get(sys, '0'),
                                                                 'fec_inner': self.transFec.get(fec, '0'),
                                                                 'import': 4772300}})

                        transponders = []
                        for key in tp:
                            transponders.append(tp[key])

                        transponders.sort(key=self.compareFrequency)
                        satellite.append(transponders)
                    satellite[0].update({'selected': False})
                    self.requestSatelliteslistRefresh = True

        self.getTransponders_state = self.thread_is_done
        return

    def getSatellites(self, dummy):
        print('getSatellites')
        satellites = []
        self.satelliteslist = satellites
        l = []
        for url in self.urlRegions:
            try:
                f = urllib2.urlopen(url + '/' + self.siteLanguages[0])
            except:
                print('connection failed:', url + '/' + self.siteLanguages[0])
                continue

            self.setTitle(_('get %s') % url + '/' + self.siteLanguages[0])
            for row in f.readlines():
                if row.find('<td') != -1 and row.find('<a') != -1 and row.find('.cgi?') == -1 and row.find('http') == -1:
                    satellite_raw = row.split('<a')[1].split('/>')
                    href = satellite_raw[0].replace('href=', '').strip()
                    satellite = satellite_raw[1].split('<b>')[1].split('/>')[0].split('</a>')[0].strip()
                    tmp = href.split('/')
                    if len(tmp) == 3 and tmp[1].isdigit() and tmp[2] == u'eng' and satellite is not None:
                        pos_raw = satellite.split()
                        pos_raw = pos_raw[len(pos_raw) - 1]
                        pos_raw = pos_raw.split('-')
                        pos_raw = pos_raw[len(pos_raw) - 1].replace(')', '').replace('(', '').lower()
                        west = False
                        if pos_raw.find('w') != -1:
                            west = True
                        pos = int(float(pos_raw.replace('e', '').replace('w', '')) * 10)
                        if west:
                            pos = -pos
                        elif pos > 1799:
                            pos -= 3600
                            west = True
                        satellites.append([{'name': str(satellite),
                          'position': str(pos),
                          'url': url + href}])
                        self.requestSatelliteslistRefresh = True

            f.close()

        self.setTitle(self.mainTitle)
        self.getSatellites_state = self.thread_is_done
        return

    def exitSatelliteImport(self):
        posList = {}
        for sat in self.satelliteslist:
            if len(sat) > 1:
                pos = sat[0].get('position')
                if pos in posList:
                    posList.get(pos)[1].extend(sat[1])
                else:
                    posList.update({pos: sat})

        cleanList = []
        for sat in posList:
            a = posList.get(sat)
            del a[0]['selected']
            newName = a[0]['name'].replace('C-Band:', '').split('-')
            newPos = newName[len(newName) - 1].split()
            newPos = newPos[len(newPos) - 1].replace(')', '').replace('(', '').strip()
            newName = newName[0].strip() + ' (' + newPos + ')'
            a[0].update({'name': newName})
            cleanList.append(a)

        self.close(cleanList)


class KingOfSat(PrestigePanelSatelliteImport):
    thread_is_off = 0
    thread_is_running = 1
    thread_is_done = 2
    transFec = {'1/2': '1',
     '2/3': '2',
     '3/4': '3',
     '5/6': '4',
     '7/8': '5',
     '8/9': '6',
     '3/5': '7',
     '4/5': '8',
     '9/10': '9'}
    listFec2 = ('8/9', '3/5', '4/5', '9/10')
    listFec = ('1/2', '2/3', '3/4', '4/5', '5/6', '7/8', '?')
    listFecAll = ('1/2', '2/3', '3/4', '4/5', '5/6', '7/8', '8/9', '3/5', '4/5', '9/10', '?')
    transModulation = {'qpsk': '1',
     '8psk': '2',
     'qam16': '3'}

    def __init__(self, session):
        PrestigePanelSatelliteImport.__init__(self, session)
        self.urlsSatellites = ('http://de.kingofsat.net', 'http://en.kingofsat.net')
        self.mainTitle = 'KingOfSat Import (www.kingofsat.net)'

    def getTransponders(self, dummy=None):
        print('getTransponders')
        transSystem = {'dvb-s': '0',
         'dvb-s2': '1'}
        transPolarisation = {'h': '0',
         'v': '1',
         'l': '2',
         'r': '3'}
        idle = False
        while idle != True:
            idle = True
            for satellite in self.satelliteslist:
                if satellite[0].get('selected', False):
                    idle = False
                    if len(satellite) == 1:
                        url = satellite[0].get('url', '')
                        try:
                            f = urllib2.urlopen(url)
                        except:
                            print('connection failed:', url)
                            return

                        self.setTitle(_('get %s') % url)
                        print('get:', url)
                        state = False
                        td_state = False
                        l = []
                        for row in f.readlines():
                            if row.lower().find('dir="ltr"') != -1:
                                if row.lower().find('colspan') != -1:
                                    l.append(row.split('dir="ltr"')[1].split('class="bld"'))

                        f.close()
                        tp = {}
                        for x in l:
                            if len(x) < 6:
                                continue
                            freq_raw = x[1].split('&nbsp;')
                            try:
                                freq = str(int(float(freq_raw[0].replace('>', '').strip()) * 1000))
                            except:
                                continue

                            pol = freq_raw[1].split('<')[0].strip().lower()
                            if pol in ('v', 'h', 'l', 'r'):
                                pass
                            else:
                                continue
                            sys = x[3].split('">')
                            sys = sys[len(sys) - 1].replace('- <a', '').replace('</td><td', '').lower().split()
                            mod = sys[1].replace(')', '').replace('(', '').strip()
                            sys = sys[0].strip()
                            if sys in transSystem:
                                pass
                            else:
                                continue
                            sym = x[4].split('<')
                            try:
                                sym = str(int(sym[0].replace('>', '').strip()) * 1000)
                            except:
                                continue

                            fec = x[5].split('<')[0].replace('>', '').strip()
                            if fec in self.transFec:
                                pass
                            else:
                                continue
                            tp.update({freq + transPolarisation.get(pol): {'frequency': freq,
                                                                 'system': transSystem.get(sys, '0'),
                                                                 'polarization': transPolarisation.get(pol),
                                                                 'symbol_rate': sym,
                                                                 'modulation': self.transModulation.get(mod, '0'),
                                                                 'fec_inner': self.transFec.get(fec, '0'),
                                                                 'import': 14315734}})

                        transponders = []
                        for key in tp:
                            transponders.append(tp[key])

                        transponders.sort(key=self.compareFrequency)
                        satellite.append(transponders)
                    satellite[0].update({'selected': False})
                    self.requestSatelliteslistRefresh = True

        self.getTransponders_state = self.thread_is_done

    def getSatellites(self, dummy):
        print('getSatellites')
        satellites = []
        self.satelliteslist = satellites
        for url in self.urlsSatellites:
            try:
                f = urllib2.urlopen(url + '/satellites.php')
                break
            except:
                print('connection failed:', url)
                continue

        self.setTitle(_('get %s') % url)
        l = []
        for row in f.readlines():
            if row.lower().find('<map ') != -1:
                l.append(row)

        f.close()
        raw = l[0].split('</MAP')[0].split('<AREA')
        l = []
        for x in raw:
            if x.find('HREF=') != -1:
                l.append(x.split('HREF=')[1].split('ALT='))

        for x in l:
            href = x[0].replace('"', '').strip()
            satellite = x[1].replace('&deg;', '').replace('"', '').replace('>', '').replace('&uuml;', 'u').strip()
            pos_raw = satellite.split()
            pos_raw = pos_raw[len(pos_raw) - 1].lower().replace(')', '').replace('(', '')
            west = False
            if pos_raw.find('w') != -1:
                west = True
            pos = int(float(pos_raw.replace('e', '').replace('w', '')) * 10)
            if west:
                pos = -pos
            elif pos > 1799:
                pos -= 3600
                west = True
            satellites.append([{'name': str(satellite),
              'position': str(pos),
              'url': url + '/' + href}])
            self.requestSatelliteslistRefresh = True

        self.setTitle(self.mainTitle)
        self.getSatellites_state = self.thread_is_done

    def getSatellites_Name(self, dummy):
        print('getSatellites')
        satellites = []
        self.satelliteslist = satellites
        for url in self.urlsSatellites:
            try:
                f = urllib2.urlopen(url)
                break
            except:
                print('connection failed:', url)
                continue

        self.setTitle(_('get %s') % url)
        state = False
        l = []
        for row in f.readlines():
            if row.find('<option ') != -1:
                l.append(row)

        f.close()
        raw = l[0].split('</option>')
        l = []
        for sat in raw:
            if sat.find('value=') != -1 and sat.find('""') == -1:
                a = sat.replace('<option', '').replace('value=', '').replace('&deg;', '').split('">')
                href = a[0].replace('"', '').strip()
                satellite = a[1].strip()
                print(satellite)
                pos_raw = satellite.split()
                print('a:', pos_raw)
                pos_raw = pos_raw[len(pos_raw) - 1].lower().replace(')', '').replace('(', '')
                print('b:', pos_raw)
                west = False
                if pos_raw.find('w') != -1:
                    west = True
                pos = int(float(pos_raw.replace('e', '').replace('w', '')) * 10)
                if west:
                    pos = -pos
                elif pos > 1799:
                    pos -= 3600
                    west = True
                satellites.append([{'name': str(satellite),
                  'position': str(pos),
                  'url': href}])
                self.requestSatelliteslistRefresh = True

        self.setTitle(_('KingOfSat Import'))
        self.getSatellites_state = self.thread_is_done

    def exitSatelliteImport(self):
        posList = {}
        for sat in self.satelliteslist:
            if len(sat) > 1:
                pos = sat[0].get('position')
                if pos in posList:
                    posList.get(pos)[1].extend(sat[1])
                else:
                    posList.update({pos: sat})

        cleanList = []
        for sat in posList:
            a = posList.get(sat)
            del a[0]['selected']
            cleanList.append(a)

        self.close(cleanList)


class PrestigePanellyngsatsatsScreen(Screen):
    skin = '\n                <screen name="PrestigePanellyngsatsatsScreen" position="center,center" size="640,520" title="Lyngsat-satellites"  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\t\t\n                <widget name="list" position="15,15" size="610,455" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t        \n        </screen>'

    def __init__(self, session):
        self.skin = PrestigePanellyngsatsatsScreen.skin
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        Screen.__init__(self, session)
        self.serversnames = []
        self.serversurls = []
        self.serversurls = ['All',
         'asia.html',
         'europe.html',
         'atlantic.html',
         'america.html']
        self.serversnames = ['All',
         'asia',
         'europe',
         'atlantic',
         'america']
        self.list = []
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okClicked,
         'cancel': self.close}, -2)
        self.ListToMulticontent()

    def cexit(self):
        self.close(None)
        return

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.serversnames
        self['list'].l.setItemHeight(35)
        self['list'].l.setFont(0, gFont('Regular', 25))
        for i in range(0, len(self.events)):
            res.append(MultiContentEntryText(pos=(0, 5), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
            res.append(MultiContentEntryText(pos=(60, 5), size=(430, 120), font=0, flags=RT_HALIGN_LEFT, text=self.events[i], color=16777215, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()

    def okClicked(self):
        selectedserverurl = ''
        try:
            selection = self['list'].getCurrent()
            cindex = self['list'].getSelectionIndex()
            selectedserverurl = str(self.serversurls[cindex])
            selectedservername = self.serversnames[cindex]
            self.session.openWithCallback(self.cexit, LyngSat, selectedserverurl)
        except:
            pass


class PrestigePanelLyngSat(PrestigePanelSatelliteImport):
    thread_is_off = 0
    thread_is_running = 1
    thread_is_done = 2
    transFec = {'1/2': '1',
     '2/3': '2',
     '3/4': '3',
     '5/6': '4',
     '7/8': '5',
     '8/9': '6',
     '3/5': '7',
     '4/5': '8',
     '9/10': '9'}
    listFec2 = ('8/9', '3/5', '4/5', '9/10')
    listFec = ('1/2', '2/3', '3/4', '4/5', '5/6', '7/8', '?')
    listFecAll = ('1/2', '2/3', '3/4', '4/5', '5/6', '7/8', '8/9', '3/5', '4/5', '9/10', '?')

    def __init__(self, session, selectedregion=None):
        PrestigePanelSatelliteImport.__init__(self, session)
        self.baseurl = 'http://lyngsat.com'
        self.urlRegions = ('asia.html', 'europe.html', 'atlantic.html', 'america.html')
        self.setTitle = 'LyngSat satellites'
        self['fspace'].setText('connecting ... please wait')
        self.selectedregion = selectedregion

    def getTransponders(self, dummy=None):
        print('getTransponders')
        transSystem = {'dvb-s': '0',
         'dvb-s2': '1'}
        transPolarisation = {'h': '0',
         'v': '1',
         'l': '2',
         'r': '3'}
        transModulation = {'dvb-s': '1',
         'dvb-s2': '2',
         'qpsk': '1',
         '8psk': '2',
         'qam16': '3'}
        idle = False
        while idle != True:
            idle = True
            for satellite in self.satelliteslist:
                if satellite[0].get('selected', False):
                    idle = False
                    if len(satellite) == 1:
                        url = satellite[0].get('url', '')
                        try:
                            f = urllib2.urlopen(url)
                        except:
                            print('connection failed:', url)
                            self['fspace'].setText(_('get %s') % url)
                            return

                        sat = self.selectedregion.replace('.html', '')
                        turl = os.path.basename(self.baseurl + '/' + url).replace('.html', '')
                        self['fspace'].setText(sat + '-- ' + turl + '  added to satellite.xml')
                        state = False
                        td_state = False
                        l = []
                        for row in f.readlines():
                            if row.lower().find('<td') != -1:
                                l.append(row.lower())

                        f.close()
                        tp = {}
                        for x in range(0, len(l) - 5):
                            if l[x].find('<b>') == -1:
                                continue
                            freq_raw = l[x].lower().replace('</b>', '').split('<b>')[1].split()
                            try:
                                freq = str(int(freq_raw[0].strip()) * 1000)
                            except:
                                continue

                            pol = freq_raw[1].split('<br>')[0].strip()
                            if pol in ('h', 'v', 'l', 'r'):
                                pass
                            else:
                                print('fail 3:', l[x])
                                continue
                            sym_raw = l[x + 5].strip().split('>')
                            try:
                                sym_raw = sym_raw[2].split('-')
                                sym = str(int(sym_raw[0].strip()) * 1000)
                            except:
                                print('fail 5:', l[x + 5])
                                print(sym_raw)
                                continue

                            sys = None
                            mod = None
                            fec = sym_raw[1].split('<')[0].strip()
                            if fec in self.listFec2:
                                sys = 'dvb-s2'
                            elif fec in self.listFec:
                                pass
                            else:
                                fec = '?'
                            if sys is None:
                                if l[x + 4].find('>dvb-s2<') != -1:
                                    sys = 'dvb-s2'
                                else:
                                    sys = 'dvb-s'
                            if l[x + 4].find('8psk') != -1:
                                sys = 'dvb-s2'
                                mod = '8psk'
                            elif l[x + 4].find('qam16') != -1:
                                sys = 'dvb-s2'
                                mod = 'qam16'
                            print(freq)
                            print(pol)
                            print(fec)
                            print(mod)
                            if mod is None:
                                mod = sys
                            tp.update({freq + transPolarisation.get(pol): {'frequency': freq,
                                                                 'system': transSystem.get(sys, '0'),
                                                                 'polarization': transPolarisation.get(pol),
                                                                 'symbol_rate': sym,
                                                                 'modulation': transModulation.get(mod, '0'),
                                                                 'fec_inner': self.transFec.get(fec, '0'),
                                                                 'import': 13749320}})

                        transponders = []
                        for key in tp:
                            transponders.append(tp[key])

                        transponders.sort(key=self.compareFrequency)
                        satellite.append(transponders)
                    satellite[0].update({'selected': False})
                    self.requestSatelliteslistRefresh = True

        self.getTransponders_state = self.thread_is_done
        return

    def getSatellites(self, dummy):
        print('getSatellites')
        satellites = []
        self.satelliteslist = satellites
        l = []
        if self.selectedregion == 'All':
            for url in self.urlRegions:
                try:
                    f = urllib2.urlopen(self.baseurl + '/' + url)
                except:
                    print('connection failed:', self.baseurl + '/' + url)
                    self['fspace'].setText('connection failed:', self.baseurl + '/' + url)

                sat = self.selectedregion.replace('.html', '')
                turl = os.path.basename(self.baseurl + '/' + url).replace('.html', '')
                self['fspace'].setText('getting  ' + sat + '-- ' + turl)
                for row in f.readlines():
                    if row.lower().find('href=') != -1 and row.lower().find('center') != -1:
                        l.append(row.split('href=')[1].replace('</font><font size=1>', '').split('>'))

                f.close()

        else:
            for url in self.urlRegions:
                if url == self.selectedregion:
                    try:
                        f = urllib2.urlopen(self.baseurl + '/' + url)
                    except:
                        print('connection failed:', self.baseurl + '/' + url)
                        self['fspace'].setText('connection failed:', self.baseurl + '/' + url)

                    sat = self.selectedregion.replace('.html', '')
                    turl = os.path.basename(self.baseurl + '/' + url).replace('.html', '')
                    self['fspace'].setText('getting ' + sat + '-- ' + turl)
                    for row in f.readlines():
                        if row.lower().find('href=') != -1 and row.lower().find('center') != -1:
                            l.append(row.split('href=')[1].replace('</font><font size=1>', '').split('>'))

                    f.close()

        for pos in l:
            href = pos[0].replace('"', '').strip()
            try:
                posDir = pos[3].upper().replace('&#176;', '').replace('&deg;', '').split('<')[0].strip()
                posStr = str(float(pos[1].split('<')[0].strip())) + pos[3].replace('&#176;', '').replace('&deg;', '').split('<')[0].strip()
                pos = int(float(pos[1].split('<')[0].strip()) * 10)
                if posDir == 'W':
                    pos = -pos
            except:
                continue

            sat = self.selectedregion.replace('.html', '')
            turl = os.path.basename(href).replace('.html', '')
            self['fspace'].setText('getting ' + sat + '-- ' + turl)
            try:
                f = urllib2.urlopen(href)
            except:
                print('connection failed:', href)
                continue

            name = ''
            for row in f.readlines():
                if row.lower().find('<title>') != -1:
                    name_raw = row.replace('<title>', '').replace('</title>', '').split()
                    for x in range(0, len(name_raw) - 4):
                        name = name + name_raw[x] + ' '

                    break

            f.close()
            satellite = name.strip() + ' (' + posStr + ')'
            print(satellite)
            satellites.append([{'name': str(satellite),
              'position': str(pos),
              'url': href}])
            self.requestSatelliteslistRefresh = True

        self['fspace'].setText('select satellite and press OK include in satellite.xml')
        self.getSatellites_state = self.thread_is_done

    def exitSatelliteImport(self):
        posList = {}
        for sat in self.satelliteslist:
            if len(sat) > 1:
                pos = sat[0].get('position')
                if pos in posList:
                    posList.get(pos)[1].extend(sat[1])
                else:
                    posList.update({pos: sat})

        cleanList = []
        for sat in posList:
            a = posList.get(sat)
            del a[0]['selected']
            newName = a[0]['name'].replace('C-Band:', '').split('-')
            newPos = newName[len(newName) - 1].split()
            newPos = newPos[len(newPos) - 1].replace(')', '').replace('(', '').strip()
            newName = newName[0].strip() + ' (' + newPos + ')'
            a[0].update({'name': newName})
            cleanList.append(a)

        self.close(cleanList)


class Lamedb():

    def __init__(self):
        self.satellitesList = self.translateTransponders(self.getTransponders(self.readLamedb()))

    def readLamedb(self):
        f = open('/etc/enigma2/lamedb', 'r')
        lamedb = f.readlines()
        f.close()
        if lamedb[0].find('/3/') != -1:
            self.version = 3
        elif lamedb[0].find('/4/') != -1:
            self.version = 4
        else:
            print('unknown version: ', lamedb[0])
            return
        print('import version %d' % self.version)
        return lamedb

    def getTransponders(self, lamedb):
        if lamedb is None:
            return
        else:
            collect = False
            state = 0
            transponders = []
            tp = []
            for x in lamedb:
                if x == 'transponders\n':
                    collect = True
                    continue
                if x == 'end\n':
                    break
                y = x.strip().split(':')
                if collect:
                    if y[0] == '/':
                        transponders.append(tp)
                        tp = []
                    else:
                        tp.append(y)

            return transponders

    def translateTransponders(self, transponders):
        t1 = ['namespace', 'tsid', 'onid']
        t2_sv3 = ['frequency',
         'symbol_rate',
         'polarization',
         'fec_inner',
         'position',
         'inversion',
         'system',
         'modulation',
         'rolloff',
         'pilot']
        t2_sv4 = ['frequency',
         'symbol_rate',
         'polarization',
         'fec_inner',
         'position',
         'inversion',
         'flags',
         'system',
         'modulation',
         'rolloff',
         'pilot']
        if transponders is None:
            return
        else:
            tplist = []
            for x in transponders:
                tp = {}
                if len(x[0]) > len(t1):
                    print('zu viele Parameter (t1) in ', x[0])
                    continue
                freq = x[1][0].split()
                if len(freq) != 2:
                    print('zwei Parameter erwartet in ', freq)
                    continue
                x[1][0] = freq[1]
                if freq[0] == 's' or freq[0] == 'S':
                    if self.version == 3 and len(x[1]) > len(t2_sv3) or self.version == 4 and len(x[1]) > len(t2_sv4):
                        print('zu viele Parameter (t2) in ', x[1])
                        continue
                    for y in range(0, len(x[0])):
                        tp.update({t1[y]: x[0][y]})

                    for y in range(0, len(x[1])):
                        if self.version == 3:
                            tp.update({t2_sv3[y]: x[1][y]})
                        elif self.version == 4:
                            tp.update({t2_sv4[y]: x[1][y]})

                    tp.update({'import': 13468991})
                    if int(tp.get('namespace'), 16) / 65536 != int(tp.get('position')):
                        print('Namespace %s und Position %s sind  nicht identisch' % (tp.get('namespace'), tp.get('position')))
                        continue
                elif freq[0] == 'c' or freq[0] == 'C':
                    print('DVB-C')
                    continue
                elif freq[0] == 't' or freq[0] == 'T':
                    print('DVB-T')
                    continue
                tplist.append(tp)

            satlist = {}
            for x in tplist:
                tmp = satlist.get(x.get('position'), [])
                tmp.append(x)
                satlist.update({x.get('position'): tmp})

            del tplist
            print('Anzahl der Satelliten: ', len(satlist))
            for x in satlist:
                print('Position: ', x)
                print('Transponder: ', len(satlist.get(x)))

            return satlist


class Transponder():
    essential = ['frequency', 'polarization', 'symbol_rate']
    niceToHave = ['system',
     'fec_inner',
     'tsid',
     'onid']
    transSystem = {'0': 'DVB-S',
     '1': 'DVB-S2',
     'dvb-s': 'DVB-S',
     'dvb-s2': 'DVB-S2'}
    reTransSystem = {'DVB-S': '0',
     'DVB-S2': '1'}
    transPolarisation = {'0': 'H',
     'h': 'H',
     '1': 'V',
     'v': 'V',
     '2': 'L',
     'cl': 'L',
     'l': 'L',
     '3': 'R',
     'cr': 'R',
     'r': 'R',
     'i': 'i'}
    reTransPolarisation = {'H': '0',
     'V': '1',
     'L': '2',
     'R': '3'}
    transModulation = {'0': 'AUTO',
     '1': 'QPSK',
     '2': '8PSK',
     '3': 'QAM16'}
    reTransModulation = {'AUTO': '0',
     'QPSK': '1',
     '8PSK': '2',
     'QAM16': '3'}
    transRolloff = {'0': '0_35',
     '1': '0_25',
     '2': '0_20'}
    reTransRolloff = {'0_35': '0',
     '0_25': '1',
     '0_20': '2'}
    transOnOff = {'0': 'OFF',
     '1': 'ON',
     '2': 'AUTO'}
    reTransOnOff = {'OFF': '0',
     'ON': '1',
     'AUTO': '2'}
    transFec = {'0': 'FEC_AUTO',
     '1': 'FEC_1_2',
     '2': 'FEC_2_3',
     '3': 'FEC_3_4',
     '4': 'FEC_5_6',
     '5': 'FEC_7_8',
     '6': 'FEC_8_9',
     '7': 'FEC_3_5',
     '8': 'FEC_4_5',
     '9': 'FEC_9_10',
     '15': 'FEC_NONE',
     'auto': 'FEC_AUTO',
     '1/2': 'FEC_1_2',
     '2/3': 'FEC_2_3',
     '3/4': 'FEC_3_4',
     '5/6': 'FEC_5_6',
     '7/8': 'FEC_7_8',
     '8/9': 'FEC_8_9',
     '3/5': 'FEC_3_5',
     '4/5': 'FEC_4_5',
     '9/10': 'FEC_9_10',
     'none': 'FEC_NONE'}
    reTransFec = {'FEC_AUTO': '0',
     'FEC_1_2': '1',
     'FEC_2_3': '2',
     'FEC_3_4': '3',
     'FEC_5_6': '4',
     'FEC_7_8': '5',
     'FEC_8_9': '6',
     'FEC_3_5': '7',
     'FEC_4_5': '8',
     'FEC_9_10': '9',
     'FEC_NONE': '15'}
    onlyDVBS2Fec = ['FEC_8_9',
     'FEC_3_5',
     'FEC_4_5',
     'FEC_9_10']
    transBand = {'KU': ('10700000', '12750000'),
     'C': ('3400000', '4200000')}

    def __init__(self, transponder):
        self.rawData = transponder
        self.system = 'DVB-S'
        self.__frequency = '10700000'
        self.__symbolrate = '27500000'
        self.polarisation = 'H'
        self.modulation = 'QPSK'
        self.pilot = 'OFF'
        self.rolloff = '0_35'
        self.fec = 'FEC_AUTO'
        self.inversion = 'AUTO'
        self.__tsid = '0'
        self.useTsid = False
        self.__onid = '0'
        self.useOnid = False
        self.band = 'KU'
        self.__importColor = None
        self.transponderDoctor(self.rawData)
        return

    def transponderDoctor(self, transponder):
        if not isinstance(transponder, dict):
            print('transponderDoctor: Transponderdaten muessen vom Type DICT sein')
            print(transponder)
            return
        else:
            param = transponder.keys()
            transParam = {}
            for x in param:
                transParam[x] = x.lower()

            if 'polarisation' in transParam:
                transParam.update({'polarization': transParam.get('polarisation').lower()})
                del transParam['polarisation']
            missing = []
            for x in self.essential:
                if x not in transParam:
                    missing.append(x)

            if len(missing):
                print('transponderDoctor: Folgende Parameter fehlen:', missing)
                return
            self.polarisation = self.transPolarisation.get(transponder.get(transParam.get('polarization'), 'i').lower())
            if self.polarisation == 'i':
                print('transponderDoctor: unbekannter Wert fuer Polarisation (%s)' % transParam.get('polarization'))
                return
            self.__frequency = transponder.get(transParam.get('frequency'), 'i').lower()
            self.__symbolrate = transponder.get(transParam.get('symbol_rate'), 'i').lower()
            dvb_s_cnt = 0
            dvb_s2_cnt = 0
            self.__importColor = transponder.get('import', None)
            if 'system' in transParam:
                self.system = self.transSystem.get(transponder.get(transParam.get('system'), 'i').lower())
                if self.system == 'DVB-S':
                    dvb_s_cnt += 1
                if self.system == 'DVB-S2':
                    dvb_s2_cnt += 1
            if 'modulation' in transParam:
                self.modulation = self.transModulation.get(transponder.get(transParam.get('modulation'), 'i').lower())
                if self.modulation == '8PSK' or self.modulation == 'QAM16':
                    dvb_s2_cnt += 1
            if 'pilot' in transParam:
                self.pilot = self.transOnOff.get(transponder.get(transParam.get('pilot'), 'i').lower())
                if self.pilot == 'ON' or self.pilot == 'AUTO':
                    dvb_s2_cnt += 1
            if 'rolloff' in transParam:
                self.rolloff = self.transRolloff.get(transponder.get(transParam.get('rolloff'), 'i').lower())
                if self.rolloff == '0_25':
                    dvb_s2_cnt += 1
            if 'fec_inner' in transParam:
                self.fec = self.transFec.get(transponder.get(transParam.get('fec_inner'), 'i').lower())
                if self.fec in self.onlyDVBS2Fec:
                    dvb_s2_cnt += 1
            if dvb_s2_cnt:
                self.system = 'DVB-S2'
            else:
                self.system = 'DVB-S'
            if 'inversion' in transParam:
                self.inversion = self.transOnOff.get(transponder.get(transParam.get('inversion'), 'i').lower())
            if 'tsid' in transParam:
                self.__tsid = transponder.get(transParam.get('tsid'), 'i').lower()
                self.useTsid = True
            if 'onid' in transParam:
                self.__onid = transponder.get(transParam.get('onid'), 'i').lower()
                self.useOnid = True
            return

    def getFrequency(self):
        return self.__frequency

    def setFrequency(self, frequency):
        if isinstance(frequency, list):
            if len(frequency) == 2:
                if isinstance(frequency[0], int) and isinstance(frequency[1], int):
                    self.__frequency = str(frequency[0] * 1000 + frequency[1])
                    return
        else:
            self.__frequency = str(frequency)

    frequency = property(getFrequency, setFrequency)
    importColor = property(lambda self: self.__importColor)

    def getSymbolrate(self):
        return self.__symbolrate

    def setSymbolrate(self, symbolrate):
        self.__symbolrate = str(symbolrate)

    symbolrate = property(getSymbolrate, setSymbolrate)

    def setTsid(self, newTsid):
        self.__tsid = str(newTsid)

    tsid = property(lambda self: self.__tsid, setTsid)

    def getOnid(self):
        return self.__onid

    def setOnid(self, newOnid):
        self.__onid = str(newOnid)

    onid = property(lambda self: self.__onid, setOnid)

    def exportImportColor(self):
        return {'import': self.__importColor}

    def exportSystem(self):
        return {'system': self.reTransSystem.get(self.system)}

    def exportFec(self):
        return {'fec_inner': self.reTransFec.get(self.fec)}

    def exportFrequency(self):
        return {'frequency': self.__frequency}

    def exportPolarisation(self):
        return {'polarization': self.reTransPolarisation.get(self.polarisation)}

    def exportSymbolrate(self):
        return {'symbol_rate': self.__symbolrate}

    def exportModulation(self):
        return {'modulation': self.reTransModulation.get(self.modulation)}

    def exportOnid(self):
        return {'onid': self.__onid}

    def exportTsid(self):
        return {'tsid': self.__tsid}

    def exportInversion(self):
        return {'inversion': self.reTransOnOff.get(self.inversion)}

    def exportPilot(self):
        return {'pilot': self.reTransOnOff.get(self.pilot)}

    def exportRolloff(self):
        return {'rolloff': self.reTransRolloff.get(self.rolloff)}

    def exportClean(self):
        res = {}
        res.update(self.exportSystem())
        res.update(self.exportFec())
        res.update(self.exportFrequency())
        res.update(self.exportPolarisation())
        res.update(self.exportSymbolrate())
        res.update(self.exportModulation())
        if self.useOnid:
            res.update(self.exportOnid())
        if self.useTsid:
            res.update(self.exportTsid())
        if self.inversion != 'AUTO':
            res.update(self.exportInversion())
        if self.system == 'DVB-S2':
            if self.pilot != 'OFF':
                res.update(self.exportPilot())
        if self.rolloff != '0_35':
            res.update(self.exportRolloff())
        return res

    def exportAll(self):
        res = self.exportClean()
        res.update(self.exportImportColor())
        return res


class TransponderList(MenuList):

    def __init__(self):
        MenuList.__init__(self, list=[], content=eListboxPythonMultiContent)
        self.rowHight = 24
        self.l.setItemHeight(24)
        self.l.setFont(0, gFont('Regular', 20))

    def setEntries(self, transponderlist):
        transRolloff = {'0_35': '0.35',
         '0_25': '0.25',
         '0_20': '0.20'}
        transFec = {'FEC_AUTO': 'auto',
         'FEC_1_2': '1/2',
         'FEC_2_3': '2/3',
         'FEC_3_4': '3/4',
         'FEC_5_6': '5/6',
         'FEC_7_8': '7/8',
         'FEC_8_9': '8/9',
         'FEC_3_5': '3/5',
         'FEC_4_5': '4/5',
         'FEC_9_10': '9/10',
         'FEC_NONE': 'none'}
        res = []
        z = 0
        for x in transponderlist:
            transponder = Transponder(x)
            tp = []
            tp.append(z)
            z += 1
            calc_xpos = lambda a: a[len(a) - 1][1] + a[len(a) - 1][3]
            color = transponder.importColor
            tp.append(MultiContentEntryText(pos=(0, 0), size=(110, self.rowHight), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_TOP, text=transponder.system, color=color, border_width=1, border_color=12092939))
            tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(100, self.rowHight), font=0, flags=RT_HALIGN_RIGHT | RT_VALIGN_TOP, text=str(int(transponder.frequency) / 1000), color=color, border_width=1, border_color=12092939))
            tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(45, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.polarisation, color=color, border_width=1, border_color=12092939))
            tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(100, self.rowHight), font=0, flags=RT_HALIGN_RIGHT | RT_VALIGN_TOP, text=str(int(transponder.symbolrate) / 1000), color=color, border_width=1, border_color=12092939))
            tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(75, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transFec.get(transponder.fec), color=color, border_width=1, border_color=12092939))
            tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(85, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.modulation, color=color, border_width=1, border_color=12092939))
            tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(70, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transRolloff.get(transponder.rolloff), color=color, border_width=1, border_color=12092939))
            tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(60, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.inversion, color=color, border_width=1, border_color=12092939))
            tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(60, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.pilot, color=color, border_width=1, border_color=12092939))
            tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(90, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.tsid, color=color, border_width=1, border_color=12092939))
            tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(90, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.onid, color=color, border_width=1, border_color=12092939))
            res.append(tp)
        self.l.setList(res)


class PrestigePanelTransponderEditor(Screen, ConfigListScreen, Transponder):
    skin = '\n                <screen name="PrestigePanelTransponderEditor" position="center,center" size="640,520" title="Edit"  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\t\n\t\t<ePixmap pixmap="~/ddbuttons/red.png" position="25,25" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/green.png" position="165,25" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/yellow.png" position="305,25" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/blue.png" position="445,25" size="140,40" alphatest="on" />\n\t\t<widget name="key_red" position="25,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="165,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="305,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="445,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="config" position="25,75" size="590,340" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t</screen>'

    def __init__(self, session, transponderData=None):
        self.skin = PrestigePanelTransponderEditor.skin
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        Screen.__init__(self, session)
        Transponder.__init__(self, transponderData)
        self.createConfig()
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'cancel': self.cancel,
         'ok': self.okExit,
         'green': self.okExit}, -1)
        self['key_red'] = Button('')
        self['key_green'] = Button(_('ok'))
        self['key_yellow'] = Button('')
        self['key_blue'] = Button('')
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self.onLayoutFinish.append(self.layoutFinished)
        self.createSetup()

    def layoutFinished(self):
        self.setTitle('Edit ')

    def createConfig(self):
        self.configTransponderSystem = ConfigSelection([('DVB-S', _('DVB-S')), ('DVB-S2', _('DVB-S2'))], self.system)
        self.configTransponderFrequency = ConfigFloat(default=[int(self.frequency) / 1000, int(self.frequency) % 1000], limits=[(0, 99999), (0, 999)])
        self.configTransponderPolarisation = ConfigSelection([('H', _('horizontal')),
         ('V', _('vertical')),
         ('L', _('circular left')),
         ('R', _('circular right'))], self.polarisation)
        self.configTransponderSymbolrate = ConfigInteger(default=int(self.symbolrate) / 1000, limits=(0, 99999))
        self.configTransponderFec = ConfigSelection([('FEC_AUTO', _('auto')),
         ('FEC_1_2', _('1/2')),
         ('FEC_2_3', _('2/3')),
         ('FEC_3_4', _('3/4')),
         ('FEC_5_6', _('5/6')),
         ('FEC_7_8', _('7/8'))], self.fec)
        self.configTransponderFec2 = ConfigSelection([('FEC_AUTO', _('auto')),
         ('FEC_1_2', _('1/2')),
         ('FEC_2_3', _('2/3')),
         ('FEC_3_4', _('3/4')),
         ('FEC_5_6', _('5/6')),
         ('FEC_7_8', _('7/8')),
         ('FEC_8_9', _('8/9')),
         ('FEC_3_5', _('3/5')),
         ('FEC_4_5', _('4/5')),
         ('FEC_9_10', _('9/10'))], self.fec)
        self.configTransponderInversion = ConfigSelection([('OFF', _('off')), ('ON', _('on')), ('AUTO', _('auto'))], self.inversion)
        self.configTransponderModulation = ConfigSelection([('AUTO', _('auto')),
         ('QPSK', _('QPSK')),
         ('8PSK', _('8PSK')),
         ('QAM16', _('QAM16'))], self.modulation)
        self.configTransponderRollOff = ConfigSelection([('0_35', _('0.35')), ('0_25', _('0.25')), ('0_20', _('0.20'))], self.rolloff)
        self.configTransponderPilot = ConfigSelection([('OFF', _('off')), ('ON', _('on')), ('AUTO', _('auto'))], self.pilot)
        self.configTransponderUseTsid = ConfigYesNo(default=self.useTsid)
        self.configTransponderUseOnid = ConfigYesNo(default=self.useOnid)
        self.configTransponderTsid = ConfigInteger(default=int(self.tsid), limits=(0, 65535))
        self.configTransponderOnid = ConfigInteger(default=int(self.onid), limits=(0, 65535))

    def createSetup(self):
        self.list = []
        self.list.append(getConfigListEntry(_('System'), self.configTransponderSystem))
        if self.system == 'DVB-S' or self.system == 'DVB-S2':
            self.list.append(getConfigListEntry(_('Freqency'), self.configTransponderFrequency))
            self.list.append(getConfigListEntry(_('Polarisation'), self.configTransponderPolarisation))
            self.list.append(getConfigListEntry(_('Symbolrate'), self.configTransponderSymbolrate))
        if self.system == 'DVB-S':
            self.list.append(getConfigListEntry(_('FEC'), self.configTransponderFec))
        elif self.system == 'DVB-S2':
            self.list.append(getConfigListEntry(_('FEC'), self.configTransponderFec2))
        if self.system == 'DVB-S' or self.system == 'DVB-S2':
            self.list.append(getConfigListEntry(_('Inversion'), self.configTransponderInversion))
            self.list.append(getConfigListEntry(_('use tsid'), self.configTransponderUseTsid))
            self.list.append(getConfigListEntry(_('use onid'), self.configTransponderUseOnid))
        if self.system == 'DVB-S2':
            self.list.append(getConfigListEntry(_('Modulation'), self.configTransponderModulation))
            self.list.append(getConfigListEntry(_('RollOff'), self.configTransponderRollOff))
            self.list.append(getConfigListEntry(_('Pilot'), self.configTransponderPilot))
        if self.system == 'DVB-S' or self.system == 'DVB-S2':
            if self.useTsid:
                self.list.append(getConfigListEntry(_('TSID'), self.configTransponderTsid))
            if self.useOnid:
                self.list.append(getConfigListEntry(_('ONID'), self.configTransponderOnid))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def cancel(self):
        self.close(None)
        return

    def okExit(self):
        self.system = self.configTransponderSystem.value
        self.frequency = self.configTransponderFrequency.value
        self.polarisation = self.configTransponderPolarisation.value
        self.symbolrate = self.configTransponderSymbolrate.value * 1000
        if self.system == 'DVB-S':
            self.fec = self.configTransponderFec.value
        else:
            self.fec = self.configTransponderFec2.value
        self.inversion = self.configTransponderInversion.value
        self.modulation = self.configTransponderModulation.value
        self.rolloff = self.configTransponderRollOff.value
        self.pilot = self.configTransponderPilot.value
        self.tsid = self.configTransponderTsid.value
        self.onid = self.configTransponderOnid.value
        self.close(self.exportAll())

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.newConfig()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.newConfig()

    def newConfig(self):
        print('newConfig')
        checkList = (self.configTransponderSystem, self.configTransponderUseTsid, self.configTransponderUseOnid)
        for x in checkList:
            if self['config'].getCurrent()[1] == x:
                if x == self.configTransponderSystem:
                    self.system = self.configTransponderSystem.value
                elif x == self.configTransponderUseTsid:
                    self.useTsid = self.configTransponderUseTsid.value
                elif x == self.configTransponderUseOnid:
                    self.useOnid = self.configTransponderUseOnid.value
            self.createSetup()


class PrestigePanelTranspondersEditor(Screen):
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
        skin = '\n                <screen name="PrestigePanelSatellitesEditor" position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frame.png" position="0,0" size="920,600" transparent="1"/>\t\n\n\t\t<ePixmap pixmap="~/ddbuttons/red.png" position="30,25" size="140,50" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/green.png" position="170,25" size="140,50" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/yellow.png" position="310,25" size="140,50" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/blue.png" position="450,25" size="140,50" alphatest="on" />\n\t\t\n\t\t<widget name="key_red" position="30,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="170,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="310,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="450,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="list" position="20,89" size="880,456" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<widget name="head" position="20,65" size="880,24" scrollbarMode="showNever" transparent="1" zPosition="2" />\n\t\t</screen>'
    else:
        skin = '\n\t\t<screen position="center,center" size="560,430" title="Transponders Editor" >\n                <screen name="PrestigePanelSatellitesEditor" position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frame.png" position="0,0" size="920,600" transparent="1"/>\t\n\n\t\t<ePixmap pixmap="~/ddbuttons/red.png" position="30,25" size="140,50" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/green.png" position="170,25" size="140,50" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/yellow.png" position="310,25" size="140,50" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/blue.png" position="450,25" size="140,50" alphatest="on" />\n\n\t\t<widget name="key_red" position="30,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="170,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="310,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="450,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="list" position="0,64" size="560,240" scrollbarMode="showOnDemand" />\n\t\t<widget name="head" position="0,40" size="560,24" scrollbarMode="showNever" />\n\t\t</screen>'

    def __init__(self, session, satellite=None):
        self.skin = PrestigePanelTranspondersEditor.skin
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['SatellitesEditorActions'], {'nextPage': self.nextPage,
         'prevPage': self.prevPage,
         'select': self.editTransponder,
         'exit': self.cancel,
         'left': self.left,
         'leftUp': self.doNothing,
         'leftRepeated': self.doNothing,
         'right': self.right,
         'rightUp': self.doNothing,
         'rightRepeated': self.doNothing,
         'up': self.up,
         'upUp': self.upUp,
         'upRepeated': self.upRepeated,
         'down': self.down,
         'downUp': self.downUp,
         'downRepeated': self.downRepeated,
         'red': self.removeTransponder,
         'green': self.editTransponder,
         'yellow': self.addTransponder,
         'blue': self.sortColumn}, -1)
        self.transponderslist = satellite[1]
        self.satelliteName = satellite[0].get('name')
        self['key_red'] = Button(_('remove'))
        self['key_green'] = Button(_('edit'))
        self['key_yellow'] = Button(_('add'))
        self['key_blue'] = Button(_('sort'))
        self['head'] = Head()
        self.currentSelectedColumn = 0
        self['list'] = TransponderList()
        self['list'].setEntries(self.transponderslist)
        self.row = [['system', _('1'), False],
         ['freq', _('2'), False],
         ['pol', _('3'), False],
         ['sr', _('4'), False],
         ['fec', _('5'), False],
         ['modul', _('6'), False],
         ['rolloff', _('7'), False],
         ['invers', _('8'), False],
         ['pilot', _('9'), False],
         ['tsid', _('10'), False],
         ['onid', _('11'), False]]
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle('Transponders Editor (%s)' % self.satelliteName)
        row = self['list'].getCurrent()
        if row is None:
            return
        else:
            head = []
            for x in range(1, len(row)):
                head.append((row[x][1], row[x][3], self.row[x - 1][0]))

            self['head'].setEntries(head)
            data = self['head'].l.getCurrentSelection()
            data = data[self.currentSelectedColumn + 1]
            self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)
            self.updateSelection()
            return

    def updateSelection(self):
        row = self['list'].l.getCurrentSelection()
        if row is None:
            return
        else:
            firstColumn = row[1]
            lastColumn = row[len(row) - 1]
            self['list'].l.setSelectionClip(eRect(firstColumn[1], firstColumn[0], lastColumn[1] + lastColumn[3], lastColumn[4]), True)
            return

    def doNothing(self):
        pass

    def left(self):
        print('left')
        if self.currentSelectedColumn:
            self.currentSelectedColumn -= 1
            data = self['head'].l.getCurrentSelection()
            data = data[self.currentSelectedColumn + 1]
            self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)

    def right(self):
        print('right')
        if self.currentSelectedColumn < len(self.row) - 1:
            self.currentSelectedColumn += 1
            data = self['head'].l.getCurrentSelection()
            data = data[self.currentSelectedColumn + 1]
            self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)

    def upRepeated(self):
        self['list'].up()
        self.updateSelection()

    def downRepeated(self):
        self['list'].down()
        self.updateSelection()

    def nextPage(self):
        self['list'].pageUp()
        self.lastSelectedIndex = self['list'].getSelectedIndex()
        self.updateSelection()

    def prevPage(self):
        self['list'].pageDown()
        self.lastSelectedIndex = self['list'].getSelectedIndex()
        self.updateSelection()

    def up(self):
        self['list'].up()
        self.lastSelectedIndex = self['list'].getSelectedIndex()
        self.updateSelection()

    def down(self):
        self['list'].down()
        self.lastSelectedIndex = self['list'].getSelectedIndex()
        self.updateSelection()

    def upUp(self):
        cur_idx = self['list'].getSelectedIndex()
        if self.lastSelectedIndex != cur_idx:
            self.lastSelectedIndex = cur_idx

    def downUp(self):
        cur_idx = self['list'].getSelectedIndex()
        if self.lastSelectedIndex != cur_idx:
            self.lastSelectedIndex = cur_idx

    def addTransponder(self):
        print('addTransponder')
        self.session.openWithCallback(self.finishedTransponderAdd, PrestigePanelTransponderEditor)

    def editTransponder(self):
        print('editTransponder')
        if not len(self.transponderslist):
            return
        cur_idx = self['list'].getSelectedIndex()
        self.session.openWithCallback(self.finishedTransponderEdit, PrestigePanelTransponderEditor, self.transponderslist[cur_idx])

    def finishedTransponderEdit(self, result):
        print('finishedTransponderEdit')
        if result is None:
            return
        else:
            cur_idx = self['list'].getSelectedIndex()
            self.transponderslist[cur_idx] = result
            self['list'].setEntries(self.transponderslist)
            return

    def finishedTransponderAdd(self, result):
        print('finishedTransponderAdd')
        if result is None:
            return
        else:
            self.transponderslist.append(result)
            self['list'].setEntries(self.transponderslist)
            return

    def removeTransponder(self):
        print('removeTransponder')
        if len(self.transponderslist):
            cb_func = lambda ret: not ret or self.deleteTransponder()
            self.session.openWithCallback(cb_func, MessageBox, _('Remove Transponder?'), MessageBox.TYPE_YESNO)

    def deleteTransponder(self):
        if len(self.transponderslist):
            self.transponderslist.pop(self['list'].getSelectedIndex())
            self['list'].setEntries(self.transponderslist)

    def cancel(self):
        self.close(None)
        return

    def compareColumn(self, a):
        return int(a.get(self.row[self.currentSelectedColumn][0], '-1'))

    def sortColumn(self):
        rev = self.row[self.currentSelectedColumn][2]
        self.transponderslist.sort(key=self.compareColumn, reverse=rev)
        if rev:
            self.row[self.currentSelectedColumn][2] = False
        else:
            self.row[self.currentSelectedColumn][2] = True
        self['list'].setEntries(self.transponderslist)
        self.update = True


class SatelliteList(MenuList):

    def __init__(self):
        MenuList.__init__(self, list=[], content=eListboxPythonMultiContent)
        self.l.setItemHeight(24)
        self.l.setFont(0, gFont('Regular', 20))

    def setEntries(self, satelliteslist):
        print('setEntries', len(satelliteslist))
        res = []
        for x in satelliteslist:
            satparameter = x[0]
            satentry = []
            pos = int(satparameter.get('position'))
            if pos < 0:
                pos += 3600
            satentry.append(pos)
            color = None
            color_sel = None
            if satparameter.get('selected', False):
                color = 0
                color_sel = 65344
            backcolor = None
            backcolor_sel = None
            if len(x) == 1:
                backcolor = 1644912
                backcolor_sel = 9466996
            satentry.append(MultiContentEntryText(pos=(0, 0), size=(730, 24), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_TOP, text=satparameter.get('name'), color=color, color_sel=color_sel, backcolor=backcolor, backcolor_sel=backcolor_sel, border_width=1, border_color=15792383))
            pos = int(satparameter.get('position'))
            posStr = str(abs(pos) / 10) + '.' + str(abs(pos) % 10)
            if pos < 0:
                posStr = posStr + ' ' + _('West')
            if pos > 0:
                posStr = posStr + ' ' + _('East')
            satentry.append(MultiContentEntryText(pos=(730, 0), size=(170, 24), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_TOP, text=posStr, color=color, color_sel=color_sel, backcolor=backcolor, backcolor_sel=backcolor_sel, border_width=1, border_color=15792383))
            res.append(satentry)

        self.l.setList(res)
        return


class PrestigePanelSatInfo(Screen):
    skin = '\n                <screen name="PrestigePanelTransponderEditor" position="center,center" size="640,520" title="Satellite info"  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\n\t\t<widget name="polhead" position="60,310" size="500,24" />\n\t\t<widget name="bandlist" position="15,334" size="55,72" />\n\t\t<widget name="infolist" position="70,334" size="500,72" />\n\t\t</screen>'

    def __init__(self, session, satellite):
        Screen.__init__(self, session)
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        self.satellite = satellite
        self['actions'] = ActionMap(['OkCancelActions'], {'ok': self.close,
         'cancel': self.close}, -1)
        self['infolist'] = MenuList([])
        self['infolist'].l = eListboxPythonMultiContent()
        self['infolist'].l.setSelectionClip(eRect(0, 0, 0, 0))
        self['infolist'].l.setItemHeight(24)
        self['infolist'].l.setFont(0, gFont('Regular', 20))
        self['polhead'] = MenuList([])
        self['polhead'].l = eListboxPythonMultiContent()
        self['polhead'].l.setSelectionClip(eRect(0, 0, 0, 0))
        self['polhead'].l.setItemHeight(24)
        self['polhead'].l.setFont(0, gFont('Regular', 20))
        self['bandlist'] = MenuList([])
        self['bandlist'].l = eListboxPythonMultiContent()
        self['bandlist'].l.setSelectionClip(eRect(0, 0, 0, 0))
        self['bandlist'].l.setItemHeight(24)
        self['bandlist'].l.setFont(0, gFont('Regular', 20))
        self.getInfo()

    def getInfo(self):
        self.name = self.satellite[0].get('name')
        self.position = self.satellite[0].get('position')
        self.tp_all = len(self.satellite[1])
        self.tp_ku = 0
        self.tp_c = 0
        self.tp_other = 0
        self.tp_ku_v = 0
        self.tp_ku_h = 0
        self.tp_ku_l = 0
        self.tp_ku_r = 0
        self.tp_ku_v2 = 0
        self.tp_ku_h2 = 0
        self.tp_ku_l2 = 0
        self.tp_ku_r2 = 0
        self.tp_c_v = 0
        self.tp_c_h = 0
        self.tp_c_l = 0
        self.tp_c_r = 0
        self.tp_c_v2 = 0
        self.tp_c_h2 = 0
        self.tp_c_l2 = 0
        self.tp_c_r2 = 0
        self.tp_ku_dvb_s = 0
        self.tp_ku_dvb_s2 = 0
        self.tp_c_dvb_s = 0
        self.tp_c_dvb_s2 = 0
        for tp in self.satellite[1]:
            freq = int(tp.get('frequency'))
            pol = tp.get('polarization')
            system = tp.get('system')
            if freq >= 10700000 and freq <= 12750000:
                if system == '0':
                    if pol == '0':
                        self.tp_ku_h += 1
                    elif pol == '1':
                        self.tp_ku_v += 1
                    elif pol == '2':
                        self.tp_ku_l += 1
                    elif pol == '3':
                        self.tp_ku_r += 1
                elif system == '1':
                    if pol == '0':
                        self.tp_ku_h2 += 1
                    elif pol == '1':
                        self.tp_ku_v2 += 1
                    elif pol == '2':
                        self.tp_ku_l2 += 1
                    elif pol == '3':
                        self.tp_ku_r2 += 1
            elif freq >= 3400000 and freq <= 4200000:
                if system == '0':
                    if pol == '0':
                        self.tp_c_h += 1
                    elif pol == '1':
                        self.tp_c_v += 1
                    elif pol == '2':
                        self.tp_c_l += 1
                    elif pol == '3':
                        self.tp_c_r += 1
                elif system == '1':
                    if pol == '0':
                        self.tp_c_h2 += 1
                    elif pol == '1':
                        self.tp_c_v2 += 1
                    elif pol == '2':
                        self.tp_c_l2 += 1
                    elif pol == '3':
                        self.tp_c_r2 += 1

        entryList = (_('Band'), _('Ku'), _('C'))
        l = []
        for entry in entryList:
            bandList = [None]
            bandList.append(MultiContentEntryText(pos=(0, 0), size=(55, 24), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=entry, border_width=1, border_color=15792383))
            l.append(bandList)

        self['bandlist'].l.setList(l)
        calc_xpos = lambda a: a[len(a) - 1][1] + a[len(a) - 1][3]
        entryList = (_('horizontal'),
         _('vertical'),
         _('left'),
         _('right'))
        xpos = 0
        polarisationList = [None]
        for entry in entryList:
            polarisationList.append(MultiContentEntryText(pos=(xpos, 0), size=(125, 24), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=entry, border_width=1, border_color=15792383))
            xpos = calc_xpos(polarisationList)

        self['polhead'].l.setList([polarisationList])
        l = []
        infolist = [None]
        entryList = (('dvb-s', 60),
         ('dvb-s2', 65),
         ('dvb-s', 60),
         ('dvb-s2', 65),
         ('dvb-s', 60),
         ('dvb-s2', 65),
         ('dvb-s', 60),
         ('dvb-s2', 65))
        xpos = 0
        for entry in entryList:
            infolist.append(MultiContentEntryText(pos=(xpos, 0), size=(entry[1], 24), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=entry[0], border_width=1, border_color=15792383))
            xpos = calc_xpos(infolist)

        l.append(infolist)
        infolist = [None]
        entryList = ((self.tp_ku_h, 60),
         (self.tp_ku_h2, 65),
         (self.tp_ku_v, 60),
         (self.tp_ku_v2, 65),
         (self.tp_ku_l, 60),
         (self.tp_ku_l2, 65),
         (self.tp_ku_r, 60),
         (self.tp_ku_r2, 65))
        xpos = 0
        for entry in entryList:
            infolist.append(MultiContentEntryText(pos=(xpos, 0), size=(entry[1], 24), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=str(entry[0]).lstrip('0'), border_width=1, border_color=15792383))
            xpos = calc_xpos(infolist)

        l.append(infolist)
        infolist = [None]
        entryList = ((self.tp_c_h, 60),
         (self.tp_c_h2, 65),
         (self.tp_c_v, 60),
         (self.tp_c_v2, 65),
         (self.tp_c_l, 60),
         (self.tp_c_l2, 65),
         (self.tp_c_r, 60),
         (self.tp_c_r2, 65))
        xpos = 0
        for entry in entryList:
            infolist.append(MultiContentEntryText(pos=(xpos, 0), size=(entry[1], 24), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=str(entry[0]).lstrip('0'), border_width=1, border_color=15792383))
            xpos = calc_xpos(infolist)

        l.append(infolist)
        self['infolist'].l.setList(l)
        return


class PrestigePanelSatEditor(Screen, ConfigListScreen):
    flagNetworkScan = 1
    flagUseBAT = 2
    flagUseONIT = 4
    skin = '\n                <screen name="PrestigePanelSatEditor" position="center,center" size="640,520" title="Edit"  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\n\t\t<ePixmap pixmap="~/ddbuttons/red.png" position="25,25" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/green.png" position="165,25" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/yellow.png" position="305,25" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/blue.png" position="445,25" size="140,40" alphatest="on" />\n\t\t<widget name="key_red" position="25,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="165,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="305,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="445,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="config" position="25,65" size="590,276" scrollbarMode="showOnDemand"  transparent="1" zPosition="2" />\n\t\t</screen>'

    def __init__(self, session, satelliteData=None):
        self.skin = PrestigePanelSatEditor.skin
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        Screen.__init__(self, session)
        self.satelliteData = satelliteData
        self.satelliteOrientation = 'east'
        if self.satelliteData is not None:
            self.satelliteName = self.satelliteData.get('name', 'new satellite')
            satellitePosition = int(self.satelliteData.get('position', '0'))
            if satellitePosition < 0:
                self.satelliteOrientation = 'west'
            satellitePosition = abs(satellitePosition)
            self.satellitePosition = [satellitePosition / 10, satellitePosition % 10]
            self.satelliteFlags = int(self.satelliteData.get('flags', '1'))
        else:
            self.satelliteName = 'new satellite'
            self.satellitePosition = [0, 0]
            self.satelliteFlags = 1
        self.createConfig()
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'cancel': self.cancel,
         'ok': self.okExit,
         'green': self.okExit}, -1)
        self['key_red'] = Button()
        self['key_green'] = Button(_('ok'))
        self['key_yellow'] = Button('')
        self['key_blue'] = Button('')
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self.onLayoutFinish.append(self.layoutFinished)
        self.createSetup()
        return

    def layoutFinished(self):
        self.setTitle('Edit ' + self.satelliteName)

    def createConfig(self):
        self.configSatelliteName = ConfigText(default=self.satelliteName, visible_width=50, fixed_size=False)
        self.configSatellitePosition = ConfigFloat(default=self.satellitePosition, limits=[(0, 179), (0, 9)])
        self.configSatelliteOrientation = ConfigSelection([('east', _('East')), ('west', _('West'))], self.satelliteOrientation)
        self.configSatelliteFlagNetworkScan = ConfigYesNo(default=self.satelliteFlags & self.flagNetworkScan and True)
        self.configSatelliteFlagUseBAT = ConfigYesNo(default=self.satelliteFlags & self.flagUseBAT and True)
        self.configSatelliteFlagUseONIT = ConfigYesNo(default=self.satelliteFlags & self.flagUseONIT and True)

    def createSetup(self):
        self.list = []
        self.list.append(getConfigListEntry(_('Name'), self.configSatelliteName))
        self.list.append(getConfigListEntry(_('Position'), self.configSatellitePosition))
        self.list.append(getConfigListEntry(_('Orientation'), self.configSatelliteOrientation))
        self.list.append(getConfigListEntry(_('Network scan'), self.configSatelliteFlagNetworkScan))
        self.list.append(getConfigListEntry(_('BAT'), self.configSatelliteFlagUseBAT))
        self.list.append(getConfigListEntry(_('ONIT'), self.configSatelliteFlagUseONIT))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def cancel(self):
        self.close(None)
        return

    def okExit(self):
        if self.configSatelliteFlagNetworkScan.value:
            satelliteFlags = self.flagNetworkScan + (self.configSatelliteFlagUseBAT.value and self.flagUseBAT) + (self.configSatelliteFlagUseONIT.value and self.flagUseONIT)
            satellitePosition = self.configSatellitePosition.value[0] * 10 + self.configSatellitePosition.value[1]
            satellitePosition = self.configSatelliteOrientation.value == 'west' and -satellitePosition
        satelliteData = {'name': self.configSatelliteName.value,
         'flags': str(satelliteFlags),
         'position': str(satellitePosition)}
        self.close(satelliteData)


class Head(HTMLComponent, GUIComponent):

    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setSelectionClip(eRect(0, 0, 0, 0))
        self.l.setItemHeight(24)
        self.l.setFont(0, gFont('Regular', 20))

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)

    def setEntries(self, data=None):
        res = [None]
        if data is not None:
            for x in data:
                res.append(MultiContentEntryText(pos=(x[0], 0), size=(x[1], 24), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=x[2], color=12632256, backcolor=625428280, color_sel=16777215, backcolor_sel=627073024, border_width=1, border_color=15792383))
        self.l.setList([res])
        return


class PrestigePanelMenuSelection(Screen):
    skin = '\n                <screen name="PrestigePanelMenuSelection" position="center,center" size="640,520" title="updates satellites"  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\t\t\n                <widget name="menulist" position="15,15" size="610,455" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\t\n\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        actionList = []
        actionList.append(_('Kingofsat-recommonded'))
        actionList.append(_('Kingofsat-Feeds'))
        actionList.append(_('Satbeams'))
        actionList.append(_('LyngSat-All satellites'))
        actionList.append(_('LyngSat-Europe satellites'))
        actionList.append(_('LyngSat-Asia satellites'))
        actionList.append(_('LyngSat-Atlantic satellites'))
        actionList.append(_('LyngSat-America satellites'))
        actionList.append(_('Internet Settings loader'))
        self['menulist'] = MenuList(actionList)
        self['actions'] = ActionMap(['OkCancelActions'], {'ok': self.okbuttonClick,
         'cancel': self.cancel}, -1)

    def okbuttonClick(self):
        print('okbuttonClick')
        self.close(self['menulist'].getCurrent())

    def cancel(self):
        self.close(None)
        return


class PrestigePanelSatellitesEditor(Screen):
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
        skin = '\n                <screen name="PrestigePanelSatellitesEditor" position="center,center" size="920,600" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/frame.png" position="0,0" size="920,600" transparent="1"/>\t\n\n\t\t<ePixmap pixmap="~/ddbuttons/red.png" position="30,25" size="140,50" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/green.png" position="170,25" size="140,50" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/yellow.png" position="310,25" size="140,50" alphatest="on" />\n\t\t<ePixmap pixmap="~/ddbuttons/blue.png" position="450,25" size="140,50" alphatest="on" />\n\t\t<ePixmap pixmap="~/buttons/menu.png" position="620,25" size="140,50" alphatest="on" />\t\t\n\t\t<widget name="key_red" position="30,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="170,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="310,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="450,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="menu" position="650,25" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\t\t\n\t\t<widget name="list" position="20,89" size="880,360" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n\t\t<widget name="head" position="20,65" size="880,24" scrollbarMode="showNever" transparent="1" zPosition="2" />\n\t\t<widget name="polhead" position="80,460" size="840,24" transparent="1" zPosition="2" />\n\t\t<widget name="bandlist" position="20,489" size="60,72" transparent="1" zPosition="2" />\n\t\t<widget name="infolist" position="80,489" size="840,72" transparent="1" zPosition="2" />\n\t\t</screen>'
    else:
        skin = '\n                <screen name="PrestigePanelSatellitesEditor" position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="~/images/framesd.png" position="0,0" size="640,520"/>\t\n\t\t<ePixmap  pixmap="~/ddbuttons/green.png" position="140,0" size="140,40" alphatest="on" />\n\t\t<ePixmap  pixmap="~/ddbuttons/yellow.png" position="280,0" size="140,40" alphatest="on" />\n\t\t<ePixmap  pixmap="~/ddbuttons/blue.png" position="420,0" size="140,40" alphatest="on" />\n\t\t<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="list" position="0,64" size="560,240" scrollbarMode="showOnDemand" />\n\t\t<widget name="head" position="0,40" size="560,24" scrollbarMode="showNever" />\n\t\t<widget name="polhead" position="55,310" size="500,24" />\n\t\t<widget name="bandlist" position="0,334" size="55,72" />\n\t\t<widget name="infolist" position="55,334" size="845,72" />\n\t\t</screen>'

    def __init__(self, session):
        self.skin = PrestigePanelSatellitesEditor.skin
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PurePrestige")
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['SatellitesEditorActions'], {'nextPage': self.nextPage,
         'prevPage': self.prevPage,
         'displayHelp': self.showHelp,
         'displayMenu': self.openMenu,
         'displayInfo': self.showSatelliteInfo,
         'select': self.editTransponders,
         'exit': self.Exit,
         'left': self.left,
         'leftUp': self.doNothing,
         'leftRepeated': self.doNothing,
         'right': self.right,
         'rightUp': self.doNothing,
         'rightRepeated': self.doNothing,
         'upUp': self.upUp,
         'up': self.up,
         'upRepeated': self.upRepeated,
         'upUp': self.upUp,
         'down': self.down,
         'downUp': self.downUp,
         'downRepeated': self.downRepeated,
         'red': self.removeSatellite,
         'green': self.editSatellite,
         'yellow': self.sortColumn,
         'blue': self.serviceeditor}, -1)
        self.satelliteslist = self.readSatellites('/etc/tuxbox/satellites.xml')
        self['key_red'] = Button(_('remove'))
        self['key_green'] = Button(_('edit'))
        self['key_yellow'] = Button(_('sort'))
        self['key_blue'] = Button(_('service editor'))
        self['menu'] = Button(_('Add-update'))
        self['infolist'] = MenuList([])
        self['infolist'].l = eListboxPythonMultiContent()
        self['infolist'].l.setSelectionClip(eRect(0, 0, 0, 0))
        self['infolist'].l.setItemHeight(24)
        self['infolist'].l.setFont(0, gFont('Regular', 20))
        self['polhead'] = MenuList([])
        self['polhead'].l = eListboxPythonMultiContent()
        self['polhead'].l.setSelectionClip(eRect(0, 0, 0, 0))
        self['polhead'].l.setItemHeight(24)
        self['polhead'].l.setFont(0, gFont('Regular', 20))
        self['bandlist'] = MenuList([])
        self['bandlist'].l = eListboxPythonMultiContent()
        self['bandlist'].l.setSelectionClip(eRect(0, 0, 0, 0))
        self['bandlist'].l.setItemHeight(24)
        self['bandlist'].l.setFont(0, gFont('Regular', 20))
        self['head'] = Head()
        self['list'] = SatelliteList()
        self['list'].setEntries(self.satelliteslist)
        self.onLayoutFinish.append(self.layoutFinished)
        self.currentSelectedColumn = 0
        self.row = [['name', _('Satellites'), False], ['position', _('Pos'), False]]
        self.update = False

    def serviceeditor(self):
        self.session.open(PrestigePanelServicesEditor)

    def layoutFinished(self):
        try:
            row = self['list'].getCurrent()
            head = []
            for x in range(1, len(row)):
                head.append([row[x][1], row[x][3], ''])

            head[0][2] = self.row[0][1]
            head[1][2] = self.row[1][1]
            self['head'].setEntries(head)
            data = self['head'].l.getCurrentSelection()
            data = data[self.currentSelectedColumn + 1]
            self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)
            self.updateSelection()
        except:
            pass

    def updateSelection(self):
        row = self['list'].l.getCurrentSelection()
        if row is None:
            return
        else:
            firstColumn = row[1]
            lastColumn = row[len(row) - 1]
            self['list'].l.setSelectionClip(eRect(firstColumn[1], firstColumn[0], lastColumn[1] + lastColumn[3], lastColumn[4]), True)
            self.getInfo()
            return

    def doNothing(self):
        pass

    def left(self):
        print('left')
        if self.currentSelectedColumn:
            self.currentSelectedColumn -= 1
            data = self['head'].l.getCurrentSelection()
            data = data[self.currentSelectedColumn + 1]
            self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)

    def right(self):
        print('right')
        if self.currentSelectedColumn < len(self.row) - 1:
            self.currentSelectedColumn += 1
            data = self['head'].l.getCurrentSelection()
            data = data[self.currentSelectedColumn + 1]
            self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)

    def nextPage(self):
        self['list'].pageUp()
        self.lastSelectedIndex = self['list'].getSelectedIndex()
        self.updateSelection()

    def prevPage(self):
        self['list'].pageDown()
        self.lastSelectedIndex = self['list'].getSelectedIndex()
        self.updateSelection()

    def up(self):
        self['list'].up()
        self.lastSelectedIndex = self['list'].getSelectedIndex()
        self.updateSelection()

    def down(self):
        self['list'].down()
        self.lastSelectedIndex = self['list'].getSelectedIndex()
        self.updateSelection()

    def upUp(self):
        cur_idx = self['list'].getSelectedIndex()
        if self.lastSelectedIndex != cur_idx:
            self.lastSelectedIndex = cur_idx

    def downUp(self):
        cur_idx = self['list'].getSelectedIndex()
        if self.lastSelectedIndex != cur_idx:
            self.lastSelectedIndex = cur_idx

    def upRepeated(self):
        self['list'].up()
        self.updateSelection()

    def downRepeated(self):
        self['list'].down()
        self.updateSelection()

    def getInfo(self):
        print('getInfo')
        cur_idx = self['list'].getSelectedIndex()
        satellite = self.satelliteslist[cur_idx]
        self.name = satellite[0].get('name')
        self.position = satellite[0].get('position')
        self.tp_all = len(satellite[1])
        self.tp_ku = 0
        self.tp_c = 0
        self.tp_other = 0
        self.tp_ku_v = 0
        self.tp_ku_h = 0
        self.tp_ku_l = 0
        self.tp_ku_r = 0
        self.tp_ku_v2 = 0
        self.tp_ku_h2 = 0
        self.tp_ku_l2 = 0
        self.tp_ku_r2 = 0
        self.tp_c_v = 0
        self.tp_c_h = 0
        self.tp_c_l = 0
        self.tp_c_r = 0
        self.tp_c_v2 = 0
        self.tp_c_h2 = 0
        self.tp_c_l2 = 0
        self.tp_c_r2 = 0
        self.tp_ku_dvb_s = 0
        self.tp_ku_dvb_s2 = 0
        self.tp_c_dvb_s = 0
        self.tp_c_dvb_s2 = 0
        for tp in satellite[1]:
            freq = int(tp.get('frequency'))
            pol = tp.get('polarization')
            system = tp.get('system')
            if freq >= 10700000 and freq <= 12750000:
                if system == '0':
                    if pol == '0':
                        self.tp_ku_h += 1
                    elif pol == '1':
                        self.tp_ku_v += 1
                    elif pol == '2':
                        self.tp_ku_l += 1
                    elif pol == '3':
                        self.tp_ku_r += 1
                elif system == '1':
                    if pol == '0':
                        self.tp_ku_h2 += 1
                    elif pol == '1':
                        self.tp_ku_v2 += 1
                    elif pol == '2':
                        self.tp_ku_l2 += 1
                    elif pol == '3':
                        self.tp_ku_r2 += 1
            elif freq >= 3400000 and freq <= 4200000:
                if system == '0':
                    if pol == '0':
                        self.tp_c_h += 1
                    elif pol == '1':
                        self.tp_c_v += 1
                    elif pol == '2':
                        self.tp_c_l += 1
                    elif pol == '3':
                        self.tp_c_r += 1
                elif system == '1':
                    if pol == '0':
                        self.tp_c_h2 += 1
                    elif pol == '1':
                        self.tp_c_v2 += 1
                    elif pol == '2':
                        self.tp_c_l2 += 1
                    elif pol == '3':
                        self.tp_c_r2 += 1

        entryList = (_('Band'), _('Ku'), _('C'))
        l = []
        for entry in entryList:
            bandList = [None]
            bandList.append(MultiContentEntryText(pos=(0, 0), size=(80, 24), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=entry, border_width=1, border_color=15792383))
            l.append(bandList)

        self['bandlist'].l.setList(l)
        calc_xpos = lambda a: a[len(a) - 1][1] + a[len(a) - 1][3]
        entryList = (_('horizontal'),
         _('vertical'),
         _('left'),
         _('right'))
        xpos = 0
        polarisationList = [None]
        for entry in entryList:
            polarisationList.append(MultiContentEntryText(pos=(xpos, 0), size=(205, 24), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=entry, border_width=1, border_color=15792383))
            xpos = calc_xpos(polarisationList)

        self['polhead'].l.setList([polarisationList])
        l = []
        infolist = [None]
        entryList = (('dvb-s', 100),
         ('dvb-s2', 105),
         ('dvb-s', 100),
         ('dvb-s2', 105),
         ('dvb-s', 100),
         ('dvb-s2', 105),
         ('dvb-s', 100),
         ('dvb-s2', 105))
        xpos = 0
        for entry in entryList:
            infolist.append(MultiContentEntryText(pos=(xpos, 0), size=(entry[1], 50), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=entry[0], border_width=1, border_color=15792383))
            xpos = calc_xpos(infolist)

        l.append(infolist)
        infolist = [None]
        entryList = ((self.tp_ku_h, 100),
         (self.tp_ku_h2, 105),
         (self.tp_ku_v, 100),
         (self.tp_ku_v2, 105),
         (self.tp_ku_l, 100),
         (self.tp_ku_l2, 105),
         (self.tp_ku_r, 100),
         (self.tp_ku_r2, 105))
        xpos = 0
        for entry in entryList:
            infolist.append(MultiContentEntryText(pos=(xpos, 0), size=(entry[1], 50), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=str(entry[0]).lstrip('0'), border_width=1, border_color=15792383))
            xpos = calc_xpos(infolist)

        l.append(infolist)
        infolist = [None]
        entryList = ((self.tp_c_h, 100),
         (self.tp_c_h2, 105),
         (self.tp_c_v, 100),
         (self.tp_c_v2, 105),
         (self.tp_c_l, 100),
         (self.tp_c_l2, 105),
         (self.tp_c_r, 100),
         (self.tp_c_r2, 105))
        xpos = 0
        for entry in entryList:
            infolist.append(MultiContentEntryText(pos=(xpos, 0), size=(entry[1], 50), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=str(entry[0]).lstrip('0'), border_width=1, border_color=15792383))
            xpos = calc_xpos(infolist)

        l.append(infolist)
        self['infolist'].l.setList(l)
        return

    def readSatellites(self, file):
        satellitesXML = xml.etree.cElementTree.parse(file)
        satDict = satellitesXML.getroot()
        satelliteslist = []
        for sat in satDict.getiterator('sat'):
            transponderslist = []
            for transponder in sat.getiterator('transponder'):
                transponderslist.append(transponder.attrib)

            sat.attrib.update({'name': sat.attrib.get('name', 'new Satellite').encode('latin-1')})
            satelliteslist.append([sat.attrib, transponderslist])

        return satelliteslist

    def importLamedb(self):
        print('importLamedb')
        lamedb = Lamedb()
        for x in lamedb.satellitesList:
            found = False
            for y in self.satelliteslist:
                if x == y[0].get('position'):
                    found = True
                    break

            if found:
                freq = []
                for tp in y[1]:
                    freq.append(int(tp.get('frequency')) + 100000000 * int(tp.get('polarization')) + 300000000 * int(tp.get('fec_inner')))

                for tp in lamedb.satellitesList.get(x):
                    print(int(tp.get('frequency')) + 100000000 * int(tp.get('polarization')) + 300000000 * int(tp.get('fec_inner')) in freq and 'Transponder in Liste', tp)
                    continue
                    print('neuer Transponder', tp)
                    newTp = Transponder(tp).exportAll()
                    y[1].append(newTp)

            else:
                posString = str(abs(int(x) / 10)) + '.' + str(abs(int(x) % 10))
                if int(x) < 0:
                    posString += 'W'
                elif int(x) > 0:
                    posString += 'E'
                newName = 'new Satellite (%s)' % posString
                newSat = [{'name': newName,
                  'flags': '0',
                  'position': x}, []]
                for tp in lamedb.satellitesList.get(x):
                    tsid = tp.get('tsid', '-1')
                    if tsid != '-1':
                        tp.update({'tsid': str(int(tsid, 16))})
                    onid = tp.get('onid', '-1')
                    if onid != '-1':
                        tp.update({'onid': str(int(onid, 16))})
                    newTp = Transponder(tp).exportAll()
                    newSat[1].append(newTp)

                newSat[0].update({'flags': newTp.get('flags', '1')})
                self.satelliteslist.append(newSat)

        self['list'].setEntries(self.satelliteslist)

    def writeSatellites(self):
        root = xml.etree.cElementTree.Element('satellites')
        root.text = '\n\t'
        transponder = None
        satellite = None
        for x in self.satelliteslist:
            satellite = xml.etree.cElementTree.SubElement(root, 'sat', x[0])
            satellite.text = '\n\t\t'
            satellite.tail = '\n\t'
            for y in x[1]:
                y = Transponder(y).exportClean()
                transponder = xml.etree.cElementTree.SubElement(satellite, 'transponder', y)
                transponder.tail = '\n\t\t'

            if transponder is not None:
                transponder.tail = '\n\t'

        if transponder is not None:
            transponder.tail = '\n\t'
        if satellite is not None:
            satellite.tail = '\n'
        tree = xml.etree.cElementTree.ElementTree(root)
        os.rename('/etc/tuxbox/satellites.xml', '/etc/tuxbox/satellites.xml.' + str(int(time.time())))
        tree.write('/etc/tuxbox/satellites.xml')
        nimmanager.satList = []
        nimmanager.cablesList = []
        nimmanager.terrestrialsList = []
        nimmanager.readTransponders()
        return

    def finishedSatAdd2(self):
        print('finishedSatAdd')
        self.satelliteslist = self.readSatellites('/etc/tuxbox/satellites.xml')
        self['list'].setEntries(self.satelliteslist)

    def addSatelliteloader(self):
        print('addSatellite')
        if self.update == True:
            self.session.openWithCallback(self.updatesatsloader, MessageBox, _('By updating or adding satellites all changes made to satellites.xml will be lost,continue?'), MessageBox.TYPE_YESNO)
        else:
            self.session.openWithCallback(self.finishedSatAdd2, PurePrestigesettingsserver)

    def updatesatsloader(self, result):
        if result:
            self.session.openWithCallback(self.finishedSatAdd2, PurePrestigesettingsserver)

    def addSatellite(self, saturl):
        print('addSatellite')
        self.saturl = saturl
        if self.update == True:
            self.session.openWithCallback(self.updatesats, MessageBox, _('By updating or adding satellites all changes made to satellites.xml will be lost,continue?'), MessageBox.TYPE_YESNO)
        else:
            self.session.openWithCallback(self.finishedSatAdd2, satellite.NewPrestigesatEditor, saturl)

    def updatesats(self, result):
        if result:
            self.session.openWithCallback(self.finishedSatAdd2, satellite.NewPrestigesatEditor, self.saturl)

    def editTransponders(self):
        print('editTransponders')
        if not len(self.satelliteslist):
            return
        cur_idx = self['list'].getSelectedIndex()
        self.update = True
        self.session.openWithCallback(self.finishedTranspondersEdit, PrestigePanelTranspondersEditor, self.satelliteslist[cur_idx])

    def finishedTranspondersEdit(self, result):
        print('finishedTranspondersEdit')
        if result is None:
            return
        else:
            cur_idx = self['list'].getSelectedIndex()
            self.satelliteslist[cur_idx][1] = result
            self.update = True
            return

    def editSatellite(self):
        print('editSatellite')
        if not len(self.satelliteslist):
            return
        cur_idx = self['list'].getSelectedIndex()
        self.update = True
        self.session.openWithCallback(self.finishedSatEdit, PrestigePanelSatEditor, self.satelliteslist[cur_idx][0])

    def finishedSatEdit(self, result):
        print('finishedSatEdit')
        if result is None:
            return
        else:
            cur_idx = self['list'].getSelectedIndex()
            self.satelliteslist[cur_idx][0] = result
            self['list'].setEntries(self.satelliteslist)
            self.update = True
            return

    def finishedSatAdd(self, result):
        print('finishedSatAdd')
        if result is None:
            return
        else:
            self.satelliteslist.append([result])
            self['list'].setEntries(self.satelliteslist)
            self.update = True
            return

    def deleteSatellite(self):
        if len(self.satelliteslist):
            self.satelliteslist.pop(self['list'].getSelectedIndex())
            self['list'].setEntries(self.satelliteslist)
            self.update = True

    def removeSatellite(self):
        print('removeSatellite')
        self.update = True
        if len(self.satelliteslist):
            cur_idx = self['list'].getSelectedIndex()
            satellite = self.satelliteslist[cur_idx][0].get('name')
            cb_func = lambda ret: not ret or self.deleteSatellite()
            self.session.openWithCallback(cb_func, MessageBox, _('Remove Satellite %s?' % satellite), MessageBox.TYPE_YESNO)

    def compareColumn(self, a):
        if self.row[self.currentSelectedColumn][0] == 'name':
            return a[0].get('name')
        if self.row[self.currentSelectedColumn][0] == 'position':
            return int(a[0].get('position'))

    def sortColumn(self):
        rev = self.row[self.currentSelectedColumn][2]
        self.satelliteslist.sort(key=self.compareColumn, reverse=rev)
        if rev:
            self.row[self.currentSelectedColumn][2] = False
        else:
            self.row[self.currentSelectedColumn][2] = True
        self['list'].setEntries(self.satelliteslist)
        self.updateSelection()
        self.update = True

    def openMenu(self):
        self.session.openWithCallback(self.menu, PrestigePanelMenuSelection)

    def menu(self, result):
        print(result)
        if result is None:
            return
        else:
            print('menu', result)
            if result == 'Kingofsat-recommonded':
                saturl = 'http://satellites.satloader.net/satellites.xml'
                self.addSatellite(saturl)
            if result == 'Kingofsat-Feeds':
                saturl = 'http://satellites.satloader.net/feeds.xml'
                self.addSatellite(saturl)
            if result == 'Satbeams':
                saturl = 'http://satellites.satloader.net/satbeam.xml'
                self.addSatellite(saturl)
            elif result == 'Internet Settings loader':
                self.addSatelliteloader()
            elif result == 'LyngSat-All satellites':
                self.update = True
                self.session.openWithCallback(self.finishedSatImport, PrestigePanelLyngSat, 'All')
            elif result == 'LyngSat-Europe satellites':
                self.update = True
                self.session.openWithCallback(self.finishedSatImport, PrestigePanelLyngSat, 'europe.html')
            elif result == 'LyngSat-Asia satellites':
                self.update = True
                self.session.openWithCallback(self.finishedSatImport, PrestigePanelLyngSat, 'asia.html')
            elif result == 'LyngSat-Atlantic satellites':
                self.update = True
                self.session.openWithCallback(self.finishedSatImport, PrestigePanelLyngSat, 'atlantic.html')
            elif result == 'LyngSat-America satellites':
                self.update = True
                self.session.openWithCallback(self.finishedSatImport, PrestigePanelLyngSat, 'america.html')
            return

    def finishedSatImport(self, result):
        print('finishedSatImport')
        self.update = True
        if result is None:
            return
        else:
            if result is not None and len(result):
                for satelliteSrc in result:
                    posSrc = satelliteSrc[0].get('position', None)
                    print('posSrc')
                    if posSrc is not None:
                        for satelliteDst in self.satelliteslist:
                            print(satelliteDst[0].get('position', None))
                            if satelliteDst[0].get('position', None) == posSrc:
                                satelliteDst[1].extend(satelliteSrc[1])
                                if satelliteDst[0].get('name', 'new Satellite').find('new Satellite') != -1 and satelliteSrc[0].get('name', None) is not None:
                                    satelliteDst[0].update({'name': satelliteSrc[0].get('name')})
                                print('extended:', posSrc)
                                break
                            else:
                                continue
                        else:
                            self.satelliteslist.append(satelliteSrc)
                            print('appended:', posSrc)

                self['list'].setEntries(self.satelliteslist)
            return

    def Exit(self):
        if self.update == False:
            pass
        else:
            cb_func = lambda ret: not ret or self.writeSatellites()
            self.session.openWithCallback(cb_func, MessageBox, _('Save satellites.xml? \n(This take some seconds.)'), MessageBox.TYPE_YESNO)
        self.close()
        self.cleansatellitesxml()

    def cleansatellitesxml(self):
        top = '/etc/tuxbox/'
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                if 'satellites.xml.' in name:
                    os.remove(os.path.join(root, name))

    def showSatelliteInfo(self):
        print('showSatelliteInfo')
        cur_idx = self['list'].getSelectedIndex()
        self.session.openWithCallback(None, PrestigePanelSatInfo, self.satelliteslist[cur_idx])
        return

    def showHelp(self):
        print('showHelp')


def SatellitesEditorMain(session, **kwargs):
    session.open(PrestigePanelSatellitesEditor)


def SatellitesEditorStart(menuid, **kwargs):
    if menuid == 'scan':
        return [(_('TS-Satellites Editor'),
          SatellitesEditorMain,
          'TS-Satellites Editor',
          None)]
    else:
        return []
        return None


def Plugins(**kwargs):
    if nimmanager.hasNimType('DVB-S'):
        return PluginDescriptor(name=_('TS-Satellites Editor'), description='Lets you edit satellites in your Dreambox', where=PluginDescriptor.WHERE_MENU, fnc=SatellitesEditorStart)
    else:
        return []
