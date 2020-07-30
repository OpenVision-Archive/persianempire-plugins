#!/usr/bin/python
# -*- coding: utf-8 -*-
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from enigma import eListboxPythonMultiContent, eServiceCenter, gFont, eServiceReference, iServiceInformation, RT_HALIGN_RIGHT, RT_HALIGN_LEFT, RT_HALIGN_CENTER, eTimer, getBoxType, getImageVersionString
from ServiceReference import ServiceReference
from Screens.InfoBarGenerics import *
from Screens.InfoBar import InfoBar
from Components.Pixmap import Pixmap, MovingPixmap
from Tools.LoadPixmap import LoadPixmap
import calendar, keymapparser
from Components.Harddisk import harddiskmanager
from RecordTimer import AFTEREVENT
from Screens.ChoiceBox import ChoiceBox
from Screens.TimerEdit import TimerEditList
from Screens.NetworkSetup import NetworkAdapterSelection
from Screens.RecordPaths import RecordPathsSettings
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Tools.FuzzyDate import FuzzyTime
import NavigationInstance
from Components.config import config
import os
from os import path as os_path, unlink, environ
import string
from time import time
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, SCOPE_SKIN
from Components.Language import language
import gettext
import sys
from Components.About import *
from Components.NimManager import nimmanager
from Screens.Menu import MainMenu
import xml.etree.cElementTree
from xml.etree.cElementTree import parse
from Components.PluginComponent import plugins
from Tools.Transponder import ConvertToHumanReadable
from Components.Network import iNetwork
import urllib2
from Components.Console import Console

lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('PEInfo', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/PEInfo/locale/'))
lenguaje = str(lang[:2])

def _(txt):
    t = gettext.dgettext('PEInfo', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t

filename = ''
carpetaimg = resolveFilename(SCOPE_PLUGINS, 'Extensions/PEInfo/icons/')
nommodelo = 'NA'
listamenu = []
listamenu.append((_('Record'), _('Recording Information'), 1))
listamenu.append((_('Tuning'), _('Information About Current Channel'), 2))
listamenu.append((_('Storage'), _('Devices Information'), 6))
listamenu.append((_('Memory'), _('Memory Table'), 7))
listamenu.append((_('Network'), _('Network Information'), 5))
listamenu.append((_('Hardware'), _('CPU - Model Information'), 3))
listamenu.append((_('Display'), _('AV Settings - Skin Information'), 9))
listamenu.append((_('OS'), _('Operating System Information'), 4))
listamenu.append((_('Process'), _('Current Running Processes'), 8))
listamenu.append((_('About'), _('About PE Info'), 10))

def ImageVersionString():
	return getImageVersionString()


def ponPorcen(valor):
    ret = '|'
    for i in range(0, 10):
        if i < valor / 10:
            ret = ret + '_'
        else:
            ret = ret + '  '

    ret = ret + '| ' + str(valor) + '%'
    return ret


def KernelVersionString():
    return getKernelVersionString()


def inforecord():
    global filename
    ret = []
    filename = ''
    for timer in NavigationInstance.instance.RecordTimer.timer_list:
        if timer.state == timer.StateRunning:
            nombre = str(timer.name) + ''
            if len(nombre) < 2:
                nombre = os.path.split(timer.Filename)[1]
            archivo = str(timer.Filename)
            filename = str(timer.Filename)
            inicio = str(FuzzyTime(timer.begin)[1])
            fin = str(FuzzyTime(timer.end)[1])
            duracion = str((timer.end - timer.begin) / 60) + ' ' + _('mins')
            nfaltan = (timer.end - time()) / 60
            cvan = str((time() - timer.begin) / 60)
            if nfaltan >= 1:
                faltan = str(int(nfaltan)) + ' ' + _('mins')
            else:
                faltan = str(int(nfaltan * 60)) + ' ' + _('secs')
            nomcan = timer.service_ref.getServiceName()
            now = int(time())
            start_time = timer.begin
            duration = timer.end - timer.begin
            valor = int((int(time()) - timer.begin) * 100 / duration)
            pos = valor
            nlen = 100
            valor = pos * 100 / nlen
            ret.append((nombre,
             nomcan,
             inicio,
             fin,
             duracion,
             faltan,
             cvan,
             valor,
             archivo))

    return ret


def grabando(selfse):
    recordings = len(selfse.session.nav.getRecordings())
    if recordings > 0:
        return True
    else:
        return False


class IniciaSelListLista(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(29)
        self.l.setFont(0, gFont('Regular', 18))
        self.l.setFont(1, gFont('Regular', 16))


def IniciaSelListEntryLista(texto1):
    res = [texto1]
    res.append(MultiContentEntryText(pos=(5, 1), size=(1000, 33), font=0, text=texto1))
    return res


class IniciaSelListInfo(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(100)
        self.l.setFont(0, gFont('Regular', 18))
        self.l.setFont(1, gFont('Regular', 16))


def IniciaSelListEntryInfo(texto1, texto2 = None, texto3 = None, texto4 = None, texto5 = None, imagen1 = None, progreso = None, ruta = None):
    global carpetaimg
    if ruta == None:
        res = [texto1]
    else:
        res = [ruta]
    res.append(MultiContentEntryText(pos=(59, 16), size=(1000, 33), font=0, text=texto1))
    if not texto2 == None:
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         0,
         43,
         744,
         22,
         0,
         RT_HALIGN_CENTER,
         texto2))
    if not texto3 == None:
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         0,
         60,
         216,
         30,
         0,
         RT_HALIGN_RIGHT,
         texto3))
    if not texto4 == None:
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         528,
         60,
         318,
         30,
         0,
         RT_HALIGN_LEFT,
         texto4))
    if not texto5 == None:
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         0,
         76,
         744,
         25,
         0,
         RT_HALIGN_CENTER,
         texto5))
    if not imagen1 == None:
        imagen = 'list' + str(imagen1) + '.png'
        png = '' + carpetaimg + '' + imagen + ''
        if fileExists(png):
            fpng = LoadPixmap(png)
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
             1,
             1,
             48,
             48,
             fpng))
    if not progreso == None:
        imagen = 'infoprogreso0.png'
        png = '' + carpetaimg + '' + imagen + ''
        if fileExists(png):
            fpng = LoadPixmap(png)
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
             223,
             66,
             300,
             13,
             fpng))
        imagen = 'infoprogreso1.png'
        if progreso > 35 and not imagen1 == 5:
            imagen = 'infoprogreso2.png'
        if progreso > 60 and not imagen1 == 5:
            imagen = 'infoprogreso3.png'
        if progreso > 80 or imagen1 == 5:
            imagen = 'infoprogreso4.png'
        png = '' + carpetaimg + '' + imagen + ''
        if fileExists(png):
            fpng = LoadPixmap(png)
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
             223,
             66,
             progreso * 3,
             13,
             fpng))
    return res


class IniciaSelList(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(50)
        self.l.setFont(0, gFont('Regular', 21))
        self.l.setFont(1, gFont('Regular', 17))


def IniciaSelListEntry(texto, info, numero):
    res = [texto]
    res.append(MultiContentEntryText(pos=(54, 14), size=(1000, 30), font=0, text=texto))
    imagen = 'info' + str(numero) + '.png'
    png = '' + carpetaimg + '' + imagen + ''
    if fileExists(png):
        fpng = LoadPixmap(png)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
         1,
         1,
         48,
         48,
         fpng))
    return res


def cargalista(valor, sigrabando = False):
    global listamenu
    templista = []
    indice = -1
    for i in range(0, len(listamenu)):
        eltexto = '' + listamenu[i][0]
        lainfo = '' + listamenu[i][1]
        elnumero = listamenu[i][2]
        if elnumero == valor:
            indice = i
        if elnumero == 1 and sigrabando:
            elnumero = 99
        templista.append(IniciaSelListEntry(eltexto, lainfo, elnumero))

    return [indice, templista]


def Humanizer(size, mostrarbytes = False):
    if size < 1024:
        humansize = str(size) + ' bytes'
    elif size < 1048576:
        humansize = '%.2f Kb' % (float(size) / 1024)
        if mostrarbytes:
            humansize = humansize + ' (' + str(size) + ' bytes)'
    elif size < 1073741824:
        humansize = '%.2f Mb' % (float(size) / 1048576)
        if mostrarbytes:
            humansize = humansize + ' (' + str(size) + ' bytes)'
    else:
        humansize = '%.2f Gb' % (float(size) / 1073741824)
        if mostrarbytes:
            humansize = humansize + ' (' + str(size) + ' bytes)'
    return humansize


def normalizatam(cualo):
    valor = 0
    if 'M' in cualo:
        valor = float(cualo.replace('M', ''))
    if 'K' in cualo:
        valor = float(cualo.replace('K', '')) / 1024
    if 'G' in cualo:
        valor = float(cualo.replace('G', '')) * 1024
    if 'T' in cualo:
        valor = float(cualo.replace('T', '')) * 1024 * 1024
    return valor


def cargaosinfo(orden, nulo = False):
    ret = ''
    Console().ePopen('%s >/tmp/tempinfo' % orden)
    booklist = None
    if fileExists('/tmp/tempinfo'):
        try:
            booklist = open('/tmp/tempinfo', 'r')
        except:
            pass

        if booklist is not None:
            for oneline in booklist:
                ret = ret + oneline

            booklist.close()
        Console().ePopen('rm -f /tmp/tempinfo')
    if len(ret) <= 1:
        if nulo == True:
            ret = ''
        else:
            ret = _('No Info Avaiable')
    return ret

class PEInfoTexto(Screen):
    skin = '\n\t<screen position="center,center" size="1050,602" title="%s">\n\n\t<widget name="lista" position="0,0" size="250,602" scrollbarMode="showOnDemand" zPosition="12" transparent="1" />\n\t<widget name="textoinfo" position="288,37" size="745,522" valign="top" halign="left" text="%s" font="Regular; 18" zPosition="1" />\n\t<widget name="listainfo" position="288,37" size="745,522" zPosition="1" scrollbarMode="showOnDemand" transparent="1"/>\n\t<widget name="listaproc" position="288,37" size="745,522" zPosition="1" scrollbarMode="showOnDemand" transparent="1"/>\n\n\t<widget name="key_pup" position="295,568" size="220,25" valign="center" halign="left" zPosition="4" font="Regular;17" transparent="1" /> \n\t<widget name="img_pup" position="260,567" zPosition="2" size="35,25" pixmap="~/icons/pup.png" transparent="1" alphatest="on" />\n\n\t<widget name="key_pdown" position="435,568" size="220,25" valign="center" halign="left" zPosition="4" font="Regular;17" transparent="1" /> \n\t<widget name="img_pdown" position="400,567" zPosition="2" size="35,25" pixmap="~/icons/pdown.png" transparent="1" alphatest="on" />\t\n\t\n\t<widget name="key_red" position="548,567" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1" /> \n\t<widget name="key_green" position="674,567" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1" />  \n\t<widget name="key_yellow" position="801,567" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1" /> \n\t<widget name="key_blue" position="928,567" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1" /> \n\n\t\n\t<widget name="img_red" position="548,572" zPosition="2" size="130,40" pixmap="~/icons/red.png" transparent="1" alphatest="on" />\n\t<widget name="img_green" position="674,572" zPosition="2" size="130,40" pixmap="~/icons/green.png" transparent="1" alphatest="on" />\n\t\n\t<widget name="img_yellow" position="801,572" zPosition="2" size="130,40" pixmap="~/icons/yellow.png" transparent="1" alphatest="on" />\n\t<widget name="img_blue" position="928,572" zPosition="2" size="130,40" pixmap="~/icons/blue.png" transparent="1" alphatest="on" />\n\t<widget name="titulo" position="288,0" size="746,28" text=" " transparent="1" halign="center" font="Regular; 22" zPosition="1" />\n\t<ePixmap name="fondo" position="0, 0" size="1050, 602" pixmap="~/icons/peinfo.png" transparent="1" alphatest="blend"/>\n\t\t\t\n\t</screen>' % (_('PE') + ' ' + 'Information', _('Please Wait'))

    def __init__(self, session, inicio = 2, **kwargs):
        self.session = session
        Screen.__init__(self, session)
	self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PEInfo")
        self.inicio = inicio
        self.iniciado = False
        self['lista'] = IniciaSelList([])
        self.TimerTemp = eTimer()
        self.TimerCarga = eTimer()
        self.tarea = ''
        self.TimerActualizar = eTimer()
        self.TimerActualizar.callback.append(self.buildList)
        self.indice = 0
        self.bloquear = False
        self.satNames = {}
        self.readSatXml()
        self.tv_list = []
        self.radio_list = []
        self.upagina = False
        self.TimerTemp.callback.append(self.cargar)
        self.TimerCarga.callback.append(self.key_ok)
        self.actualizar = False
        self['textoinfo'] = ScrollLabel(_(''))
        self['listaproc'] = IniciaSelListLista([])
        self['listainfo'] = IniciaSelListInfo([])
        self.listarec = []
        self.tmrecord = None
        self['titulo'] = Label(' ')
        self['key_red'] = Label(_(''))
        self['key_green'] = Label('')
        self['key_blue'] = Label(_(''))
        self['key_yellow'] = Label('')
        self['key_pup'] = Label('')
        self['key_pdown'] = Label('')
        service = session.nav.getCurrentService()
        if service is not None:
            self.info = service.info()
            self.feinfo = service.frontendInfo()
        else:
            self.info = None
            self.feinfo = None
        self['img_red'] = MovingPixmap()
        self['img_green'] = MovingPixmap()
        self['img_yellow'] = MovingPixmap()
        self['img_blue'] = MovingPixmap()
        self['img_pup'] = MovingPixmap()
        self['img_pdown'] = MovingPixmap()
        self['setupActions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'green': self.acc_green,
         'red': self.acc_red,
         'yellow': self.acc_yellow,
         'blue': self.acc_blue,
         'back': self.exit,
         'left': self.key_left,
         'right': self.key_right,
         'up': self.key_up,
         'down': self.key_down,
         'info': self.key_info,
         'ok': self.key_re}, -2)
        self.onLayoutFinish.append(self.buildList)
        self.onShow.append(self.cargaacciones)
        return

    def cargar(self):
        self['textoinfo'].setText('\n' + _('Please Wait'))
        self['titulo'].setText(' ')
        self['listainfo'].hide()
        self['listaproc'].hide()
        self['key_red'].hide()
        self['img_red'].hide()
        self['key_blue'].hide()
        self['img_blue'].hide()
        self['key_green'].hide()
        self['img_green'].hide()
        self['key_yellow'].hide()
        self['img_yellow'].hide()
        if self.tarea == 'dmesg':
            self.tarea = ''
        self.TimerCarga.start(200, True)

    def cargaacciones(self):
        self['key_red'].hide()
        self['img_red'].hide()
        self['key_blue'].hide()
        self['img_blue'].hide()
        self['key_green'].hide()
        self['img_green'].hide()
        self['key_yellow'].hide()
        self['img_yellow'].hide()
        self.muestra('pup', 'Page Up')
        self.muestra('pdown', 'Page Down')
        if self.inicio == 6:
            if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/PEPanel/HddSetup.pyo')):
                self.muestra('green', 'Manage')
            self.muestra('blue', 'Setup')
            self.muestra('yellow', 'Explorer')
        elif self.inicio == 2:
            self.muestra('green', 'Event')
            self.muestra('yellow', 'EPG')
        elif self.inicio == 11:
            if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/PersianPalace/plugin.pyo')):
                self.muestra('green', 'Persian Palace')
            if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/DownloadManager/plugin.pyo')):
                self.muestra('blue', 'DM 5.0')
        elif self.inicio == 5:
            self.muestra('blue', 'Setup')
            self.muestra('yellow', 'Refresh')
        elif self.inicio == 4:
            self.muestra('blue', 'Restart')
            self.muestra('yellow', 'Restart enigma')
            self.muestra('green', 'Backup')
        elif self.inicio == 9:
            self.muestra('blue', 'Setup')
            self.muestra('yellow', 'Skins')
        elif self.inicio == 8:
            self.muestra('red', 'CrashLogs')
            self.muestra('blue', 'Kernel')
            self.muestra('yellow', 'Save To File')
        elif self.inicio == 1:
			self.muestra('green', 'Add Recording')
			self.muestra('yellow', 'Movies')
			self.muestra('blue', 'Paths')

    def detengrab(self):
        self.listarec = []
        self.tmrecord = None
        for timer in NavigationInstance.instance.RecordTimer.timer_list:
            if timer.state == timer.StateRunning:
                self.listarec.append(timer)
                self.tmrecord = timer

        if len(self.listarec) > 1:
            self.seleGrab()
            return
        else:
            if not self.tmrecord == None:
                self.session.openWithCallback(self.stopRecordConfirmation, MessageBox, _('Stop Current Recording ?') + ':\n' + str(self.tmrecord.name), MessageBox.TYPE_YESNO)
            return

    def cbseleGrab(self, answer):
        answer = answer and answer[1]
        if not answer:
            return
        else:
            sel = int(answer)
            self.tmrecord = self.listarec[sel]
            if not self.tmrecord == None:
                self.session.openWithCallback(self.stopRecordConfirmation, MessageBox, _('Stop Current Recording ?') + ':\n' + str(self.tmrecord.name), MessageBox.TYPE_YESNO)
            return

    def seleGrab(self):
        list = []
        nkeys = []
        conta = 0
        for elerec in self.listarec:
            nombre = elerec.name
            if len(nombre) > 17:
                nombre = nombre[:15] + '...'
            nombre = nombre + ' (' + str(FuzzyTime(elerec.begin)[1])
            nombre = nombre + ' - ' + str(FuzzyTime(elerec.end)[1])
            nombre = nombre + ') ' + elerec.service_ref.getServiceName()
            list.append((nombre + ' ', str(conta)))
            nkeys.append(str(conta + 1))
            if conta < 9:
                conta = conta + 1

        if len(list) > 0:
            self.session.openWithCallback(self.cbseleGrab, ChoiceBox, keys=nkeys, title=_('Select A Record To Stop'), list=list)

    def cbborralogs(self, answer):
        if answer:
            rutacras1 = '/media/hdd/*.log'
            rutacras2 = '/media/usb/*.log'
            rutacras3 = '/media/cf/*.log'
            Console().ePopen('rm -rf %s' % rutacras1)
            Console().ePopen('rm -rf %s' % rutacras2)
            Console().ePopen('rm -rf %s' % rutacras3)
            cmens = _('These CrashLogs') + ' :\n' + rutacras1 + '\n' + rutacras2 + '\n' + rutacras3 + '\n' + _('Have Been Deleted !')
            dei = self.session.open(MessageBox, cmens, MessageBox.TYPE_INFO)
            dei.setTitle(_('Delete CrashLogs'))

    def acc_red(self):
        if self.inicio == 1 and grabando(self):
            self.detengrab()
        elif self.inicio == 8:
            rutacras1 = '/media/hdd/*.log'
            rutacras2 = '/media/usb/*.log'
            rutacras3 = '/media/cf/*.log'
            cmens = _('Delete CrashLogs') + ' :\n' + rutacras1 + '\n' + rutacras2 + '\n' + rutacras3 + '\n' + _('Are You Sure To Delete .log Files ?')
            dei = self.session.openWithCallback(self.cbborralogs, MessageBox, cmens, MessageBox.TYPE_YESNO)
        elif self.inicio == 11:
            if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/PersianPalace/plugin.pyo')):
                try:
                    from Plugins.Extensions.PersianPalace.plugin import *
                    persianpalaceplugin(self.session)
                except:
                    pass

        elif self.inicio == 55:
            xmdom = xml.etree.cElementTree.parse(resolveFilename(SCOPE_SKIN, 'menu.xml'))
            root = xmdom.getroot()
            ret = ''
            for x in root.findall('menu'):
                y = x.find('id')
                if y is not None:
                    id = y.get('val')
                    if id and id == 'setup':
                        for j in x:
                            for h in j:
                                ret = ret + str(h) + '\n'
                                mo = h.get('module')
                                sc = h.get('screen')
                                if mo:
                                    ret = ret + mo + ' :: '
                                if sc:
                                    ret = ret + sc
                                ret = ret + '\n'
                                try:
                                    ret = ret + str(h.nodeValue) + '\n'
                                except:
                                    pass

            self['textoinfo'].setText(ret)
        return

    def acc_green(self):
        if self.inicio == 1:
            try:
                self.session.open(TimerEditList)
            except:
                pass

        elif self.inicio == 2:
            if InfoBar and InfoBar.instance:
                InfoBar.openEventView(InfoBar.instance)
        elif self.inicio == 4:
            try:
                from Plugins.Extensions.AutoBackup.plugin import *
                main(self.session)
            except:
                pass

        elif self.inicio == 11:
            try:
                from Plugins.Extensions.PersianPalace.plugin import *
                persianpalaceplugin(self.session)
            except:
                pass

        elif self.inicio == 6:
            try:
                from Plugins.SystemPlugins.PEPanel.HddSetup import *
                self.session.open(HddSetup)
            except:
                pass

    def acc_yellow(self):
        if self.inicio == 2:
            try:
                if InfoBar and InfoBar.instance:
                    servicelist = InfoBar.instance.servicelist
                from Plugins.Extensions.GraphMultiEPG.plugin import *
                main(self.session, servicelist)
            except:
                pass

        elif self.inicio == 4:
            laref = _('Restart GUI ?')
            dei = self.session.openWithCallback(self.reiniciargui, MessageBox, laref, MessageBox.TYPE_YESNO)
        elif self.inicio == 9:
            try:
                from Plugins.SystemPlugins.SkinSelector.plugin import SkinSelMain
                SkinSelMain(self.session)
            except:
                pass

        elif self.inicio == 1:
			if InfoBar and InfoBar.instance:
				cerrar = False
				InfoBar.showMovies(InfoBar.instance)
        elif self.inicio == 5:
            self.tarea = 'ping'
            self.buildList()
        elif self.inicio == 8:
            self.TimerActualizar.stop()
            lalista = self['listaproc'].list
            cadena = 'PE Info Log\n' + cargaosinfo('date').replace('\n', '') + '\n'
            try:
                newbooklist = open('/tmp/PEInfo.log', 'w')
            except:
                dei = self.session.open(MessageBox, _('Error !'), MessageBox.TYPE_ERROR)
                dei.setTitle(_('PEInfo'))

            if newbooklist is not None:
                newbooklist.write(cadena)
                for i in lalista:
                    newbooklist.write(str(i[0]) + '')

                newbooklist.close()
            info1 = _('Log File Saved To') + ' :\n'
            info2 = '/tmp/PEInfo.log'
            cmens = info1 + '\n' + info2
            dei = self.session.open(MessageBox, cmens, MessageBox.TYPE_INFO)
            dei.setTitle(_('Save to file'))
            self.TimerActualizar.start(15000, True)
        elif self.inicio == 6:
            lalista = self['listainfo'].list
            idx = self['listainfo'].getSelectionIndex()
            ruta = str(lalista[idx][0])
            try:
                from Plugins.Extensions.DreamExplorer.plugin import *
                main(self.session)
            except:
                pass
        return

    def acc_blue(self):
        if self.inicio == 6:
            self.ejecutaMenu2('harddisk')
        elif self.inicio == 11:
            try:
                from Plugins.Extensions.DownloadManager.plugin import *
                main(self.session)
            except:
                pass

        elif self.inicio == 8:
            self.tarea = 'dmesg'
            self.buildList()
        elif self.inicio == 4:
            laref = _('Reboot ?')
            dei = self.session.openWithCallback(self.reiniciar, MessageBox, laref, MessageBox.TYPE_YESNO)
        elif self.inicio == 9:
            try:
                from Plugins.SystemPlugins.Videomode.plugin import videoSetupMain
                videoSetupMain(self.session)
            except:
                pass

        elif self.inicio == 5:
            try:
                self.session.open(NetworkAdapterSelection)
            except:
                pass

        elif self.inicio == 1:
            try:
                self.session.open(RecordPathsSettings)
            except:
                pass

    def ccamscript(self, answer):
        answer = answer and answer[1]
        if answer:
            if answer == 'Persian Palace':
                try:
                    from Plugins.Extensions.PersianPalace.plugin import *
                    persianpalaceplugin(self.session)
                except:
                    pass

            else:
                self.tarea = answer
                self.cargar()

    def ejecutaMenu2(self, nombreid):
        ret = '\n\n\n\n\n\n\n**** ' + nombreid + '***\n'
        xmdom = xml.etree.cElementTree.parse(resolveFilename(SCOPE_SKIN, 'menu.xml'))
        root = xmdom.getroot()
        for x in root.findall('menu'):
            y = x.find('id')
            if y is not None:
                id = y.get('val')
                ret = ret + str(id) + '\n'
                if id and id == 'setup':
                    for j in x.findall('menu'):
                        m = j.find('id')
                        if m is not None:
                            id2 = m.get('val')
                            ret = ret + str(id2) + '\n'
                            if id2 and id2 == 'system':
                                for j2 in j.findall('menu'):
                                    m2 = j2.find('id')
                                    if m2 is not None:
                                        id3 = m2.get('val')
                                        ret = ret + str(id3) + '\n'
                                        if id3 and id3 == nombreid:
                                            self.session.infobar = self
                                            menu_screen = self.session.openWithCallback(self.MenuClosed, MainMenu, j2)
                                            menu_screen.setTitle(_('Setup'))

        return

    def ejecutaMenu(self, nombreid):
        xmdom = xml.etree.cElementTree.parse(resolveFilename(SCOPE_SKIN, 'menu.xml'))
        root = xmdom.getroot()
        for x in root.findall('menu'):
            y = x.find('id')
            if y is not None:
                id = y.get('val')
                if id and id == 'setup':
                    for j in x.findall('menu'):
                        m = j.find('id')
                        if m is not None:
                            id2 = m.get('val')
                            if id2 and id2 == nombreid:
                                self.session.infobar = self
                                menu_screen = self.session.openWithCallback(self.MenuClosed, MainMenu, j)
                                menu_screen.setTitle(_('Setup'))

        return

    def reiniciar(self, respuesta):
        if respuesta:
            self.session.open(TryQuitMainloop, 2)

    def MenuClosed(self, dummy):
        pass

    def reiniciargui(self, respuesta):
        if respuesta:
            self.session.open(TryQuitMainloop, 3)

    def ejecutaPlugin(self, nombre):
        for plugin in plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU,
         PluginDescriptor.WHERE_MENU,
         PluginDescriptor.WHERE_EXTENSIONSMENU,
         PluginDescriptor.WHERE_EVENTINFO]):
            if plugin.name == _(nombre):
                plugin(session=self.session)
                break

    def stopRecordConfirmation(self, confirmed):
        if not confirmed:
            return
        elif self.tmrecord == None:
            return
        else:
            for timer in NavigationInstance.instance.RecordTimer.timer_list:
                if timer.isRunning() and not timer.justplay and timer.Filename == self.tmrecord.Filename:
                    self.TimerActualizar.stop()
                    self.TimerTemp.stop()
                    if timer.repeated:
                        return False
                    timer.afterEvent = AFTEREVENT.NONE
                    NavigationInstance.instance.RecordTimer.removeEntry(timer)
                    if not grabando(self):
                        self['img_red'].hide()
                    self.buildList()

            return

    def muestra(self, cual, texto):
        self['key_' + cual].show()
        self['img_' + cual].show()
        self['key_' + cual].setText(_(texto))

    def accionlistaproc(self):
        self['listaproc'].selectionEnabled(0)
        texto = ' '
        templista = []
        if self.inicio == 8:
            self['listaproc'].selectionEnabled(0)
            if self.tarea == 'dmesg':
                orden = 'dmesg'
            else:
                orden = 'ps'
            Console().ePopen('%s >/tmp/tempinfo1' % orden)
            booklist = None
            booklist = open('/tmp/tempinfo1', 'r')
            temparray = []
            if booklist is not None:
                for oneline in booklist:
                    temparray.append(oneline)

                booklist.close()
            Console().ePopen('rm -f /tmp/tempinfo1')
            for i in range(0, len(temparray)):
                if i > 0:
                    templista.append(IniciaSelListEntryLista(texto1=temparray[i]))

        if not templista == None:
            self['listaproc'].setList(templista)
        self['listaproc'].show()
        return texto

    def accionlista(self):
        global filename
        self['listainfo'].selectionEnabled(0)
        texto = ' '
        templista = []
        if self.inicio == 1:
            listarec = inforecord()
            texto = ''
            if len(listarec) == 1:
                texto = _('File Name') + ' : ' + listarec[0][8] + ''
            else:
                texto = ''
            for infog in listarec:
                templista.append(IniciaSelListEntryInfo(texto1=infog[1] + ' - ' + infog[0], texto2=infog[4] + '(+' + infog[5] + ')', texto3=infog[2], texto4=infog[3], texto5=str(infog[7]) + '%', imagen1=5, progreso=infog[7]))

        elif self.inicio == 6:
            self['listainfo'].selectionEnabled(1)
            sumtam = 0
            sumfree = 0
            sumocupado = 0
            summontado = ''
            sumporcentaje = 0
            contaflash = 0
            entrointernal = False
            for p in harddiskmanager.getMountedPartitions():
                texto = _(str(p.description)).replace('External', _('External'))
                montado = str(p.mountpoint)
                if os.path.exists(p.mountpoint + '/') or p.mountpoint == '/':
                    ntipo = 3
                    if p.mountpoint == '/' or p.mountpoint == '/' or p.mountpoint == '/dev' or p.mountpoint == '/tmp' or p.mountpoint == '/boot' or p.mountpoint == '/media/cf':
                        ntipo = 0
                    elif p.mountpoint[:len('/dev/hda')] == '/dev/hda':
                        ntipo = 0
                    elif p.mountpoint[:len('/autofs/sd')] == '/autofs/sd' or p.mountpoint[:len('/dev/sd')] == '/dev/sd':
                        ntipo = 2
                        texto = 'USB ' + texto
                    elif p.mountpoint[:len('/media/hdd')] == '/media/hdd' or p.mountpoint[:len('/dev/hdb')] == '/dev/hdb':
                        ntipo = 1
                    if p.mountpoint == '/':
                        path = '/'
                    else:
                        path = p.mountpoint + '/'
                    stat = os.statvfs(path)
                    total = stat.f_bsize * stat.f_blocks
                    free = (stat.f_bavail if stat.f_bavail != 0 else stat.f_bfree) * stat.f_bsize
                    ocupado = total - stat.f_bsize * stat.f_bfree
                    porcentaje = int(ocupado * 100 / total)
                    if ntipo == 10:
                        entrointernal = True
                        sumtam = sumtam + total
                        sumfree = sumfree + free
                        sumocupado = sumocupado + ocupado
                        sumporcentaje = sumporcentaje + porcentaje
                        summontado = summontado + '[' + montado + '] '
                        if contaflash == 1:
                            templista.append(IniciaSelListEntryInfo(texto1=texto + ' - ' + summontado, texto2=_('Size') + ' ' + Humanizer(sumtam), texto3=_('Used') + ' ' + Humanizer(sumocupado), texto4=Humanizer(sumfree) + ' ' + _('Free'), texto5=str(sumporcentaje / 6) + '%', imagen1=ntipo, progreso=sumporcentaje / 6, ruta=path + '/'))
                            entrointernal = False
                        contaflash = contaflash + 1
                    else:
                        if entrointernal:
                            templista.append(IniciaSelListEntryInfo(texto1=texto + ' - ' + summontado, texto2=_('Size') + ' ' + Humanizer(sumtam), texto3=_('Used') + ' ' + Humanizer(sumocupado), texto4=Humanizer(sumfree) + ' ' + _('Free'), texto5=str(sumporcentaje / 6) + '%', imagen1=ntipo, progreso=sumporcentaje / 6, ruta=path + '/'))
                            entrointernal = False
                            contaflash = 0
                        templista.append(IniciaSelListEntryInfo(texto1=texto + ' - ' + montado, texto2=_('Size') + ' ' + Humanizer(total), texto3=_('Used') + ' ' + Humanizer(ocupado), texto4=Humanizer(free) + ' ' + _('Free'), texto5=str(porcentaje) + '%', imagen1=ntipo, progreso=porcentaje, ruta=path + '/'))

        elif self.inicio == 7:
            ret = ''
            orden = 'free'
            archivo = '/tmp/tempinfo'
            Console().ePopen('%s >/tmp/tempinfo' % orden)
            booklist = None
            booklist = open(archivo, 'r')
            temparray = []
            if booklist is not None:
                for oneline in booklist:
                    temparray.append(oneline)

                booklist.close()
            Console().ePopen('rm -f /tmp/tempinfo')
            haytotal = False
            totalmem = 0
            totalused = 0
            totalfree = 0
            for i in range(0, len(temparray)):
                if i > 0:
                    array = temparray[i].split()
                    tipo = array[0]
                    ntipo = 4
                    if tipo == 'Mem:':
                        tipo = _('RAM')
                        ntipo = 4
                    elif tipo == 'Swap:':
                        tipo = _('Swap')
                        ntipo = 7
                    elif tipo == 'Total:':
                        haytotal = True
                        tipo = _('Total Memory')
                        ntipo = 6
                    else:
                        tipo = tipo.replace(':', '')
                        ntipo = 9
                    err = False
                    try:
                        total = _('Size') + ' ' + Humanizer(int(array[1]) * 1024)
                        totalmem = totalmem + int(array[1])
                        usado = _('Used') + ' ' + Humanizer(int(array[2]) * 1024)
                        totalused = totalused + int(array[2])
                        libre = _('Free') + ' ' + Humanizer(int(array[3]) * 1024)
                        totalfree = totalfree + int(array[3])
                    except:
                        err = True

                    if not err:
                        if len(array) > 5:
                            if int(array[5]) > 0:
                                tipo = tipo + ' - ' + array[5] + ' ' + _('Buffers')
                        if len(array) > 4:
                            if int(array[4]) > 0:
                                tipo = tipo + ' - ' + Humanizer(int(array[4]) * 1024) + ' ' + _('Shared')
                        try:
                            porcentaje = int(array[2]) * 100 / int(array[1])
                        except:
                            porcentaje = 0

                        templista.append(IniciaSelListEntryInfo(texto1=tipo, texto2=total, texto3=usado, texto4=libre, texto5=str(porcentaje) + '%', imagen1=ntipo, progreso=porcentaje))

            if not haytotal:
                try:
                    porcentaje = totalused * 100 / totalmem
                    templista.append(IniciaSelListEntryInfo(texto1=_('Total memory'), texto2=_('Size') + ' ' + Humanizer(totalmem * 1024), texto3=_('Used') + ' ' + Humanizer(totalused * 1024), texto4=_('Free') + ' ' + Humanizer(totalfree * 1024), texto5=str(porcentaje) + '%', imagen1=1, progreso=porcentaje))
                except:
                    pass

        if not templista == None:
            self['listainfo'].setList(templista)
        self['listainfo'].show()
        return texto

    def inicializa(self):
        self.bloquear = False
        self.buildList()
        self.cargaacciones()

    def getListFromRef(self, ref):
        list = []
        serviceHandler = eServiceCenter.getInstance()
        services = serviceHandler.list(ref)
        bouquets = services and services.getContent('SN', True)
        for bouquet in bouquets:
            services = serviceHandler.list(eServiceReference(bouquet[0]))
            channels = services and services.getContent('SN', True)
            for channel in channels:
                if not channel[0].startswith('1:64:'):
                    list.append(channel[1].replace('\xc2\x86', '').replace('\xc2\x87', ''))

        return list

    def getServiceInfoValue(self, what):
        if self.info is None:
            return ''
        else:
            v = self.info.getInfo(what)
            if v == -2:
                v = self.info.getInfoString(what)
            elif v == -1:
                v = 'N/A'
            return v

    def getFEData(self, frontendDataOrg):
        TYPE_TEXT = 0
        TYPE_VALUE_HEX = 1
        TYPE_VALUE_DEC = 2
        TYPE_VALUE_HEX_DEC = 3
        TYPE_SLIDER = 4
        if frontendDataOrg and len(frontendDataOrg):
            frontendData = ConvertToHumanReadable(frontendDataOrg)
            if frontendDataOrg['tuner_type'] == 'DVB-S':
                return (('NIM', ('0', '1', '2', '3')[frontendData['tuner_number']], TYPE_TEXT),
                 ('Type', 'SAT ' + frontendData['system'], TYPE_TEXT),
                 ('Modulation', frontendData['modulation'], TYPE_TEXT),
                 ('Frequency', frontendData['frequency'], TYPE_VALUE_DEC),
                 ('Symbolrate', frontendData['symbol_rate'], TYPE_VALUE_DEC),
                 ('Polarization', frontendData['polarization'], TYPE_TEXT),
                 ('Inversion', frontendData['inversion'], TYPE_TEXT),
                 ('FEC inner', frontendData['fec_inner'], TYPE_TEXT),
                 ('Pilot', frontendData.get('pilot', None), TYPE_TEXT),
                 ('Rolloff', frontendData.get('rolloff', None), TYPE_TEXT))
            if frontendDataOrg['tuner_type'] == 'DVB-C':
                return (('NIM', ('0', '1', '2', '3')[frontendData['tuner_number']], TYPE_TEXT),
                 ('Type', frontendData['tuner_type'], TYPE_TEXT),
                 ('Frequency', frontendData['frequency'], TYPE_VALUE_DEC),
                 ('Symbolrate', frontendData['symbol_rate'], TYPE_VALUE_DEC),
                 ('Modulation', frontendData['modulation'], TYPE_TEXT),
                 ('Inversion', frontendData['inversion'], TYPE_TEXT),
                 ('FEC inner', frontendData['fec_inner'], TYPE_TEXT))
            if frontendDataOrg['tuner_type'] == 'DVB-T':
                return (('NIM', ('0', '1', '2', '3')[frontendData['tuner_number']], TYPE_TEXT),
                 ('Type', frontendData['tuner_type'], TYPE_TEXT),
                 ('Frequency', frontendData['frequency'], TYPE_VALUE_DEC),
                 ('Channel', str(self.devchfr(frontendData['frequency'])), TYPE_VALUE_DEC),
                 ('Inversion', frontendData['inversion'], TYPE_TEXT),
                 ('Bandwidth', frontendData['bandwidth'], TYPE_VALUE_DEC),
                 ('CodeRateLP', frontendData['code_rate_lp'], TYPE_TEXT),
                 ('CodeRateHP', frontendData['code_rate_hp'], TYPE_TEXT),
                 ('Constellation', frontendData['constellation'], TYPE_TEXT),
                 ('Transmission Mode', frontendData['transmission_mode'], TYPE_TEXT),
                 ('Guard Interval', frontendData['guard_interval'], TYPE_TEXT),
                 ('Hierarchy Inform.', frontendData['hierarchy_information'], TYPE_TEXT))
        return []

    def devchfr(self, frecu):
        ret = 'NA'
        arrfecs = [(21, 474),
         (22, 482),
         (23, 490),
         (24, 498),
         (25, 506),
         (26, 514),
         (27, 522),
         (28, 530),
         (29, 538),
         (30, 546),
         (31, 554),
         (32, 562),
         (33, 570),
         (34, 578),
         (35, 586),
         (36, 594),
         (37, 602),
         (38, 610),
         (39, 618),
         (40, 626),
         (41, 634),
         (42, 642),
         (43, 650),
         (44, 658),
         (45, 666),
         (46, 674),
         (47, 682),
         (48, 690),
         (49, 698),
         (50, 706),
         (51, 714),
         (52, 722),
         (53, 730),
         (54, 738),
         (55, 746),
         (56, 754),
         (57, 762),
         (58, 770),
         (59, 778),
         (60, 786),
         (61, 794),
         (62, 802),
         (63, 810),
         (64, 818),
         (65, 826),
         (66, 834),
         (67, 842),
         (68, 850),
         (69, 858)]
        for ele in arrfecs:
            if ele[1] == int(frecu / 1000000):
                ret = ele[0]
                break

        return ret

    def readSatXml(self):
        satXml = parse('/etc/tuxbox/satellites.xml').getroot()
        if satXml is not None:
            for sat in satXml.findall('sat'):
                name = sat.get('name') or None
                position = sat.get('position') or None
                if name is not None and position is not None:
                    position = '%s.%s' % (position[:-1], position[-1:])
                    if position.startswith('-'):
                        position = '%sW' % position[1:]
                    else:
                        position = '%sE' % position
                    if position.startswith('.'):
                        position = '0%s' % position
                    self.satNames[position] = name

        return

    def getOrbitalPosition(self, info):
        transponderData = info.getInfoObject(iServiceInformation.sTransponderData)
        orbital = 0
        if transponderData is not None:
            if isinstance(transponderData, float):
                return ''
            if transponderData.has_key('tuner_type'):
                if transponderData['tuner_type'] == 'DVB-S' or transponderData['tuner_type'] == 'DVB-S2':
                    orbital = transponderData['orbital_position']
                    orbital = int(orbital)
                    if orbital > 1800:
                        orbital = str(float(3600 - orbital) / 10.0) + 'W'
                    else:
                        orbital = str(float(orbital) / 10.0) + 'E'
                    return orbital
        return ''

    def getServiceNumber(self, name, ref):
        list = []
        if ref.startswith('1:0:2'):
            list = self.radio_list
        elif ref.startswith('1:0:1'):
            list = self.tv_list
        number = ''
        if name in list:
            for idx in range(1, len(list)):
                if name == list[idx - 1]:
                    number = str(idx)
                    break

        return number

    def infored(self):
        ret = ''
        adapters = [ (iNetwork.getFriendlyAdapterName(x), x) for x in iNetwork.getAdapterList() ]
        if not adapters:
            return '\n' + _('No Network Adapters Configured')
        else:
            default_gw = None
            num_configured_if = len(iNetwork.getConfiguredAdapters())
            if num_configured_if < 2 and os_path.exists('/etc/default_gw'):
                unlink('/etc/default_gw')
            if os_path.exists('/etc/default_gw'):
                fp = open('/etc/default_gw', 'r')
                result = fp.read()
                fp.close()
                default_gw = result
            hay1 = ''
            if len(adapters) == 0:
                ret = _('iface') + ' : ' + 'eth0' + '\n' + _('Name') + ' : ' + _(iNetwork.getFriendlyAdapterName('eth0')) + _('Default') + '-> ' + str(True) + _('Active') + '-> ' + str(True) + '\n'
            else:
                for x in adapters:
                    cpre = ''
                    if x[1] == default_gw:
                        default_int = True
                        cpre = _('Default')
                    else:
                        default_int = False
                    if iNetwork.getAdapterAttribute(x[1], 'up') is True:
                        active_int = True
                    else:
                        active_int = False
                    description = iNetwork.getFriendlyAdapterDescription(x[1])
                    if active_int:
                        estado = _('Active')
                    else:
                        estado = _('Inactive')
                    ret = ret + _(x[0]) + ' (' + str(x[1]) + ') -> ' + cpre + _('Status') + ' : ' + estado + '\n\n'
                    if active_int:
                        iNetwork.loadNameserverConfig()
                        ret = ret + _('IP') + ' : ' + str(iNetwork.getAdapterAttribute(x[1], 'ip')) + '\n'
                        ret = ret + _('Mask') + ' : ' + str(iNetwork.getAdapterAttribute(x[1], 'netmask')) + '\n'
                        if iNetwork.getAdapterAttribute(x[1], 'gateway'):
                            dhcpl = _('yes')
                        else:
                            dhcpl = _('no')
                        if iNetwork.getAdapterAttribute(x[1], 'dhcp'):
                            dhcp2 = _('yes')
                        else:
                            dhcp2 = _('no')
                        ret = ret + _('Gateway') + ' : ' + str(iNetwork.getAdapterAttribute(x[1], 'gateway')) + '\n'
                        ret = ret + _('Dhcp') + ' : ' + dhcp2 + '\n'
                        nameserver = (iNetwork.getNameserverList() + [[0,
                          0,
                          0,
                          0]] * 2)[0:2]
                        ret = ret + _('Primary DNS') + ' : ' + str(nameserver[0]) + '\n'
                        ret = ret + _('Secondary DNS') + ' : ' + str(nameserver[1]) + '\n\n'
                        estadis = cargaosinfo('ifconfig ' + x[1] + ' | grep bytes', True)
                        if 'Device not found' in estadis:
                            estadis = ''
                        estadis = estadis.replace('RX bytes', _('Received bytes')).replace('TX bytes', _('Transmited bytes')).replace('   ', ' ')
                        ret = ret + _('Stats') + ' :\n' + estadis
                        if self.tarea == 'ping':
                            cpong = cargaosinfo('ping -c 4 -q -W 4 google.com', True)
                        else:
                            cpong = cargaosinfo('ping -c 1 -q -W 4 google.com', True)
                        ippub = ''
                        if len(cpong + ' ') < 2:
                            cpong = _('Internet Conection Not Avaiable') + '\n'
                        else:
                            laurl = 'http://checkip.dyndns.org/'
                            try:
                                response = urllib2.urlopen(laurl, timeout=4)
                                ippub = response.read()
                                xstr = ippub.split('<body>')[1]
                                xstr = xstr.split('</body>')[0]
                                if len(xstr) > 8:
                                    ippub = xstr
                                xstr = xstr.split(':')[1]
                                if len(xstr) > 8:
                                    ippub = xstr.lstrip().rstrip()
                            except:
                                ippub = _('No Info Avaiable')

                            if len(ippub) > 8:
                                ippub = '\n' + _('Public IP') + ' : ' + ippub + '\n'
                        test = _('Internet Conection Test') + ' :\n' + cpong.replace('--- google.com ping statistics ---', '').replace('\n\n', '').replace('packets transmitted', _('packets transmitted')).replace('packets received', _('packets received')).replace('packet loss', _('packet loss')).replace('round-trip', '')
                        if test == _('No Info Avaiable'):
                            test = _('Ping google.com Failed\n')
                        ret = hay1 + ret + '\n' + test + ippub
                        hay1 = '\n'

            self.tarea = ''
            return ret

    def buildList(self):
        global lenguaje
        self.TimerActualizar.stop()
        self.TimerTemp.stop()
        self['textoinfo'].setText('\n' + _('Please Wait'))
        self['titulo'].setText(' ')
        self['listainfo'].hide()
        self['listaproc'].hide()
        lista = []
        xvalor = cargalista(self.inicio, grabando(self))
        lista = xvalor[1]
        indice = xvalor[0]
        self.indice = indice
        if not self.iniciado:
            self['lista'].setList(lista)
        self.iniciado = True
        if indice >= 0:
            self['lista'].moveToIndex(indice)
            titulo = listamenu[indice][1]
            self['titulo'].setText(titulo)
        texto = _('Information Not Avaiable')
        self.actualizar = False
        if self.inicio == 1:
            if grabando(self):
                texto = '\n\n\n\n\n'
                texto = texto + self.accionlista() + '\n'
                self.actualizar = True
            else:
                texto = '\n' + _('No Record In Progress')
                texto = texto + '\n\n' + _('Recording Paths') + ': ' + str(config.usage.default_path.value) + '\n'
                texto = texto + _('Instant Record Path') + ': ' + str(config.usage.instantrec_path.value) + '\n'
        if self.inicio == 3:
            texto = ''
            texto = _('STB') + ' : ' + getBoxType() + '\n\n'
            texto = texto + cargaosinfo('cat /proc/cpuinfo')
        elif self.inicio == 7:
            texto = '  '
            ret = self.accionlista()
            self.actualizar = True
        elif self.inicio == 2:
            try:
                name = self.info.getName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                nomcan = ServiceReference(self.session.nav.getCurrentlyPlayingServiceReference()).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                texto = _('Channel') + ' : ' + nomcan + '\n' + _('Provider') + ' : ' + self.getServiceInfoValue(iServiceInformation.sProvider) + '\n'
                texto = texto + _('Service Reference') + ' : ' + self.session.nav.getCurrentlyPlayingServiceReference().toString() + '\n'
                calidad = 0
                status = self.feinfo.getFrontendStatus()
                calidad = status.get('tuner_signal_quality') * 100 / 65536
                potencia = 0
                status = self.feinfo.getFrontendStatus()
                potencia = status.get('tuner_signal_power') * 100 / 65536
                terror = 0
                status = self.feinfo.getFrontendStatus()
                terror = status.get('tuner_bit_error_rate') * 100 / 65536
                texto = texto + _('Signal Quality') + ' ' + ponPorcen(calidad) + '\n' + _('Intensity') + ' ' + ponPorcen(potencia) + '\n' + str(terror) + '% ' + _('Of Error') + '\n\n'
                aspect = self.getServiceInfoValue(iServiceInformation.sAspect)
                if aspect in (1, 2, 5, 6, 9, 10, 13, 14):
                    texto = texto + _('Video Format') + ' -> 4:3'
                else:
                    texto = texto + _('Video Format') + ' -> 16:9'
                width = self.info and self.info.getInfo(iServiceInformation.sVideoWidth) or -1
                height = self.info and self.info.getInfo(iServiceInformation.sVideoHeight) or -1
                texto = texto + '\n' + _('Video Size') + ' : ' + '%dx%d' % (width, height) + '\n'
                TYPE_VALUE_HEX_DEC = 3
                xLabels = (('VideoPID',
                  self.getServiceInfoValue(iServiceInformation.sVideoPID),
                  TYPE_VALUE_HEX_DEC,
                  4),
                 ('AudioPID',
                  self.getServiceInfoValue(iServiceInformation.sAudioPID),
                  TYPE_VALUE_HEX_DEC,
                  4),
                 ('PCRPID',
                  self.getServiceInfoValue(iServiceInformation.sPCRPID),
                  TYPE_VALUE_HEX_DEC,
                  4),
                 ('PMTPID',
                  self.getServiceInfoValue(iServiceInformation.sPMTPID),
                  TYPE_VALUE_HEX_DEC,
                  4),
                 ('TXTPID',
                  self.getServiceInfoValue(iServiceInformation.sTXTPID),
                  TYPE_VALUE_HEX_DEC,
                  4),
                 ('TSID',
                  self.getServiceInfoValue(iServiceInformation.sTSID),
                  TYPE_VALUE_HEX_DEC,
                  4),
                 ('ONID',
                  self.getServiceInfoValue(iServiceInformation.sONID),
                  TYPE_VALUE_HEX_DEC,
                  4),
                 ('SID',
                  self.getServiceInfoValue(iServiceInformation.sSID),
                  TYPE_VALUE_HEX_DEC,
                  4))
                carsep = '\n'
                carsep2 = '\n'
                for j in xLabels:
                    texto = texto + j[0] + ' : ' + str(j[1]) + carsep
                frontendData = self.feinfo and self.feinfo.getAll(True)
                xLabels = self.getFEData(frontendData)
                tuners = '\n'
                nims = nimmanager.nimList()
                texto = texto + '\n'
                orbital = self.getOrbitalPosition(self.info)
                satName = self.satNames.get(orbital, orbital)
                conta = 0
                for j in xLabels:
                    if conta == 0:
                        numero = j[1]
                        for count in (0, 1, 2, 3):
                            if count < len(nims):
                                if numero == str(count):
                                    texto = texto + str(nims[count]) + '\n'
                                    if not satName == None and not satName == '':
                                        texto = texto + _('Service') + ' : ' + satName
                                        if str(orbital) not in satName:
                                            texto = texto + ' (' + str(orbital) + ')'
                                        texto = texto + '\n'
                                    break
                    else:
                        texto = texto + _(j[0]) + ' : ' + _(str(j[1])) + carsep2
                    conta = conta + 1
            except:
                texto = '\n' + _('Information Not Avaiable')

            self.actualizar = True
        elif self.inicio == 9:
            texto = ''
            modosaudio = ['PCM', 'RAW']
            modosdolby = ['Line Mode', 'RF Mode']
            texto = texto + _('Video Mode') + ' : ' + str(config.av.videoport.value) + '\n'
            if config.av.videoport.value in config.av.videomode:
                try:
                    texto = texto + _('Resolution') + ' : ' + str(config.av.videomode[config.av.videoport.value].value) + '\n'
                except:
                    pass

                try:
                    texto = texto + _('Refresh Rate') + ' : ' + str(config.av.videorate[config.av.videomode[config.av.videoport.value].value].value) + '\n\n'
                except:
                    pass

            try:
                texto = texto + _('Video System') + ' : ' + str(config.av.analogmode.value) + '\n'
            except:
                pass

            try:
                texto = texto + _('Deinterlace') + ' : ' + str(config.av.deinterlace.value) + '\n\n'
            except:
                pass

            try:
                texto = texto + _('Dolby Digital') + ' : ' + modosaudio[int(config.av.dolbydigital.value)] + '\n'
            except:
                pass

            try:
                texto = texto + _('DTS') + ' : ' + modosaudio[int(config.av.dts.value)] + '\n'
            except:
                pass

            try:
                texto = texto + _('AAC') + ' : ' + modosaudio[int(config.av.aac.value)] + '\n'
            except:
                pass

            try:
                texto = texto + _('Other') + ' : ' + modosaudio[int(config.av.otheraudio.value)] + '\n'
            except:
                pass

            try:
                texto = texto + _('Dolby Digital Mode') + ' : ' + modosaudio[int(config.av.dolbydigitalmode.value)] + '\n\n'
            except:
                pass

            try:
                texto = texto + _('Audio Prebuffering (ms)') + ' : ' + str(config.av.aprebuff.value) + '\n'
                texto = texto + _('Video Prebuffering (ms)') + ' : ' + str(config.av.vprebuff.value) + '\n\n'
            except:
                pass

            nomskin = str(config.skin.primary_skin.value).replace('/skin.xml', '')
            texto = texto + _('Skin') + ' : ' + nomskin + '\n'
            texto = texto + '\n'
        elif self.inicio == 4:
            texto = _('Operating System') + ' :\n' + cargaosinfo('cat /proc/version') + '\n'
            retinfo = ImageVersionString()
            texto = texto + _('PE Version') + ' : ' + retinfo + '\n\n'
            texto = texto + _('Date/Time') + ' :\n' + cargaosinfo('date') + '\n'
            texto = texto + _('Up Time') + ' :\n' + cargaosinfo('uptime')
            self.actualizar = True
        elif self.inicio == 6:
            texto = ' '
            ret = self.accionlista()
            textot = '\n\n\n\n\n' + texto
            texto = textot
        elif self.inicio == 5:
            texto = _('Host Name') + ' : ' + cargaosinfo('hostname').replace('\n', '')
            array = cargaosinfo('ifconfig | grep HWaddr').split('HWaddr')
            if len(array) > 1:
                texto = texto + '\n' + _('MAC Adress') + ' : ' + array[1]
            texto = texto + '\n'
            texto = texto + self.infored() + '\n'
            lascon = cargaosinfo('netstat -e | grep ESTABLISHED', True)
            arrcon = lascon.split('\n')
            cadcon = ''
            contacon = 1
            for iji in arrcon:
                if len(iji) > 4:
                    cadcon = cadcon + str(contacon) + ') ' + iji.replace('ESTABLISHED', '').replace('    ', ' ').replace('   ', ' ').replace('  ', ' ').replace(' 0', '').replace(' ', ' :: ') + '\n'
                    contacon = contacon + 1

            lascon = lascon
            texto = texto + _('Active Connections') + ' (' + str(contacon - 1) + '):\n' + cadcon
            self.actualizar = False
        elif self.inicio == 8:
            ret = self.accionlistaproc()
            texto = '   '
            self.actualizar = True
        elif self.inicio == 10:
            texto = '\n\n' + _('PE Info') + '\n\n' + _('Advanced information panel')
            texto = texto + '\n\n' + _('For more information visit https://openvision.tech')
            texto = texto + '\n\n' + _('You can control your Open Vision via our android app')
            texto = texto + '\n\n' + _('But first take a look at : https://openvision.tech/openvision-table.html')
            texto = texto + '\n\n' + _('Then search for Persian Grandeur on Google Play')
            texto = texto + '\n\n' + _('Or download it from : https://openvision.tech')
            texto = texto + '\n\n' + _('Developed for Open Vision images')
            lenguaje = 'en'
        self['textoinfo'].setText(texto)
        if self.actualizar:
            self.TimerActualizar.start(15000, True)
        if self.upagina:
            self['textoinfo'].lastPage()
        return

    def key_re(self):
        self.TimerActualizar.stop()
        self.TimerTemp.stop()
        self.TimerCarga.stop()
        if self.tarea == 'dmesg':
            self.tarea = ''
        idx = self['lista'].getSelectionIndex()
        if self.indice == idx:
            self.buildList()
        else:
            self.cargar()

    def key_ok(self):
        self.TimerActualizar.stop()
        self.TimerCarga.stop()
        self.TimerTemp.stop()
        if not self.bloquear:
            self['titulo'].setText(' ')
            self['textoinfo'].setText('\n' + _('Please Wait'))
            self['listainfo'].hide()
            self['listaproc'].hide()
            self.bloquear = True
            lalista = self['lista'].list
            idx = self['lista'].getSelectionIndex()
            numero = listamenu[idx][2]
            self.inicio = numero
            self.inicializa()

    def key_info(self):
        info1 = _('PE Info') + '\n'
        info2 = _('Advanced Information Panel')
        cmens = info1 + '\n' + info2
        dei = self.session.open(MessageBox, cmens, MessageBox.TYPE_INFO)
        dei.setTitle(_('About'))

    def key_left2(self):
        if self['listainfo'].getSelectionIndex() == 0:
            self['listainfo'].moveToIndex(len(self['listainfo'].list) - 1)
        else:
            self['listainfo'].up()

    def key_right2(self):
        if self['listainfo'].getSelectionIndex() == len(self['listainfo'].list) - 1:
            self['listainfo'].moveToIndex(0)
        else:
            self['listainfo'].down()

    def key_left(self):
        if self.inicio == 6:
            self.key_left2()
        else:
            self['textoinfo'].pageUp()
            self['listainfo'].selectionEnabled(1)
            self['listainfo'].pageUp()
            self['listainfo'].selectionEnabled(0)
            self['listaproc'].selectionEnabled(1)
            self['listaproc'].pageUp()
            self['listaproc'].selectionEnabled(0)
        self.upagina = False

    def key_right(self):
        if self.inicio == 6:
            self.key_right2()
        else:
            self['textoinfo'].pageDown()
            self['listainfo'].selectionEnabled(1)
            self['listainfo'].pageDown()
            self['listainfo'].selectionEnabled(0)
            self['listaproc'].selectionEnabled(1)
            self['listaproc'].pageDown()
            self['listaproc'].selectionEnabled(0)
        self.upagina = True

    def key_up(self):
        self.TimerActualizar.stop()
        self.TimerCarga.stop()
        self.TimerTemp.stop()
        if self['lista'].getSelectionIndex() == 0:
            self['lista'].moveToIndex(len(self['lista'].list) - 1)
        else:
            self['lista'].up()
        self.upagina = False
        self.TimerTemp.start(2000, True)

    def key_down(self):
        self.TimerTemp.stop()
        self.TimerActualizar.stop()
        self.TimerCarga.stop()
        if self['lista'].getSelectionIndex() == len(self['lista'].list) - 1:
            self['lista'].moveToIndex(0)
        else:
            self['lista'].down()
        self.upagina = False
        self.TimerTemp.start(2000, True)

    def exit(self):
        self.TimerActualizar.stop()
        self.TimerCarga.stop()
        self.TimerTemp.stop()
        self.close(0)


class PEInfo(Screen):
    skin = '\n\t<screen position="center,center" size="1050,602" title="%s">\n\t<widget name="textoinfo" position="288,37" size="745,522" valign="top" halign="left" text="%s" font="Regular; 18" zPosition="1" />\n\t</screen>' % (_('PE') + ' ' + 'Information', _('Please Wait'))

    def __init__(self, session, **kwargs):
        self.session = session
        self['textoinfo'] = Label(_('Please Wait'))
        Screen.__init__(self, session)
        self.inicio = 2
        self.iniciado = False
        self['setupActions'] = ActionMap(['WizardActions'], {'back': self.close}, -2)
        self.onShow.append(self.cargapantalla)

    def cargapantalla(self):
        pinicial = self.inicio
        if grabando(self):
            pinicial = 1
        if not self.iniciado:
            self.iniciado = True
            self.session.openWithCallback(self.vueltapantalla, PEInfoTexto, inicio=pinicial)

    def vueltapantalla(self, respuesta):
        if respuesta == 0:
            self.close()
        elif respuesta == 1:
            self.session.openWithCallback(self.vueltapantalla, PEInfoTexto, inicio=1)
        elif respuesta == 6:
            self.session.openWithCallback(self.vueltapantalla, PEInfoTexto, inicio=6)
        elif respuesta == 8:
            self.session.openWithCallback(self.vueltapantalla, PEInfoTexto, inicio=8)
        elif respuesta == 10:
            self.session.openWithCallback(self.vueltapantalla, PEInfoTexto, inicio=10)
        elif respuesta == 2:
            self.session.openWithCallback(self.vueltapantalla, PEInfoTexto, inicio=2)
        elif respuesta == 3:
            self.session.openWithCallback(self.vueltapantalla, PEInfoTexto, inicio=3)
        elif respuesta == 5:
            self.session.openWithCallback(self.vueltapantalla, PEInfoTexto, inicio=5)
        elif respuesta == 9:
            self.session.openWithCallback(self.vueltapantalla, PEInfoTexto, inicio=9)
        elif respuesta == 4:
            self.session.openWithCallback(self.vueltapantalla, PEInfoTexto, inicio=4)
        elif respuesta == 7:
            self.session.openWithCallback(self.vueltapantalla, PEInfoTexto, inicio=7)
        else:
            self.close()

    def exit(self):
        self.close()


def start_from_mainmenu(menuid, **kwargs):
    if menuid == 'information':
        return [(_('PE Info'),
          iniciainfo,
          'PEInfo',
          1)]
    return []

def OVLock():
    try:
        from ov import gettitle
        ovtitle = gettitle()
        return ovtitle
    except:
        return False

def iniciainfo(session, **kwargs):
    if OVLock()==False:
        return
    else:
        session.open(PEInfo)


def Plugins(**kwargs):
    name = _('PE Info')
    descr = _('Advanced Information Panel')
    list = []
    if True:
        list.append(PluginDescriptor(name=_('PE Info'), description=descr, where=PluginDescriptor.WHERE_MENU, fnc=start_from_mainmenu))
    return list
