from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ActionMap import HelpableActionMap, ActionMap
from Components.Sources.StaticText import StaticText
from Components.config import config, ConfigSubsection, ConfigSet, ConfigSelection, NoSave, ConfigYesNo
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Sources.List import List
from enigma import eListbox
from os import path as os_path, remove
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, copyfile
from Tools.LoadPixmap import LoadPixmap
from Tools.Notifications import AddPopup
from twisted.web.client import getPage
import xml.etree.cElementTree as etree
from xml.parsers.expat import ParserCreate
from enigma import eTimer
from Components.ScrollLabel import ScrollLabel
import os

FILEURL = 'http://satellites.satloader.net/satellites.xml'
USERAGENT = 'Enima2 Satellite Editor Plugin'
SATFILE = '/etc/tuxbox/satellites.xml'
TMPFILE = '/tmp/satellites.xml'
config.plugins.sateditor = ConfigSubsection()
config.plugins.sateditor.satellites = ConfigSet(default=['192',
 '235',
 '282',
 '130'], choices=['192',
 '235',
 '282',
 '130'])
config.plugins.sateditor.sortby = ConfigSelection(default=1, choices=[(1, '1'), (2, '2'), (3, '3')])

class NewPrestigesatEditor(Screen, HelpableScreen):
    skin = '\n                \n                <screen name="NewPrestigesatEditor" position="center,center" size="640,520" title="Satellite.xml update"  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520"/>\t                \n\n                <ePixmap position="15,450" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\t<widget name="info" position="15,380" zPosition="4" size="610,60" font="Regular;22" foregroundColor="#dddddd" transparent="1" valign="top" halign="center"  />\n\t\t\n                        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/red.png" position="45,460" zPosition="0" size="140,40" transparent="1" alphatest="on" />\n\t\t\t\n\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" position="245,460" zPosition="0" size="140,40" transparent="1" alphatest="on" />\n\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/blue.png" position="445,460" zPosition="0" size="140,40" transparent="1" alphatest="on" />\n\t\t\t<widget render="Label" source="key_red" position="45,510" size="140,90" zPosition="2" valign="center" halign="center"  font="Regular;21" transparent="1" />\n\t\t\t\n\t\t\t<widget render="Label" source="key_yellow" position="245,460" size="140,40" zPosition="2" valign="center" halign="center"  font="Regular;21" transparent="1" />\n\t\t\t<widget render="Label" source="key_blue" position="445,460" size="140,40" zPosition="2" valign="center" halign="center"  font="Regular;21" transparent="1"  />\n\t\t\t<widget source="satlist" render="Listbox" position="15,20" size="610,350" scrollbarMode="showOnDemand" transparent="1" zPosition="2" >\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (50, 0), size = (460, 26), font=0, flags = RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos = (5, 0), size = (25, 24), png = 2),\n\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 22)],\n\t\t\t\t\t"itemHeight": 25\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t</screen>'

    def __init__(self, session, saturl):
        self.session = session
        Screen.__init__(self, session)
        self['info'] = Label()
        self.saturl = saturl
        self['key_red'] = StaticText(_('Exit'))
        self['key_yellow'] = StaticText(_('Download'))
        self['key_blue'] = StaticText('')
        self.satList = []
        self['satlist'] = List(self.satList)
        HelpableScreen.__init__(self)
        self['OkCancelActions'] = HelpableActionMap(self, 'OkCancelActions', {'cancel': (self.exit, _('Exit plugin')),
         'ok': (self.changeSelection, _('Select/deselect satellite'))}, -1)
        self['ColorActions'] = HelpableActionMap(self, 'ColorActions', {'red': (self.exit, _('Exit plugin')),
         'yellow': (self.downloadSattelitesFile, _('Download satellites.xml file')),
         'blue': (self.purgeSattelitesFile, _('Purge satellites.xml file'))}, -1)
        self['ChannelSelectBaseActions'] = HelpableActionMap(self, 'ChannelSelectBaseActions', {'nextBouquet': (self.changeSortingUp, _('Sorting up')),
         'prevBouquet': (self.changeSortingDown, _('Sorting down'))}, -1)
        self.showAccept = False
        self.useTmpFile = False
        self.purgePossible = False
        self.downloadPossible = True
        self.xmlVersion = ''
        self.xmlEncoding = ''
        self.xmlComment = ''
        self['info'].setText('Downloading satellite.xml file..please wait')
        self.onShown.append(self.downloadSattelitesFile)

    def exit(self):
        print '[PrestigesatEditor] closing'
        if os_path.exists(TMPFILE):
            try:
                remove(TMPFILE)
            except OSError as error:
                print '[PrestigesatEditor] unable to delete temp file', TMPFILE
                AddPopup(text=_('Unable to delete temp file.\n%s') % error, type=MessageBox.TYPE_ERROR, timeout=0, id='RemoveFileError')

        self.close()

    def accept(self):
        print '[PrestigesatEditor] copying temp satellite file to target'
        if os_path.exists(TMPFILE):
            try:
                copyfile(TMPFILE, SATFILE)
            except OSError as error:
                print '[PrestigesatEditor] error during copying of', TMPFILE
                self.session.open(MessageBox, _('Unable to copy temp file.\n%s') % error, type=MessageBox.TYPE_ERROR)

        self.showAccept = False
        self['info'].setText('Satellite.xml saved')
        self.exit()

    def changeSortingUp(self):
        if config.plugins.sateditor.sortby.value == 1:
            config.plugins.sateditor.sortby.value = 3
        else:
            config.plugins.sateditor.sortby.value -= 1
        self.setListSorted()

    def changeSortingDown(self):
        if config.plugins.sateditor.sortby.value == 3:
            config.plugins.sateditor.sortby.value = 1
        else:
            config.plugins.sateditor.sortby.value += 1
        self.setListSorted()

    def loadSattelitesFile(self, fileName = SATFILE):
        print '[PrestigesatEditor] loading satellite file', fileName
        self.satList = []
        try:
            satFile = open(fileName, 'r')
        except IOError as error:
            print '[PrestigesatEditor] unable to open', fileName
            satFile = None
            AddPopup(text=_('Unable to open file.\n%s') % error, type=MessageBox.TYPE_ERROR, timeout=0, id='OpenFileError')
            self.exit()

        if not satFile:
            return
        else:
            satellites = config.plugins.sateditor.satellites.value
            curroot = etree.parse(satFile)
            for sat in curroot.findall('sat'):
                position = sat.attrib.get('position')
                name = sat.attrib.get('name')
                if position in satellites:
                    png = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, '/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/lock_on.png'))
                    self.satList.append((position, name.encode('utf-8'), png))
                else:
                    self.satList.append((position, name.encode('utf-8'), None))

            satFile.close()
            self['satlist'].setList(self.satList)
            self.setListSorted()
            return

    def setListSorted(self):
        if config.plugins.sateditor.sortby.value == 1:
            s = sorted(self.satList, lambda x, y: cmp(x[1], y[1]), reverse=False)
            self.satList = sorted(s, lambda x, y: cmp(x[2], y[2]), reverse=True)
        elif config.plugins.sateditor.sortby.value == 2:
            s = sorted(self.satList, lambda x, y: cmp(int(x[0]), int(y[0])), reverse=False)
            self.satList = sorted(s, lambda x, y: cmp(x[2], y[2]), reverse=True)
        else:
            s = sorted(self.satList, lambda x, y: cmp(int(x[0]), int(y[0])), reverse=True)
            self.satList = sorted(s, lambda x, y: cmp(x[2], y[2]), reverse=True)
        self['satlist'].updateList(self.satList)
        if len(self.satList) > len(config.plugins.sateditor.satellites.value):
            self['key_blue'].setText(_('Save'))
            self.purgePossible = True
        else:
            self['key_blue'].setText('')
            self.purgePossible = False

    def changeSelection(self):
        try:
            png = None
            idx = self['satlist'].getIndex()
            position = self.satList[idx][0]
            name = self.satList[idx][1]
            if position in config.plugins.sateditor.satellites.value:
                config.plugins.sateditor.satellites.value.remove(position)
            else:
                config.plugins.sateditor.satellites.value.append(position)
                png = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, '/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/lock_on.png'))
            config.plugins.sateditor.satellites.save()
            self.satList[idx] = (position, name, png)
            self.setListSorted()
        except:
            pass

        return

    def downloadSattelitesFile(self):
        if not self.downloadPossible:
            return
        print '[PrestigesatEditor] downloading satellite file'
        self['info'].setText('Downloading satellite.xml...please wait')
        self.timer = eTimer()
        self.timer.callback.append(self.startdownload)
        self.timer.start(100, 1)

    def startdownload(self):
        getPage(self.saturl, agent=USERAGENT, timeout=20).addCallback(self.cbDownload).addErrback(self.cbDownloadError)

    def commentHandler(self, data):
        self.xmlComment = data

    def declarationHandler(self, version, encoding, standalone):
        self.xmlVersion = version
        self.xmlEncoding = encoding

    def getXmlInfo(self):
        print '[PrestigesatEditor] trying to get the XML declaration and comment'
        parser = ParserCreate()
        parser.XmlDeclHandler = self.declarationHandler
        parser.CommentHandler = self.commentHandler
        satFile = open(TMPFILE, 'r')
        parser.ParseFile(satFile)
        satFile.close()

    def cbDownload(self, data):
        print '[PrestigesatEditor] saving download to temp satellite file'
        try:
            tmpFile = open(TMPFILE, 'w')
            tmpFile.write(data)
            tmpFile.close()
        except IOError as error:
            print '[PrestigesatEditor] unable to save download to temp satellite file'
            self.session.open(MessageBox, _('Unable to save download to temp satellite file.\n'), MessageBox.TYPE_ERROR)
            return

        self.getXmlInfo()
        self.loadSattelitesFile(TMPFILE)
        self.useTmpFile = True
        self.showAccept = True
        self.downloadPossible = False
        self['key_yellow'].setText('')
        self['info'].setText('To edit satellite.xml,select satellites to be included,then Save')

    def cbDownloadError(self, error):
        if error is not None:
            print '[PrestigesatEditor] error downloading satellite file:', str(error.getErrorMessage())
            self.session.open(MessageBox, _('Unable to download satellite file. Please try again later.\n%s') % str(error.getErrorMessage()), MessageBox.TYPE_ERROR)
            self['info'].setText('To edit satellite.xml,select satellites to be included,then save')
        return

    def purgeSattelitesFile(self):
        if not self.purgePossible:
            return
        print '[PrestigesatEditor] purging temp satellite file'
        self['info'].setText('Saving satellite.xml..please wait')
        if self.useTmpFile:
            satFile = TMPFILE
        else:
            satFile = SATFILE
        savesatellite(satFile, self.xmlVersion, self.xmlEncoding, self.xmlComment)
        self.postPurge()

    def postPurge(self):
        self.loadSattelitesFile(TMPFILE)
        self.downloadPossible = True
        self['info'].setText('To edit satellite.xml,select satellites to be included,then save')
        self['key_yellow'].setText(_('Download'))
        self.showAccept = True
        self.accept()


class savesatellite:

    def __init__(self, satFile, xmlVersion, xmlEncoding, xmlComment):
        self.satFile = satFile
        self.xmlVersion = xmlVersion
        self.xmlEncoding = xmlEncoding
        self.xmlComment = xmlComment
        self.purge()

    def run(self):
        self.purge()

    def stop(self):
        pass

    def purge(self):
        satellites = config.plugins.sateditor.satellites.value
        newRoot = etree.Element('satellites')
        satFile = open(self.satFile, 'r')
        curroot = etree.parse(satFile)
        satFile.close()
        for sat in curroot.findall('sat'):
            position = sat.attrib.get('position')
            if position in satellites:
                newRoot.append(sat)

        header = ''
        if self.satFile == TMPFILE:
            if self.xmlVersion and self.xmlEncoding:
                header = '<?xml version="%s" encoding="%s"?>\n' % (self.xmlVersion, self.xmlEncoding)
            if self.xmlComment:
                modified = '\n     THIS FILE WAS MODIFIED BY THE ENIGMA2 PLUGIN SATELLITE EDITOR!\n'
                header += '<!-- %s%s-->\n' % (self.xmlComment, modified)
            if header:
                tmpFile = open(TMPFILE, 'w')
                tmpFile.writelines(header)
                tmpFile.close()
        if header:
            tmpFile = open(TMPFILE, 'a')
        else:
            tmpFile = open(TMPFILE, 'w')
        xmlString = etree.tostring(newRoot)
        tmpFile.writelines(xmlString)
        tmpFile.close()
