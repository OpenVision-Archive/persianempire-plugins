import enigma
from enigma import eTimer, eDVBCI_UI, eDVBCIInterfaces, iServiceInformation
from Plugins.Plugin import PluginDescriptor

autoStartTimer = None

def Plugins(**kwargs):
    return [PluginDescriptor(name='vusolo2 CI high bitrate fix', description='CI high bitrate fix for VuPlus Solo 2', where=PluginDescriptor.WHERE_SESSIONSTART, fnc=autostart)]


def autostart(reason, session = None):
    global autoStartTimer
    print '[VUSolo2CIHighBitrateFix] autostart'
    if reason == 0:
        if autoStartTimer is None:
            autoStartTimer = AutoStartTimer(session)
    return


class AutoStartTimer:
    ciCaids = []

    def __init__(self, session):
        self.session = session
        self.timer = enigma.eTimer()
        self.timer.callback.append(self.onTimer)
        self.timer.startLongTimer(2)

    def onTimer(self):
        try:
            state = eDVBCI_UI.getInstance().getState(0)
            if state == 0:
                self.timer.stop()
            elif state == 1:
                self.timer.startLongTimer(2)
            elif state == 2:
                self.ciCaids = eDVBCIInterfaces.getInstance().readCICaIds(0)
                if not self.ciCaids:
                    self.timer.startLongTimer(2)
                    return
                service = self.session.nav.getCurrentService()
                info = service and service.info()
                if service is None:
                    self.timer.startLongTimer(2)
                    return
                info = service and service.info()
                if not info:
                    self.timer.startLongTimer(2)
                    return
                serviceCaids = info.getInfoObject(iServiceInformation.sCAIDs)
                for serviceCaid in serviceCaids:
                    for ciCaid in self.ciCaids:
                        if ciCaid == serviceCaid:
                            eDVBCI_UI.getInstance().setClockRate(0, eDVBCI_UI.rateHigh)
                            self.timer.stop()
                            return

                self.timer.startLongTimer(2)
            else:
                self.timer.startLongTimer(2)
        except:
            self.timer.startLongTimer(2)

        return

    def debugLog(self, log):
        try:
            f = open('/tmp/VUSolo2CIHighBitrateFix.log', 'a')
            f.write(log + '\n')
            f.close()
        except:
            pass
