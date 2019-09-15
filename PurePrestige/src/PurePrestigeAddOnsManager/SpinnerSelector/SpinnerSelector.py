from Plugins.Plugin import PluginDescriptor
from SpinnerSelectionBox import *
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.config import config
import os
import gettext
from Components.Console import Console

try:
    cat = gettext.translation('lang', '/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/PurePrestigeAddOnsManager/SpinnerSelector/po', [config.osd.language.getText()])
    _ = cat.gettext
except IOError:
    pass

class SpinnerSelector:

    def __init__(self, session):
        self.session = session
        pdir = 'Baby'
        defpath = '/usr/share/enigma2/Spinner/' + pdir
        if os.path.isdir(defpath):
            self.session.open(SpinnerSelectionBox, title=_('Chose Spinner'), pdir=pdir)

    def menuCallback(self, choice):
        if choice is None:
            return
        else:
            First = True
            for i in range(64):
                if os.path.isfile('/usr/share/enigma2/skin_default/spinner/wait%d.png' % (i + 1)):
                    Console().ePopen('rm -f /usr/share/enigma2/skin_default/spinner/wait%d.png' % (i + 1))
                if os.path.isfile('/usr/share/enigma2/Spinner/%s/wait%d.png' % (choice, i + 1)):
                    Console().ePopen('ln -s /usr/share/enigma2/Spinner/%s/wait%d.png /usr/share/enigma2/skin_default/spinner/wait%d.png' % (choice, i + 1, i + 1))
                    if First:
                        First = False
                        Console().ePopen('rm -f /usr/lib/enigma2/python/Plugins/Extensions/SpinnerSelektor/plugin.png; ln -s /usr/share/enigma2/Spinner/%s/wait%d.png /usr/lib/enigma2/python/Plugins/Extensions/SpinnerSelektor/plugin.png' % (choice, i + 1))

            self.session.openWithCallback(self.restart, MessageBox, _('GUI needs a restart to apply a new spinner.\nDo you want to restart the GUI now ?'), MessageBox.TYPE_YESNO)
            return

    def restart(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
