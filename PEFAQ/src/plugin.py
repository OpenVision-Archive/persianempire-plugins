#!/usr/bin/python
# -*- coding: utf-8 -*-
from enigma import *
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.MultiContent import MultiContentEntryText
from enigma import eListboxPythonMultiContent, gFont
from Screens.InfoBarGenerics import *
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Components.ActionMap import ActionMap
import os
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Components.Language import language
from os import environ
import gettext
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('PEFAQ', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/PEFAQ/locale/'))

def _(txt):
    t = gettext.dgettext('PEFAQ', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


carpetaimg = resolveFilename(SCOPE_PLUGINS, 'Extensions/PEFAQ/img/')


class IniciaSelListFaqs(MenuList):

    def __init__(self, list, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(30)
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 17))


def IniciaSelListEntryFaqs(texto, yavista = False):
    global carpetaimg
    res = [texto]
    res.append(MultiContentEntryText(pos=(35, 4), size=(1000, 30), font=0, text=texto))
    if not yavista:
        imagen = 'question.png'
    else:
        imagen = 'info.png'
    png = '' + carpetaimg + '' + imagen + ''
    if fileExists(png):
        fpng = LoadPixmap(png)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST,
         2,
         2,
         24,
         24,
         fpng))
    return res


class IniciaSelList(MenuList):

    def __init__(self, list, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(70)
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 17))

class PEVerfaq(Screen):
    skin = '\n\t<screen name="PEVerfaqsScr" position="center,center" size="1000,610" title="%s">\n\n\t<widget name="reply" render="Listbox" position="8,87" size="970,470" scrollbarMode="showOnDemand" zPosition="12" text=" " font="Regular; 19" />\n\t<ePixmap name="new ePixmap" position="10,33" size="35,25" pixmap="~/img/question.png" alphatest="blend" transparent="1" zPosition="10"/>\n\n\t<widget name="mode" position="8,31" size="970,50" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" />\n\n\t<widget name="key_red" position="654,585" size="162,22" transparent="1" text="Exit" font="Regular; 16"/>\n\n\t<widget name="key_mode" position="8,8" size="685,22" transparent="1" text=" " font="Regular; 15" halign="center" />\n\t<convert type="TemplatedMultiContent">{"template": [MultiContentEntryText(pos = (50, 0), size = (460, 26), font=0, flags = RT_HALIGN_LEFT, text = 1),MultiContentEntryPixmapAlphaTest(pos = (5, 0), size = (25, 24), png = 2),],"fonts": [gFont("Regular", 22)],"itemHeight": 26}</convert>\n\t</screen>' % _('FAQs')

    def __init__(self, session, numeroquestion = None):
        self.session = session
        Screen.__init__(self, session)
	self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PEFAQ")
        self.nquestion = numeroquestion
        self['reply'] = Label(_(''))
        self.modeactivo = 1
        self['mode'] = Label(_(''))
        self['key_mode'] = Label(_(''))
        self['key_red'] = Label(_('Back'))
        self['setupActions'] = ActionMap(['WizardActions',
         'DirectionActions'], {'green': self.exit,
         'red': self.exit,
         'blue': self.exit,
         'yellow': self.exit,
         'back': self.exit,
         'info': self.exit,
         'ok': self.exit}, -2)
        self.onLayoutFinish.append(self.cargaquestion)

    def exit(self):
        self.close(True)

    def cargaquestion(self):
        self['key_red'].setText(_(' '))
        self['key_mode'].setText(_('Press Any Key = Go Back'))
        archivo = resolveFilename(SCOPE_PLUGINS, 'Extensions/PEFAQ/PEFAQs.xml')
        import xml.sax.xmlreader
        from xml.dom import minidom, Node
        menu = xml.dom.minidom.parse(archivo)
        rootNode = menu.childNodes[0]
        contador = 0
        for node in rootNode.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                for node2 in node.childNodes:
                    if node2.nodeType == Node.ELEMENT_NODE:
                        id = question = category = reply = ''
                        for node3 in node2.childNodes:
                            if node2.nodeType == Node.ELEMENT_NODE:
                                for node4 in node3.childNodes:
                                    if node3.nodeType == Node.ELEMENT_NODE:
                                        if node4.nodeType == Node.TEXT_NODE:
                                            if node3.nodeName == 'category':
                                                category = node4.nodeValue.encode('utf-8')
                                            elif node3.nodeName == 'id':
                                                id = node4.nodeValue.encode('utf-8')
                                            elif node3.nodeName == 'question':
                                                question = node4.nodeValue.encode('utf-8')
                                            elif node3.nodeName == 'reply':
                                                reply = node4.nodeValue.encode('utf-8')

                        contador = contador + 1
                        if self.nquestion == str(contador):
                            self['mode'].setText('     ' + question + ' (' + category + ')')
                            self['reply'].setText(reply)
                            break

class PEFaqs(Screen):
    skin = '\n\t<screen name="PEFaqsScr" position="center,center" size="1000,610" title="%s">\n\n\t<widget name="list" position="8,67" size="970,490" scrollbarMode="showOnDemand" zPosition="12" />\n\t<widget name="mode" position="8,31" size="970,30" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" />\n\n\t<ePixmap name="new ePixmap" position="620,584" size="35,25" pixmap="~/img/red.png" alphatest="blend" transparent="1" />\n\t<widget name="key_red" position="654,585" size="162,22" transparent="1" text="Exit" font="Regular; 16"/>\n\t<ePixmap name="new ePixmap" position="715,584" size="35,25" pixmap="~/img/green.png" alphatest="blend" transparent="1" />\n\t<widget name="key_green" position="749,585" size="462,22" transparent="1" text="Update" font="Regular; 16"/>\n\t<widget name="key_mode" position="8,8" size="685,22" transparent="1" text=" " font="Regular; 15" halign="center" />\n\t</screen>' % _('Open Vision FAQs - https://openvision.tech')

    def __init__(self, session, instance = None, args = 0):
        self.session = session
        Screen.__init__(self, session)
	self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PEFAQ")
        self.faqs = []
        self['list'] = IniciaSelListFaqs([])
        self.modeactivo = 1
        self.categorys = ['All']
        self.vistas = []
        self['mode'] = Label(_(''))
        self['key_mode'] = Label(_(''))
        self['key_red'] = Label(_('Exit'))
        self['key_green'] = Label(_('Update'))
        self['setupActions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'green': self.update,
         'red': self.exit,
         'blue': self.exit,
         'yellow': self.exit,
         'back': self.exit,
         'left': self.key_left,
         'right': self.key_right,
         'up': self.key_up,
         'down': self.key_down,
         'info': self.key_info,
         'ok': self.key_ok}, -2)
        self.onLayoutFinish.append(self.buildList)

    def update(self):
        self.session.open(Console,title = _("Open Vision FAQs update"), cmdlist = ["echo Downloading latest FAQs , Please wait", "wget https://openvision.tech/PEFAQs.zip -O /tmp/PEFAQs.zip > /dev/null 2>&1", "echo Extracting update file", "unzip -o /tmp/PEFAQs.zip -d %s/Extensions/PEFAQ > /dev/null 2>&1", "rm -rf /tmp/PEFAQs.zip > /dev/null 2>&1", "echo Done!"]) % resolveFilename(SCOPE_PLUGINS)

    def cargaquestions(self, filtrado = None):
        self.categorys = ['All']
        self.faqs = []
        archivo = resolveFilename(SCOPE_PLUGINS, 'Extensions/PEFAQ/PEFAQs.xml')
        import xml.sax.xmlreader
        from xml.dom import minidom, Node
        menu = xml.dom.minidom.parse(archivo)
        rootNode = menu.childNodes[0]
        contador = 0
        for node in rootNode.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                for node2 in node.childNodes:
                    if node2.nodeType == Node.ELEMENT_NODE:
                        id = question = category = reply = ''
                        for node3 in node2.childNodes:
                            if node2.nodeType == Node.ELEMENT_NODE:
                                for node4 in node3.childNodes:
                                    if node3.nodeType == Node.ELEMENT_NODE:
                                        if node4.nodeType == Node.TEXT_NODE:
                                            if node3.nodeName == 'category':
                                                category = node4.nodeValue.encode('utf-8')
                                            if node3.nodeName == 'id':
                                                id = node4.nodeValue.encode('utf-8')
                                            elif node3.nodeName == 'question':
                                                question = node4.nodeValue.encode('utf-8')

                        contador = contador + 1
                        if filtrado == None or filtrado == category:
                            self.faqs.append((contador, question, category))
                        if category not in self.categorys:
                            self.categorys.append(category)

    def buildList(self, modelist = 1):
        self['key_mode'].setText(_('Use The Cursor Left (<) And Right (>) To Filter By Category'))
        titulo = _(' FAQs')
        cfiltrado = None
        if modelist > 1:
            titulo = titulo + ' :: Category : ' + self.categorys[modelist - 1]
            cfiltrado = self.categorys[modelist - 1]
        else:
            titulo = titulo + ' :: Displaying All'
        self.modeactivo = modelist
        self.cargaquestions(cfiltrado)
        self['mode'].setText(titulo + ' (' + str(len(self.faqs)) + ') <>')
        list = []
        for i in range(0, len(self.faqs)):
            lafaq = '' + self.faqs[i][1]
            numero = str(self.faqs[i][0])
            vista = False
            if numero in self.vistas:
                vista = True
            list.append(IniciaSelListEntryFaqs(lafaq, vista))

        self['list'].setList(list)

    def key_ok(self):
        lalist = self['list'].list
        idx = self['list'].getSelectionIndex()
        texto = str(lalist[idx][0])
        numero = str(self.faqs[idx][0])
        if numero not in self.vistas:
            self.vistas.append(numero)
        info1 = ''
        info2 = texto + ''
        self.buildList(self.modeactivo)
        self.session.openWithCallback(self.callBackFaqsVer, PEVerfaq, numeroquestion=numero)

    def callBackFaqsVer(self, reply):
        if reply:
            pass

    def key_info(self):
        info1 = 'FAQs'
        info2 = 'by Open Vision team , https://openvision.tech'
        cmens = _(info1) + ' [' + nommodelo + ']\n' + _(info2).replace('spazeTeam', 'Open Vision')
        dei = self.session.open(MessageBox, cmens, MessageBox.TYPE_INFO)
        dei.setTitle(_('Open Vision') + ' ' + _('Help'))

    def key_left(self):
        self.modeactivo -= 1
        if self.modeactivo < 1:
            self.modeactivo = len(self.categorys)
        self.buildList(self.modeactivo)
        self['list'].moveToIndex(0)

    def key_right(self):
        self.modeactivo += 1
        if self.modeactivo > len(self.categorys):
            self.modeactivo = 1
        self.buildList(self.modeactivo)
        self['list'].moveToIndex(0)

    def key_up(self):
        self['list'].up()

    def key_down(self):
        self['list'].down()

    def exit(self):
        self.close(True)

def OVLock():
    try:
        from ov import gettitle
        ovtitle = gettitle()
        return ovtitle
    except:
        return False

def main(session, **kwargs):
        if OVLock()==False:
            return
     	else:
            session.open(PEFaqs)

def Plugins(**kwargs):
	return PluginDescriptor(
			name = _("PE FAQ"),
			description = _("FAQs for Open Vision"),
			where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
			icon="pefaq.png",
			fnc=main)
