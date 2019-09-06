from enigma import eConsoleAppContainer, iServiceInformation
from Components.Console import Console

class Bitrate:

    def __init__(self, session, refresh_func = None, finished_func = None):
        self.session = session
        self.refresh_func = refresh_func
        self.finished_func = finished_func
        self.remainingdata = ''
        self.running = False
        self.clearValues()
        self.datalines = []
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.appClosed)
        self.container.dataAvail.append(self.dataAvail)

    def start(self):
        if self.running:
            return
        service = self.session.nav.getCurrentService()
        if service:
            demux = 2
            try:
                stream = service.stream()
                if stream:
                    streamdata = stream.getStreamingData()
                    if streamdata and 'demux' in streamdata:
                        demux = streamdata['demux']
            except:
                pass

            info = service.info()
            vpid = info.getInfo(iServiceInformation.sVideoPID)
            apid = info.getInfo(iServiceInformation.sAudioPID)
            cmd = 'bitrate '
            cmd += str(demux)
            cmd += ' '
            cmd += str(vpid)
            cmd += ' '
            cmd += str(apid)
            self.running = True
            self.container.execute(cmd)

    def clearValues(self):
        self.vmin = 0
        self.vmax = 0
        self.vavg = 0
        self.vcur = 0
        self.amin = 0
        self.amax = 0
        self.aavg = 0
        self.acur = 0

    def stop(self):
        Console().ePopen('killall -9 bitrate')
        self.container.kill()
        self.remainingdata = ''
        self.clearValues()
        self.running = False

    def appClosed(self, retval):
        self.remainingdata = ''
        self.clearValues()
        self.running = False
        if self.finished_func:
            self.finished_func(retval)

    def dataAvail(self, str):
        str = self.remainingdata + str
        newlines = str.split('\n')
        if len(newlines[-1]):
            self.remainingdata = newlines[-1]
            newlines = newlines[0:-1]
        else:
            self.remainingdata = ''
        for line in newlines:
            if len(line):
                self.datalines.append(line)

        if len(self.datalines) >= 2:
            try:
                self.vmin, self.vmax, self.vavg, self.vcur = self.datalines[0].split(' ')
                self.amin, self.amax, self.aavg, self.acur = self.datalines[1].split(' ')
                self.datalines = []
                if self.refresh_func:
                    self.refresh_func()
            except ValueError:
                print '[Bitrateviewer] No valid data grabbed.'
