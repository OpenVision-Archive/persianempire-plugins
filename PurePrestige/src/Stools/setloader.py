from enigma import *
from Screens.MessageBox import MessageBox
from Components.Label import Label
from Components.Button import Button
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.PluginComponent import plugins
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_SKIN, copyfile, pathExists, createDir, removeDir, fileExists, copytree
from Components.Pixmap import Pixmap
from Plugins.Plugin import PluginDescriptor
from Components.config import ConfigSelection, config, ConfigSubsection, ConfigText, ConfigYesNo, getConfigListEntry, configfile
from time import *
from Screens.Screen import Screen
from Components.Sources.List import List
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.ServiceEvent import ServiceEvent
from Components.ServiceEventTracker import ServiceEventTracker
from Components.ProgressBar import ProgressBar
from Tools.LoadPixmap import LoadPixmap
from Components.FileList import FileList
import os
import sys
from Components.ConfigList import ConfigListScreen
from urlparse import urlparse
import xml.etree.cElementTree
import httplib
from Tools.Directories import resolveFilename, pathExists, SCOPE_MEDIA, copyfile
from Screens.Standby import TryQuitMainloop
import datetime
from ServiceReference import ServiceReference
from enigma import eTimer, eDVBDB, eServiceCenter, eServiceReference, iPlayableService, iFrontendInformation
import re
from Components.Console import Console

Tunisiasat_HOST = 'tunisia-dreambox.info'
Tunisiasat_PATH = 'http://www.tunisia-dreambox.info/dreambox-e2-addons/dreambox-e2-updates/Settings/'
SARI_HOST = 'tunisia-dreambox.info'
SARI_PATH = '/e2-addons-manager/TunisiaSat-Settings/'
SAMI73_HOST = 'tunisia-dreambox.info'
SAMI73_PATH = '/e2-addons-manager/TunisiaSat-Settings/'
VHANNIBAL_HOST = 'adams.mine.nu'
VHANNIBAL_PATH = '/vhannibal/'
CYRUS_HOST = 'adams.mine.nu'
CYRUS_PATH = '/cyrus/'
VHANNIBAL_HOST = 'adams.mine.nu'
VHANNIBAL_PATH = '/vhannibal/'
MORPHEUS_HOST = 'openee.sifteam.eu'
MORPHEUS_PATH = '/settings/morph883/'
TMP_SETTINGS_PWD = '/tmp/sl_settings_tmp'
TMP_IMPORT_PWD = '/tmp/sl_import_tmp'
ENIGMA2_SETTINGS_PWD = '/etc/enigma2'
ENIGMA2_TUXBOX_PWD = '/etc/tuxbox'
config.plugins.settingsloader = ConfigSubsection()
config.plugins.settingsloader.keepterrestrial = ConfigYesNo(False)
config.plugins.settingsloader.keepsatellitesxml = ConfigYesNo(False)
config.plugins.settingsloader.keepcablesxml = ConfigYesNo(False)
config.plugins.settingsloader.keepterrestrialxml = ConfigYesNo(False)
config.plugins.settingsloader.keepbouquets = ConfigText('', False)
config.plugins.settingsloader.updatebouqeuts = ConfigSelection(default='no', choices=[('no', _('no')), ('select', _('select bouquets to keep')), ('yes', _('yes'))])

def dirsremove(folder):
    try:
        for root, dirs, files in os.walk(folder):
            for f in files:
                os.remove(os.path.join(root, f))

            for d in dirs:
                removeDir(os.path.join(root, d))

    except:
        pass


class PurePrestigeSL_SettingsList(Screen):

    def __init__(self, session, list, title):
        Screen.__init__(self, session)
        self.session = session
        self.setTitle(title)
        self.drawList = []
        self.list = list
        for entry in self.list:
            self.drawList.append(self.buildListEntry(entry[0], entry[1]))

        self['list'] = List(self.drawList)
        self['key_yellow'] = Button('Install')
        self['key_blue'] = Button(_('Back'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok': self.ok,
         'yellow': self.ok,
         'cancel': self.quit}, -2)

    def buildListEntry(self, sat, date):
        return (sat, date)

    def download(self):
        try:
            dirsremove(TMP_IMPORT_PWD)
        except:
            pass

        try:
            os.mkdir(TMP_IMPORT_PWD)
        except:
            pass

        self.installed = False
        url = urlparse(self.url)
        try:
            conn = httplib.HTTPConnection(url.netloc)
            conn.request('GET', url.path)
            httpres = conn.getresponse()
            if httpres.status == 200:
                tmp = url.path.split('/')
                filename = TMP_IMPORT_PWD + '/' + tmp[len(tmp) - 1]
                out = open(filename, 'w')
                out.write(httpres.read())
                out.close()
                self.installed = SL_Deflate().deflate(filename)
            else:
                self.session.open(MessageBox, _('Cannot download settings (%s)') % self.url, MessageBox.TYPE_ERROR)
                return
        except Exception as e:
            print e
            self.session.open(MessageBox, _('Cannot download settings (%s)') % self.url, MessageBox.TYPE_ERROR)
            return

        if self.installed == True:
            if os.path.exists('/tmp/sl_settings_tmp/lamedb'):
                print 'lamedb exists m1'
                settings = SL_Settings()
                settings.apply()
            else:
                self.session.open(MessageBox, _('Settings installation failed,format may be not supported or files in server corrupted'), type=MessageBox.TYPE_INFO, timeout=5)
                self.installed == False
                self.removedirs()
                return
        else:
            self.session.open(MessageBox, _('Settings installation failed,format may be not supported'), type=MessageBox.TYPE_INFO, timeout=5)
            self.installed == False
            self.removedirs
            return
        self.removedirs()
        if self.installed == False:
            return
        from Plugins.Extensions.PurePrestige.restart import PurePrestigerestartScreen
        self.session.open(PurePrestigerestartScreen)

    def removedirs(self):
        try:
            dirsremove(TMP_SETTINGS_PWD)
        except Exception as e:
            print e

        try:
            dirsremove(TMP_IMPORT_PWD)
        except Exception as e:
            print e

    def restartenigma(self, result):
        if result:
            epgpath = '/media/hdd/epg.dat'
            epgbakpath = '/media/hdd/epg.dat.bak'
            if os.path.exists(epgbakpath):
                os.remove(epgbakpath)
            if os.path.exists(epgpath):
                copyfile(epgpath, epgbakpath)
            Console().ePopen('killall -9 enigma2')

    def ok(self):
        if len(self.list) == 0:
            return
        index = self['list'].getIndex()
        self.url = self.list[index][2]
        self.session.open(PurePrestigeSL_ActionBox, _('Downloading settings'), _('Downloading ...'), self.download)

    def quit(self):
        self.close()


class PurePrestigeSL_Setup(Screen, ConfigListScreen):
    skin = '\n                               <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520" transparent="1"/>\t\n                        <widget name="config" position="15,30" size="610,300" scrollbarMode="showOnDemand" zPosition="2" transparent="1"  />\n\n\t\t\t                               <ePixmap position="15,365" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n\t\t\t<widget name="key_green" position="120,420" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>\n\t\t\t<widget name="key_yellow" position="260,420" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>\n\t\t\t\n\t\t\t\n\t\t\t\n\t\t\t<ePixmap name="green" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/green.png" position="120,415" size="140,40" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t<ePixmap name="yellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" position="260,415" size="140,40" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t<widget name="key_blue" position="400,420" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>\n\t\t\t\n\t\t\t\n\t\t\t\n\n\t\t\t<ePixmap name="blue" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/blue.png" position="400,415" size="140,40" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\t\t\t\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = [getConfigListEntry(_('Keep currently installed bouquets:'), config.plugins.settingsloader.updatebouqeuts),
         getConfigListEntry(_('Keep terrestrial settings:'), config.plugins.settingsloader.keepterrestrial),
         getConfigListEntry(_('Keep satellites.xml:'), config.plugins.settingsloader.keepsatellitesxml),
         getConfigListEntry(_('Keep terrestrial.xml:'), config.plugins.settingsloader.keepterrestrialxml),
         getConfigListEntry(_('Keep cables.xml:'), config.plugins.settingsloader.keepcablesxml)]
        ConfigListScreen.__init__(self, self.list, session=session)
        self['key_green'] = Button('Save')
        self['key_yellow'] = Button('Cancel')
        self['key_blue'] = Button('Bouquets')
        self['key_blue'].hide()
        if config.plugins.settingsloader.updatebouqeuts.value == 'select':
            self['key_blue'].show()
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'green': self.ok,
         'blue': self.selectbq2,
         'yellow': self.keyCancel,
         'cancel': self.keyCancel}, -2)

    def selectbq2(self):
        if config.plugins.settingsloader.updatebouqeuts.value == 'select':
            self.session.open(PurePrestigeSL_KeepBouquets)

    def selectbq(self, result):
        if result:
            if config.plugins.settingsloader.updatebouqeuts.value == 'select':
                self.session.open(PurePrestigeSL_KeepBouquets)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        if config.plugins.settingsloader.updatebouqeuts.value == 'select':
            self['key_blue'].show()
        else:
            self['key_blue'].hide()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        if config.plugins.settingsloader.updatebouqeuts.value == 'select':
            self['key_blue'].show()
        else:
            self['key_blue'].hide()

    def ok(self):
        self.keySave()

    def keySave(self):
        for x in self['config'].list:
            x[1].save()

        configfile.save()
        self.close()


class SL_Settings():

    def __init__(self):
        self.providers = []
        self.providersT = []
        self.services = []
        self.servicesT = []

    def read(self, pwd):
        self.providers = []
        self.services = []
        try:
            f = open(pwd + '/lamedb')
        except Exception as e:
            print e
            return

        while True:
            line = f.readline()
            if line == '':
                return
            line = line.strip()
            if line == 'transponders':
                break

        while True:
            line = f.readline()
            if line == '':
                return
            line = line.strip()
            if line == 'end':
                break
            line2 = f.readline().strip()
            line3 = f.readline().strip()
            self.providers.append([line.split(':'), line2.split(':'), line3.split(':')])

        while True:
            line = f.readline()
            if line == '':
                return
            line = line.strip()
            if line == 'services':
                break

        while True:
            line = f.readline()
            if line == '':
                return
            line = line.strip()
            if line == 'end':
                break
            line2 = f.readline().strip('\n')
            line3 = f.readline().strip('\n')
            self.services.append([line.split(':'), line2.split(':'), line3.split(':')])

        f.close()

    def write(self, pwd):
        try:
            f = open(pwd + '/lamedb', 'w')
        except Exception as e:
            print e
            return

        f.write('eDVB services /4/\n')
        f.write('transponders\n')
        for provider in self.providers:
            f.write(':'.join(provider[0]) + '\n')
            f.write('\t' + ':'.join(provider[1]) + '\n')
            f.write(':'.join(provider[2]) + '\n')

        f.write('end\n')
        f.write('services\n')
        for service in self.services:
            f.write(':'.join(service[0]) + '\n')
            f.write(':'.join(service[1]) + '\n')
            f.write(':'.join(service[2]) + '\n')

        f.write('end\n')
        f.write('Have a lot of bugs!\n')
        f.close()

    def saveTerrestrial(self):
        providersT = []
        servicesT = []
        for provider in self.providers:
            if provider[1][0][:1] == 't':
                providersT.append(provider)

        for service in self.services:
            for provider in providersT:
                if service[0][1] == provider[0][0] and service[0][2] == provider[0][1] and service[0][3] == provider[0][2]:
                    servicesT.append(service)

        self.providersT = providersT
        self.servicesT = servicesT

    def restoreTerrestrial(self):
        tmp = self.providersT
        for provider in self.providers:
            if provider[1][0][:1] != 't':
                tmp.append(provider)

        self.providers = tmp
        tmp = self.servicesT
        for service in self.services:
            if service[0][1][:4] != 'eeee':
                tmp.append(service)

        self.services = tmp

    def readBouquetsTvList(self, pwd):
        return self.readBouquetsList(pwd, 'bouquets.tv')

    def readBouquetsRadioList(self, pwd):
        return self.readBouquetsList(pwd, 'bouquets.radio')

    def readBouquetsList(self, pwd, bouquetname):
        try:
            f = open(pwd + '/' + bouquetname)
        except Exception as e:
            print e
            return

        ret = []
        while True:
            line = f.readline()
            if line == '':
                break
            if line[:8] != '#SERVICE':
                continue
            tmp = line.strip().split(':')
            line = tmp[len(tmp) - 1]
            filename = None
            if line[:12] == 'FROM BOUQUET':
                tmp = line[13:].split(' ')
                filename = tmp[0].strip('"')
            else:
                filename = line
            if filename:
                try:
                    fb = open(pwd + '/' + filename)
                except Exception as e:
                    print e
                    continue

                tmp = fb.readline().strip()
                if tmp[:6] == '#NAME ':
                    ret.append([filename, tmp[6:]])
                else:
                    ret.append([filename, filename])
                fb.close()

        return ret

    def copyBouquetsTv(self, srcpwd, dstpwd, keeplist):
        return self.copyBouquets(srcpwd, dstpwd, 'bouquets.tv', keeplist)

    def copyBouquetsRadio(self, srcpwd, dstpwd, keeplist):
        return self.copyBouquets(srcpwd, dstpwd, 'bouquets.radio', keeplist)

    def copyBouquets(self, srcpwd, dstpwd, bouquetname, keeplist):
        srclist = self.readBouquetsList(srcpwd, bouquetname)
        dstlist = self.readBouquetsList(dstpwd, bouquetname)
        if srclist is None:
            srclist = []
        if dstlist is None:
            dstlist = []
        count = 0
        for item in dstlist:
            if item[0] in keeplist:
                found = False
                for x in srclist:
                    if x[0] == item[0]:
                        found = True
                        break

                if not found:
                    srclist.insert(count, item)
            else:
                os.remove(dstpwd + '/' + item[0])
            count += 1

        for x in srclist:
            if x[0] not in keeplist:
                try:
                    os.copyfile(srcpwd + '/' + x[0], dstpwd + '/' + x[0])
                except:
                    pass

        try:
            f = open(dstpwd + '/' + bouquetname, 'w')
        except Exception as e:
            print e
            return

        if bouquetname[-3:] == '.tv':
            f.write('#NAME Bouquets (TV)\n')
        else:
            f.write('#NAME Bouquets (Radio)\n')
        for x in srclist:
            if bouquetname[-3:] == '.tv':
                f.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + x[0] + '" ORDER BY bouquet\n')
            else:
                f.write('#SERVICE 1:7:2:0:0:0:0:0:0:0:FROM BOUQUET "' + x[0] + '" ORDER BY bouquet\n')

        return

    def apply(self):
        if config.plugins.settingsloader.updatebouqeuts.value == 'yes':
            print 'ok delete old bq m3'
            copyfile(TMP_SETTINGS_PWD + '/lamedb', ENIGMA2_SETTINGS_PWD + '/lamedb')
            if config.plugins.settingsloader.keepsatellitesxml.value == False:
                print 'ok delete old bq m3'
                copyfile(TMP_SETTINGS_PWD + '/satellites.xml', ENIGMA2_TUXBOX_PWD + '/satellites.xml')
            eDVBDB.getInstance().reloadServicelist()
            eDVBDB.getInstance().reloadBouquets()
            return
        if config.plugins.settingsloader.keepterrestrial.value:
            self.read(ENIGMA2_SETTINGS_PWD)
            self.saveTerrestrial()
            self.read(TMP_SETTINGS_PWD)
            self.restoreTerrestrial()
            self.write(ENIGMA2_SETTINGS_PWD)
            keeplist = config.plugins.settingsloader.keepbouquets.value.split('|')
        else:
            self.read(TMP_SETTINGS_PWD)
            self.write(ENIGMA2_SETTINGS_PWD)
        if config.plugins.settingsloader.updatebouqeuts.value == 'select':
            keeplist = config.plugins.settingsloader.keepbouquets.value.split('|')
        else:
            keeplist = []
        self.copyBouquets(TMP_SETTINGS_PWD, ENIGMA2_SETTINGS_PWD, 'bouquets.tv', keeplist)
        self.copyBouquets(TMP_SETTINGS_PWD, ENIGMA2_SETTINGS_PWD, 'bouquets.radio', keeplist)
        if not config.plugins.settingsloader.keepsatellitesxml.value:
            try:
                copyfile(TMP_SETTINGS_PWD + '/satellites.xml', ENIGMA2_TUXBOX_PWD + '/satellites.xml')
            except Exception as e:
                print e

        if not config.plugins.settingsloader.keepcablesxml.value:
            try:
                copyfile(TMP_SETTINGS_PWD + '/cables.xml', ENIGMA2_TUXBOX_PWD + '/cables.xml')
            except Exception as e:
                print e

        if not config.plugins.settingsloader.keepterrestrialxml.value:
            try:
                copyfile(TMP_SETTINGS_PWD + '/terrestrial.xml', ENIGMA2_TUXBOX_PWD + '/terrestrial.xml')
            except Exception as e:
                print e

        try:
            copyfile(TMP_SETTINGS_PWD + '/whitelist', ENIGMA2_SETTINGS_PWD + '/whitelist')
        except Exception as e:
            print e

        try:
            copyfile(TMP_SETTINGS_PWD + '/blacklist', ENIGMA2_SETTINGS_PWD + '/blacklist')
        except Exception as e:
            print e

        eDVBDB.getInstance().reloadServicelist()
        eDVBDB.getInstance().reloadBouquets()


class SL_Deflate():

    def __init__(self):
        pass

    def deflatebz(self, filename):
        try:
            dirsremove(TMP_SETTINGS_PWD)
        except:
            pass

        try:
            os.mkdir(TMP_SETTINGS_PWD)
        except:
            pass

        Console().ePopen("tar -xjvf %s -C %s" % (filename, TMP_SETTINGS_PWD))
        Console().ePopen("cd %s && find -type f -exec mv {} . \\;" % TMP_SETTINGS_PWD)

    def deflatezip(self, filename):
        try:
            dirsremove(TMP_SETTINGS_PWD)
        except:
            pass

        try:
            os.mkdir(TMP_SETTINGS_PWD)
        except:
            pass

        Console().ePopen("unzip -o %s -d %s" % (filename, TMP_SETTINGS_PWD))
        Console().ePopen("cd %s && find -type f -exec mv {} . \\;" % TMP_SETTINGS_PWD)

    def deflateTar(self, filename):
        try:
            dirsremove(TMP_SETTINGS_PWD)
        except:
            pass

        try:
            os.mkdir(TMP_SETTINGS_PWD)
        except:
            pass

        Console().ePopen("tar zxf %s -C %s" % (filename, TMP_SETTINGS_PWD))
        Console().ePopen("cd %s && find -type f -exec mv {} . \\;" % TMP_SETTINGS_PWD)

    def deflateIpk(self, filename):
        try:
            dirsremove(TMP_SETTINGS_PWD)
        except:
            pass

        try:
            os.mkdir(TMP_SETTINGS_PWD)
        except:
            pass

        Console().ePopen("cp %s %s/tmp.ipk" % (filename, TMP_SETTINGS_PWD))
        Console().ePopen("cd %s && ar -x tmp.ipk" % TMP_SETTINGS_PWD)
        Console().ePopen("tar zxf %s/data.tar.gz -C %s" % (TMP_SETTINGS_PWD, TMP_SETTINGS_PWD))
        Console().ePopen("cd %s && find -type f -exec mv {} . \\;" % TMP_SETTINGS_PWD)

    def deflate(self, filename):
        if filename.endswith('.tar.bz2') or filename.endswith('.tbz2') or filename.endswith('.tbz'):
            self.deflatebz(filename)
        elif filename[-7:] == '.tar.gz' or filename[-8:] == '.tgz':
            self.deflateTar(filename)
        elif filename[-4:] == '.ipk':
            self.deflateIpk(filename)
        elif filename[-4:] == '.zip':
            self.deflatezip(filename)
        else:
            return False
        return True


class PurePrestigeSL_ActionBox(Screen):
    skin = '\n\t\t<screen position="center,center" size="560,70" title=" ">\n\n                        <widget alphatest="on" name="logo" position="10,10" size="48,48" transparent="1" zPosition="2" backgroundColor="background" />\n\t\t\t<widget font="Regular;20" halign="center" name="message" position="10,10" size="538,48" valign="center" foregroundColor="foreground" backgroundColor="background" transparent="1" zPosition="2" />\n\t\t</screen>'

    def __init__(self, session, message, title, action):
        Screen.__init__(self, session)
        self.session = session
        self.ctitle = title
        self.caction = action
        self['message'] = Label(message)
        self['logo'] = Pixmap()
        self.timer = eTimer()
        self.timer.callback.append(self.__setTitle)
        self.timer.start(200, 1)

    def __setTitle(self):
        if self['logo'].instance is not None:
            self['logo'].instance.setPixmapFromFile(os.path.dirname(sys.modules[__name__].__file__) + '/images/download.png')
        self.setTitle(self.ctitle)
        self.timer = eTimer()
        self.timer.callback.append(self.__start)
        self.timer.start(200, 1)
        return

    def __start(self):
        self.close(self.caction())


class SL_Settings():

    def __init__(self):
        self.providers = []
        self.providersT = []
        self.services = []
        self.servicesT = []

    def read(self, pwd):
        self.providers = []
        self.services = []
        try:
            f = open(pwd + '/lamedb')
        except Exception as e:
            print e
            return

        while True:
            line = f.readline()
            if line == '':
                return
            line = line.strip()
            if line == 'transponders':
                break

        while True:
            line = f.readline()
            if line == '':
                return
            line = line.strip()
            if line == 'end':
                break
            line2 = f.readline().strip()
            line3 = f.readline().strip()
            self.providers.append([line.split(':'), line2.split(':'), line3.split(':')])

        while True:
            line = f.readline()
            if line == '':
                return
            line = line.strip()
            if line == 'services':
                break

        while True:
            line = f.readline()
            if line == '':
                return
            line = line.strip()
            if line == 'end':
                break
            line2 = f.readline().strip('\n')
            line3 = f.readline().strip('\n')
            self.services.append([line.split(':'), line2.split(':'), line3.split(':')])

        f.close()

    def write(self, pwd):
        try:
            f = open(pwd + '/lamedb', 'w')
        except Exception as e:
            print e
            return

        f.write('eDVB services /4/\n')
        f.write('transponders\n')
        for provider in self.providers:
            f.write(':'.join(provider[0]) + '\n')
            f.write('\t' + ':'.join(provider[1]) + '\n')
            f.write(':'.join(provider[2]) + '\n')

        f.write('end\n')
        f.write('services\n')
        for service in self.services:
            f.write(':'.join(service[0]) + '\n')
            f.write(':'.join(service[1]) + '\n')
            f.write(':'.join(service[2]) + '\n')

        f.write('end\n')
        f.write('Have a lot of bugs!\n')
        f.close()

    def saveTerrestrial(self):
        providersT = []
        servicesT = []
        for provider in self.providers:
            if provider[1][0][:1] == 't':
                providersT.append(provider)

        for service in self.services:
            for provider in providersT:
                if service[0][1] == provider[0][0] and service[0][2] == provider[0][1] and service[0][3] == provider[0][2]:
                    servicesT.append(service)

        self.providersT = providersT
        self.servicesT = servicesT

    def restoreTerrestrial(self):
        tmp = self.providersT
        for provider in self.providers:
            if provider[1][0][:1] != 't':
                tmp.append(provider)

        self.providers = tmp
        tmp = self.servicesT
        for service in self.services:
            if service[0][1][:4] != 'eeee':
                tmp.append(service)

        self.services = tmp

    def readBouquetsTvList(self, pwd):
        return self.readBouquetsList(pwd, 'bouquets.tv')

    def readBouquetsRadioList(self, pwd):
        return self.readBouquetsList(pwd, 'bouquets.radio')

    def readBouquetsList(self, pwd, bouquetname):
        try:
            f = open(pwd + '/' + bouquetname)
        except Exception as e:
            print e
            return

        ret = []
        while True:
            line = f.readline()
            if line == '':
                break
            if line[:8] != '#SERVICE':
                continue
            tmp = line.strip().split(':')
            line = tmp[len(tmp) - 1]
            filename = None
            if line[:12] == 'FROM BOUQUET':
                tmp = line[13:].split(' ')
                filename = tmp[0].strip('"')
            else:
                filename = line
            if filename:
                try:
                    fb = open(pwd + '/' + filename)
                except Exception as e:
                    print e
                    continue

                tmp = fb.readline().strip()
                if tmp[:6] == '#NAME ':
                    ret.append([filename, tmp[6:]])
                else:
                    ret.append([filename, filename])
                fb.close()

        return ret

    def copyBouquetsTv(self, srcpwd, dstpwd, keeplist):
        return self.copyBouquets(srcpwd, dstpwd, 'bouquets.tv', keeplist)

    def copyBouquetsRadio(self, srcpwd, dstpwd, keeplist):
        return self.copyBouquets(srcpwd, dstpwd, 'bouquets.radio', keeplist)

    def copyBouquets(self, srcpwd, dstpwd, bouquetname, keeplist):
        srclist = self.readBouquetsList(srcpwd, bouquetname)
        dstlist = self.readBouquetsList(dstpwd, bouquetname)
        if srclist is None:
            srclist = []
        if dstlist is None:
            dstlist = []
        count = 0
        for item in dstlist:
            if item[0] in keeplist:
                found = False
                for x in srclist:
                    if x[0] == item[0]:
                        found = True
                        break

                if not found:
                    srclist.insert(count, item)
            else:
                os.remove(dstpwd + '/' + item[0])
            count += 1

        for x in srclist:
            if x[0] not in keeplist:
                try:
                    copyfile(srcpwd + '/' + x[0], dstpwd + '/' + x[0])
                except:
                    pass

        try:
            f = open(dstpwd + '/' + bouquetname, 'w')
        except Exception as e:
            print e
            return

        if bouquetname[-3:] == '.tv':
            f.write('#NAME Bouquets (TV)\n')
        else:
            f.write('#NAME Bouquets (Radio)\n')
        for x in srclist:
            if bouquetname[-3:] == '.tv':
                f.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + x[0] + '" ORDER BY bouquet\n')
            else:
                f.write('#SERVICE 1:7:2:0:0:0:0:0:0:0:FROM BOUQUET "' + x[0] + '" ORDER BY bouquet\n')

        return

    def apply(self):
        if config.plugins.settingsloader.updatebouqeuts.value == 'yes':
            copyfile(TMP_SETTINGS_PWD + '/lamedb', ENIGMA2_SETTINGS_PWD + '/lamedb')
            if config.plugins.settingsloader.keepsatellitesxml.value == False:
                copyfile(TMP_SETTINGS_PWD + '/satellites.xml', ENIGMA2_TUXBOX_PWD + '/satellites.xml')
            eDVBDB.getInstance().reloadServicelist()
            eDVBDB.getInstance().reloadBouquets()
            return
        if config.plugins.settingsloader.keepterrestrial.value:
            self.read(ENIGMA2_SETTINGS_PWD)
            self.saveTerrestrial()
            self.read(TMP_SETTINGS_PWD)
            self.restoreTerrestrial()
            self.write(ENIGMA2_SETTINGS_PWD)
            keeplist = config.plugins.settingsloader.keepbouquets.value.split('|')
        else:
            self.read(TMP_SETTINGS_PWD)
            self.write(ENIGMA2_SETTINGS_PWD)
            keeplist = []
        if config.plugins.settingsloader.updatebouqeuts.value == 'select':
            keeplist = config.plugins.settingsloader.keepbouquets.value.split('|')
        else:
            keeplist = []
        self.copyBouquets(TMP_SETTINGS_PWD, ENIGMA2_SETTINGS_PWD, 'bouquets.tv', keeplist)
        self.copyBouquets(TMP_SETTINGS_PWD, ENIGMA2_SETTINGS_PWD, 'bouquets.radio', keeplist)
        if not config.plugins.settingsloader.keepsatellitesxml.value:
            try:
                copyfile(TMP_SETTINGS_PWD + '/satellites.xml', ENIGMA2_TUXBOX_PWD + '/satellites.xml')
            except Exception as e:
                print e

        if not config.plugins.settingsloader.keepcablesxml.value:
            try:
                copyfile(TMP_SETTINGS_PWD + '/cables.xml', ENIGMA2_TUXBOX_PWD + '/cables.xml')
            except Exception as e:
                print e

        if not config.plugins.settingsloader.keepterrestrialxml.value:
            try:
                copyfile(TMP_SETTINGS_PWD + '/terrestrial.xml', ENIGMA2_TUXBOX_PWD + '/terrestrial.xml')
            except Exception as e:
                print e

        try:
            copyfile(TMP_SETTINGS_PWD + '/whitelist', ENIGMA2_SETTINGS_PWD + '/whitelist')
        except Exception as e:
            print e

        try:
            copyfile(TMP_SETTINGS_PWD + '/blacklist', ENIGMA2_SETTINGS_PWD + '/blacklist')
        except Exception as e:
            print e

        eDVBDB.getInstance().reloadServicelist()
        eDVBDB.getInstance().reloadBouquets()


class SL_MorpheusHelper():

    def __init__(self, session):
        self.session = session

    def download(self):
        self.loaded = True
        self.list = []
        try:
            conn = httplib.HTTPConnection(MORPHEUS_HOST)
            conn.request('GET', MORPHEUS_PATH + 'morph883.xml')
            httpres = conn.getresponse()
            if httpres.status == 200:
                mdom = xml.etree.cElementTree.parse(httpres)
                root = mdom.getroot()
                for node in root:
                    if node.tag == 'package':
                        sat = node.text
                        date = node.get('date')
                        print date[:4]
                        print date[4:6]
                        print date[-2:]
                        date = datetime.date(int(date[:4]), int(date[4:6]), int(date[-2:]))
                        date = date.strftime('%d %b')
                        url = 'http://' + MORPHEUS_HOST + MORPHEUS_PATH + node.get('filename')
                        self.list.append([sat, date, url])

            else:
                self.session.open(MessageBox, _('Cannot download morpheus883 list'), MessageBox.TYPE_ERROR)
                self.loaded = False
        except Exception as e:
            print e
            self.session.open(MessageBox, _('Cannot download morpheus883 list'), MessageBox.TYPE_ERROR)
            self.loaded = False

    def load(self):
        self.session.openWithCallback(self.show, PurePrestigeSL_ActionBox, _('Downloading morpheus883 list'), _('Downloading ...'), self.download)

    def show(self, ret = None):
        if self.loaded:
            self.session.open(PurePrestigeSL_Morpheus, self.list)


class PurePrestigeSL_Morpheus(PurePrestigeSL_SettingsList):
    skin = '\n\t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520" transparent="1"/>\t\n\n                <ePixmap position="15,440" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n                                <widget source="list" render="Listbox" position="15,20" size="610,400" scrollbarMode="showOnDemand" transparent="1" zPosition="2" >\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\tMultiContentEntryText(pos = (10, 5), size = (440, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 0),\n\t\t\t\t\t\tMultiContentEntryText(pos = (480, 5), size = (130, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),\n\t\t\t\t\t\t],\n\t\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t\t"itemHeight": 40\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t\n\t\t\t\n\t\t\t\n\t\t\t<widget name="key_yellow" position="270,460" size="140,20" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>\n\t\t\t\n\t\t\t\n\t\t\t\n\t\t\t<ePixmap name="yellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" position="270,450" size="140,40" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\n\t\t</screen>'

    def __init__(self, session, list):
        PurePrestigeSL_SettingsList.__init__(self, session, list, 'MORPHEUS-settings')


class SL_VhannibalHelper():

    def __init__(self, session):
        self.session = session

    def download(self):
        self.loaded = True
        self.list = []
        try:
            conn = httplib.HTTPConnection(VHANNIBAL_HOST)
            conn.request('GET', VHANNIBAL_PATH + 'lista.xml')
            httpres = conn.getresponse()
            if httpres.status == 200:
                mdom = xml.etree.cElementTree.parse(httpres)
                root = mdom.getroot()
                for node in root:
                    if node.tag == 'MAIN':
                        sat = ''
                        date = ''
                        url = ''
                        for x in node:
                            if x.tag == 'SAT':
                                sat = str(x.text)
                            elif x.tag == 'DATE':
                                date = x.text
                            elif x.tag == 'URL':
                                url = x.text

                        self.list.append([sat, date, url])

            else:
                self.session.open(MessageBox, _('Cannot download VHANNIBAL list'), MessageBox.TYPE_ERROR)
                self.loaded = False
        except Exception as e:
            print e
            self.session.open(MessageBox, _('Cannot download VHANNIBAL list'), MessageBox.TYPE_ERROR)
            self.loaded = False

    def load(self):
        self.session.openWithCallback(self.show, PurePrestigeSL_ActionBox, _('Downloading VHANNIBAL list'), _('Downloading ...'), self.download)

    def show(self, ret = None):
        if self.loaded:
            self.session.open(PurePrestigeSL_Vhanibbal, self.list)


class PurePrestigeSL_Vhanibbal(PurePrestigeSL_SettingsList):
    skin = '\n\t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520" transparent="1"/>\t\n\n                <ePixmap position="15,440" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n                                <widget source="list" render="Listbox" position="15,20" size="610,400" scrollbarMode="showOnDemand" transparent="1" zPosition="2" >\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\tMultiContentEntryText(pos = (10, 5), size = (440, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 0),\n\t\t\t\t\t\tMultiContentEntryText(pos = (480, 5), size = (130, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),\n\t\t\t\t\t\t],\n\t\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t\t"itemHeight": 40\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t\n\t\t\t\n\t\t\t\n\t\t\t<widget name="key_yellow" position="270,460" size="140,20" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>\n\t\t\t\n\t\t\t\n\t\t\t\n\t\t\t<ePixmap name="yellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" position="270,450" size="140,40" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\n\t\t</screen>'

    def __init__(self, session, list):
        PurePrestigeSL_SettingsList.__init__(self, session, list)


class SL_SettingsHelper():

    def __init__(self, session, settings_host = None, settings_path = None, title = None, xmlname = None):
        self.session = session
        self.path = settings_path
        self.host = settings_host
        self.title = title
        self.xml = xmlname

    def download(self):
        self.loaded = True
        self.list = []
        try:
            conn = httplib.HTTPConnection(self.host)
            conn.request('GET', self.path + self.xml)
            httpres = conn.getresponse()
            if httpres.status == 200:
                mdom = xml.etree.cElementTree.parse(httpres)
                root = mdom.getroot()
                for node in root:
                    if node.tag == 'MAIN':
                        sat = ''
                        date = ''
                        url = ''
                        for x in node:
                            if x.tag == 'SAT':
                                sat = str(x.text)
                            elif x.tag == 'DATE':
                                date = x.text
                            elif x.tag == 'URL':
                                url = x.text

                        self.list.append([sat, date, url])

                if self.list == []:
                    self.session.open(MessageBox, _('Cannot download settings list'), MessageBox.TYPE_ERROR)
                    self.loaded = False
            else:
                self.session.open(MessageBox, _('Cannot download settings list'), MessageBox.TYPE_ERROR)
                self.loaded = False
        except Exception as e:
            print e
            self.session.open(MessageBox, _('Cannot download settings list'), MessageBox.TYPE_ERROR)
            self.loaded = False

    def load(self):
        self.session.openWithCallback(self.show, PurePrestigeSL_ActionBox, _('Downloading settings list'), _('Downloading ...'), self.download)

    def show(self, ret = None):
        if self.loaded:
            self.session.open(PurePrestigeSL_Settingsshow, self.list, self.title)


class PurePrestigeSL_Settingsshow(PurePrestigeSL_SettingsList):
    skin = '\n\t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520" transparent="1"/>\t\n\n                <ePixmap position="15,440" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n                                <widget source="list" render="Listbox" position="15,20" size="610,400" scrollbarMode="showOnDemand" transparent="1" zPosition="2" >\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\tMultiContentEntryText(pos = (10, 5), size = (440, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 0),\n\t\t\t\t\t\tMultiContentEntryText(pos = (480, 5), size = (130, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),\n\t\t\t\t\t\t],\n\t\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t\t"itemHeight": 40\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t\n\t\t\t\n\t\t\t\n\t\t\t<widget name="key_yellow" position="270,460" size="140,20" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>\n\t\t\t\n\t\t\t\n\t\t\t\n\t\t\t<ePixmap name="yellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" position="270,450" size="140,40" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\n\t\t</screen>'

    def __init__(self, session, list, title):
        PurePrestigeSL_SettingsList.__init__(self, session, list, title)


class SL_CyrusHelper():

    def __init__(self, session):
        self.session = session

    def download(self):
        self.loaded = True
        self.list = []
        try:
            conn = httplib.HTTPConnection(CYRUS_HOST)
            conn.request('GET', CYRUS_PATH + 'lista.xml')
            httpres = conn.getresponse()
            if httpres.status == 200:
                mdom = xml.etree.cElementTree.parse(httpres)
                root = mdom.getroot()
                for node in root:
                    if node.tag == 'MAIN':
                        sat = ''
                        date = ''
                        url = ''
                        for x in node:
                            if x.tag == 'SAT':
                                sat = x.text
                            elif x.tag == 'DATE':
                                date = x.text
                            elif x.tag == 'URL':
                                url = x.text

                        self.list.append([sat, date, url])

            else:
                self.session.open(MessageBox, _('Cannot download cyrus list'), MessageBox.TYPE_ERROR)
                self.loaded = False
        except Exception as e:
            print e
            self.session.open(MessageBox, _('Cannot download cyrus list'), MessageBox.TYPE_ERROR)
            self.loaded = False

    def load(self):
        self.session.openWithCallback(self.show, PurePrestigeSL_ActionBox, _('Downloading cyrus list'), _('Downloading ...'), self.download)

    def show(self, ret = None):
        if self.loaded:
            self.session.open(PurePrestigeSL_Cyrus, self.list)


class PurePrestigeSL_Cyrus(PurePrestigeSL_SettingsList):
    skin = '\n\t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520" transparent="1"/>\t\n\n                <ePixmap position="15,440" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n                                <widget source="list" render="Listbox" position="15,20" size="610,400" scrollbarMode="showOnDemand" transparent="1" zPosition="2" >\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\tMultiContentEntryText(pos = (10, 5), size = (440, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 0),\n\t\t\t\t\t\tMultiContentEntryText(pos = (480, 5), size = (130, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),\n\t\t\t\t\t\t],\n\t\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t\t"itemHeight": 40\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t\n\t\t\t\n\t\t\t\n\t\t\t<widget name="key_yellow" position="270,460" size="140,20" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>\n\t\t\t\n\t\t\t\n\t\t\t\n\t\t\t<ePixmap name="yellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" position="270,450" size="140,40" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\n\t\t</screen>'

    def __init__(self, session, list):
        PurePrestigeSL_SettingsList.__init__(self, session, list)


class SL_SamiHelper():

    def __init__(self, session):
        self.session = session

    def download(self):
        self.loaded = True
        self.list = []
        try:
            conn = httplib.HTTPConnection(SAMI73_HOST)
            conn.request('GET', SAMI73_PATH + 'lista.xml')
            httpres = conn.getresponse()
            if httpres.status == 200:
                mdom = xml.etree.cElementTree.parse(httpres)
                root = mdom.getroot()
                for node in root:
                    if node.tag == 'MAIN':
                        sat = ''
                        date = ''
                        url = ''
                        for x in node:
                            if x.tag == 'SAT':
                                sat = x.text
                            elif x.tag == 'DATE':
                                date = x.text
                            elif x.tag == 'URL':
                                url = x.text

                        self.list.append([sat, date, url])

            else:
                self.session.open(MessageBox, _('Cannot download cyrus list'), MessageBox.TYPE_ERROR)
                self.loaded = False
        except Exception as e:
            print e
            self.session.open(MessageBox, _('Cannot download cyrus list'), MessageBox.TYPE_ERROR)
            self.loaded = False

    def load(self):
        self.session.openWithCallback(self.show, PurePrestigeSL_ActionBox, _('Downloading cyrus list'), _('Downloading ...'), self.download)

    def show(self, ret = None):
        if self.loaded:
            self.session.open(PurePrestigeSL_Sami, self.list)


class PurePrestigeSL_Sami(PurePrestigeSL_SettingsList):
    skin = '\n\t\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520" transparent="1"/>\t\n\n                <ePixmap position="15,440" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n                                <widget source="list" render="Listbox" position="15,20" size="610,400" scrollbarMode="showOnDemand" transparent="1" zPosition="2" >\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\tMultiContentEntryText(pos = (10, 5), size = (440, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 0),\n\t\t\t\t\t\tMultiContentEntryText(pos = (480, 5), size = (130, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),\n\t\t\t\t\t\t],\n\t\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t\t"itemHeight": 40\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t\n\t\t\t\n\t\t\t\n\t\t\t<widget name="key_yellow" position="270,460" size="140,20" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>\n\t\t\t\n\t\t\t\n\t\t\t\n\t\t\t<ePixmap name="yellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" position="270,450" size="140,40" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\n\t\t</screen>'

    def __init__(self, session, list):
        PurePrestigeSL_SettingsList.__init__(self, session, list)


class PurePrestigeSL_KeepBouquets(Screen):
    skin = '\n                <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520" transparent="1"/>\t\n\n                <ePixmap position="15,460" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\n                                <widget source="list" render="Listbox" position="20,15" size="600,440" scrollbarMode="showOnDemand" transparent="1" zPosition="2" >\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\tMultiContentEntryText(pos = (70, 5), size = (360, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),\n\t\t\t\t\t\tMultiContentEntryText(pos = (430, 5), size = (150, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 2),\n\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos = (3, 3), size = (64, 64), png = 0), # Icon\n\n\t\t\t\t\t\t],\n\t\t\t\t\t\t"fonts": [gFont("Regular", 22)],\n\t\t\t\t\t\t"itemHeight": 40\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t\n\t\t\t\n\t\t\t\n\t\t\t<widget name="key_blue" position="210,475" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>\n\t\t\t\n\t\t\t\n\t\t\t\n\t\t\t<ePixmap name="blue" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/blue.png" position="210,470" size="140,40" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.drawList = []
        self['list'] = List(self.drawList)
        self['key_blue'] = Button(_('Save'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok': self.ok,
         'blue': self.saveconfig,
         'cancel': self.quit}, -2)
        self.refresh()

    def buildListEntry(self, enabled, name, type):
        if enabled:
            pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, '/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/lock_on.png'))
        else:
            pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, '/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/lock_off.png'))
        return (pixmap, name, type)

    def refresh(self):
        settings = SL_Settings()
        self.listTv = settings.readBouquetsTvList(ENIGMA2_SETTINGS_PWD)
        self.listRadio = settings.readBouquetsRadioList(ENIGMA2_SETTINGS_PWD)
        self.drawList = []
        self.listAll = []
        self.bouquets = config.plugins.settingsloader.keepbouquets.value.split('|')
        if self.listTv is not None and self.listRadio is not None:
            for x in self.listTv:
                if x[0] in self.bouquets:
                    self.drawList.append(self.buildListEntry(True, str(x[1]), 'TV'))
                else:
                    self.drawList.append(self.buildListEntry(False, str(x[1]), 'TV'))
                self.listAll.append(x)

            for x in self.listRadio:
                if x[0] in self.bouquets:
                    self.drawList.append(self.buildListEntry(True, str(x[1]), 'Radio'))
                else:
                    self.drawList.append(self.buildListEntry(False, str(x[1]), 'Radio'))
                self.listAll.append(x)

        self['list'].setList(self.drawList)
        return

    def ok(self):
        if len(self.listAll) == 0:
            return
        index = self['list'].getIndex()
        name = str(self.drawList[index][1])
        typetv = str(self.drawList[index][2])
        if self.listAll[index][0] in self.bouquets:
            self.bouquets.remove(self.listAll[index][0])
            pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, '/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/lock_off.png'))
            self.drawList[index] = self.buildListEntry(False, name, typetv)
        else:
            self.bouquets.append(self.listAll[index][0])
            pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, '/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/lock_on.png'))
            self.drawList[index] = self.buildListEntry(True, name, typetv)
        config.plugins.settingsloader.keepbouquets.value = '|'.join(self.bouquets)
        self['list'].setList(self.drawList)
        self['list'].setIndex(index)

    def quit(self):
        self.close()

    def saveconfig(self):
        config.save()
        self.close()


class PurePrestigesettingsserver(Screen):
    skin = '\n                               <screen  position="center,center" size="640,520" title=""  flags="wfNoBorder" >\n                                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/framesd.png" position="0,0" size="640,520" transparent="1"/>\t\n\t\t\n                <ePixmap name="yellow" position="250,460" zPosition="4" size="180,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/ddbuttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t<widget name="key_yellow" position="230,465" zPosition="5" size="180,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n    \n                <widget name="list" position="15,60" size="610,348" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />\n                <ePixmap position="15,405" size="610,5" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/images/slider.png" alphatest="blend" transparent="1" backgroundColor="transparent"/>\t        \n        \n        </screen>'

    def __init__(self, session):
        self.skin = PurePrestigesettingsserver.skin
        Screen.__init__(self, session)
        self.serversnames = ['Morpheus883 settings', 'Vhannibal settings']
        self['key_yellow'] = Button(_('Settings'))
        self.list = []
        self['list'] = MenuList([], True, eListboxPythonMultiContent)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.openSelected,
         'yellow': self.showsettings,
         'cancel': self.close}, -2)
        self.ListToMulticontent()

    def ListToMulticontent(self):
        res = []
        theevents = []
        self.events = []
        self.events = self.serversnames
        self['list'].l.setItemHeight(58)
        self['list'].l.setFont(0, gFont('Regular', 23))
        for i in range(0, len(self.events)):
            res.append(MultiContentEntryText(pos=(0, 10), size=(2, 120), font=0, flags=RT_HALIGN_LEFT, text='', color=16777215, color_sel=16777215))
            res.append(MultiContentEntryText(pos=(60, 10), size=(430, 120), font=0, flags=RT_HALIGN_LEFT, text=self.events[i], color=16777215, color_sel=16777215))
            theevents.append(res)
            res = []

        self['list'].l.setList(theevents)
        self['list'].show()

    def showsettings(self):
        self.session.open(PurePrestigeSL_Setup)

    def openSelected(self):
        index = self['list'].getSelectionIndex()
        self.host = ''
        self.path = ''
        self.title = ''
        self.xml = 'lista.xml'
        if index == 0:
            SL_MorpheusHelper(self.session).load()
            return
            self.host = MORPHEUS_HOST
            self.path = MORPHEUS_PATH
            self.title = 'MORPHEUS_settings'
            self.xml = 'morph883.xml'
        elif index == 1:
            self.host = VHANNIBAL_HOST
            self.path = VHANNIBAL_PATH
            self.title = 'VHANNIBAL_settings'
        SL_SettingsHelper(self.session, self.host, self.path, self.title, self.xml).load()
        self.setTitle('PurePrestige-Settings loader')

    def okClicked(self):
        selectedserverurl = ''
        try:
            selection = self['list'].getCurrent()
            cindex = self['list'].getSelectionIndex()
        except:
            pass
