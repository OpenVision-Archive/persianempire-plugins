from Components.config import ConfigSubsection, ConfigText, ConfigYesNo, config
from Screens.MessageBox import MessageBox
from BaseMediaBackend import BaseMediaBackend
from enigma import eServiceCenter, eDVBVolumecontrol, eServiceReference, eTimer, getBoxType
import urllib2
from AirPlayMoviePlayer import AirPlayMoviePlayer
from AirPlayMusicPlayer import AirPlayMusicPlayer
from AirPlayPicturePlayer import AirPlayPicturePlayer

def isValidServiceId(idToTest):
    testSRef = eServiceReference(idToTest, 0, 'Just a TestReference')
    info = eServiceCenter.getInstance().info(testSRef)
    return info is not None


ENIGMA_SERVICEGS_ID = 4097
ENIGMA_SERVICEAP_ID = 4105
ENIGMA_SERVICEAZ_ID = 4370
ENIGMA_SERVICE_ID = 0
print '[AirPlayer] Checking for usable AzBox service ... '
if isValidServiceId(ENIGMA_SERVICEAZ_ID):
    print 'yes'
    ENIGMA_SERVICE_ID = ENIGMA_SERVICEAZ_ID
else:
    print 'no\n'
    print '[AirPlayer] Checking for usable gstreamer service ... '
    if isValidServiceId(ENIGMA_SERVICEGS_ID):
        print 'yes\n'
        ENIGMA_SERVICE_ID = ENIGMA_SERVICEGS_ID
    else:
        print 'no\n'
        print '[AirPlayer] No valid AirPlayer-Service found'

class E2MediaBackend(BaseMediaBackend):

    def __init__(self, session):
        global ENIGMA_SERVICE_ID
        print '[AirPlayer] init E2MediaBackEnd'
        super(E2MediaBackend, self).__init__()
        self.session = session
        self.sref = None
        self.MovieWindow = None
        self.PictureWindow = None
        self.MusicWindow = None
        self.onClose = []
        self.duration = 0.0
        self.playPosition = 0.0
        self.updateEventInfo = None
        self.downmix_ac3 = None
        if getBoxType().startswith('az'):
            ENIGMA_SERVICE_ID = ENIGMA_SERVICEAZ_ID
        print '[AirPlayer] using ServiceID: ', ENIGMA_SERVICE_ID
        self.ENIGMA_SERVICE_ID = ENIGMA_SERVICE_ID
        self.ENIGMA_SERVICEAZ_ID = ENIGMA_SERVICEAZ_ID
        self.ErrorTimer = eTimer()
        self.ErrorTimer.callback.append(self.showErrorMessage)
        self.validationMessage = ''
        return

    def showErrorMessage(self):
        print '[AirPlayer] showing validaten message ', self.validationMessage
        try:
            self.session.open(MessageBox, _(self.validationMessage), MessageBox.TYPE_INFO, timeout=10)
        except Exception as e:
            pass

    def setValidationMessage(self, message):
        if message == None or message == '':
            self.ErrorTimer.stop()
        else:
            self.validationMessage = message
            self.ErrorTimer.start(2000, True)
        return

    def setUpdateEventInfoFunc(self, func):
        self.updateEventInfo = func

    def cleanup(self):
        print '[AirPlayer] cleanup'
        self.stop_playing()

    def stop_playing(self):
        print '[AirPlayer] stop_playing'
        if self.MovieWindow is not None:
            self.MovieWindow.leavePlayer()
        if self.PictureWindow is not None:
            self.PictureWindow.leavePlayer()
        self.sref = None
        self.MovieWindow = None
        self.PictureWindow = None
        print '[AirPlayer] stop_playing done'
        return

    def show_picture(self, data):
        print '[AirPlayer] show_picture '
        if self.PictureWindow is not None:
            self.PictureWindow.start_decode()
        else:
            try:
                self.session.open(AirPlayPicturePlayer, self, config.plugins.airplayer.path.value + '/pic.jpg')
            except Exception as e:
                print ('Exception(Can be ignored): ' + str(e), __name__, 'W')

        return

    def play_airtunes(self, message):
        print '[AirPlayer] play AirTunes '
        lastservice = None
        if self.MusicWindow is not None:
            lastservice = self.MusicWindow.lastservice
            self.MusicWindow.leavePlayer()
        if self.MovieWindow is not None:
            lastservice = self.MovieWindow.lastservice
        try:
            self.session.open(AirPlayMusicPlayer, self, message, lastservice)
        except Exception as e:
            print ('Exception(Can be ignored): ' + str(e), __name__, 'W')

        return

    def updateAirTunesCover(self):
        print '[AirPlayer] updateAirTunesCover'
        if self.MusicWindow is not None:
            self.MusicWindow.start_decode()
        return

    def updateAirTunesProgress(self, seconds, runtime = None):
        print '[AirPlayer] updateAirTunesProgress'
        if self.MusicWindow is not None:
            self.MusicWindow.setProgress(seconds, runtime)
        return

    def updateAirTunesMetadata(self):
        print '[AirPlayer] updateAirTunesMetadata'
        if self.MusicWindow is not None:
            self.MusicWindow.parseMetadata()
        return

    def stop_airtunes(self):
        print '[AirPlayer] stop_airtunes'
        if self.MusicWindow is not None:
            self.MusicWindow.leavePlayer()
        self.MusicWindow = None
        return

    def play_movie(self, url, start = None):
        print '[AirPlayer] play_movie'
        self.setValidationMessage(None)
        if 'mov' in url.lower():
            print '[AirPlayer] mov found in url, fetching http headers'
            page = urllib2.urlopen(url)
            info = page.info()
            print info
            print '[AirPlayer] Content-Type:', info['Content-Type'], 'Content-Length:', info['Content-Length']
            if int(info['Content-Length']) < 10240:
                print '[AirPlayer] this might be some QuickTime forwarding be that gstreamer cant handle, so we are parsing it!'
                text = page.read()
                pos = text.find('http://')
                while pos > 0:
                    url = text[pos:].split('\x00', 1)[0]
                    pos = text.find('http://', pos + 1)
                    print 'new url', url, ' ', len(url)

            page.close()
        lastservice = None
        if self.MusicWindow is not None:
            print '[AirPlayer] MusicPlayer still open'
            lastservice = self.MusicWindow.lastservice
            print '[AirPlayer] lastService', lastservice
            self.MusicWindow.lastservice = None
        if self.MovieWindow is not None:
            print '[AirPlayer] MoviePlayer still open'
            lastservice = self.MovieWindow.lastservice
            print '[AirPlayer] lastService', lastservice
            self.MovieWindow.lastservice = None
            self.MovieWindow.leavePlayer()
        sref = eServiceReference(ENIGMA_SERVICE_ID, 0, url)
        sref.setName('AirPlay')
        self.sref = sref
        self.duration = 0.0
        self.playPosition = 0.0
        try:
            self.session.open(AirPlayMoviePlayer, sref, self, start, lastservice)
        except Exception as e:
            print ('Exception(Can be ignored): ' + str(e), __name__, 'W')
            if self.MusicWindow is not None:
                self.MusicWindow.lastservice = lastservice

        if self.MusicWindow is not None:
            self.MusicWindow.leavePlayer()
        return

    def notify_started(self):
        print '[AirPlayer] notify_started'
        print '[AirPlayer] Started connection to VLC'

    def pause(self):
        print '[AirPlayer] pause'
        if self.MovieWindow is not None:
            self.MovieWindow.setSeekState(self.MovieWindow.SEEK_STATE_PAUSE)
        return

    def play(self):
        print '[AirPlayer] play'
        if self.MovieWindow is not None:
            self.MovieWindow.setSeekState(self.MovieWindow.SEEK_STATE_PLAY)
        return

    def get_player_position(self):
        time = 0
        length = 0
        service = self.session.nav.getCurrentService()
        seek = service and service.seek()
        if seek != None:
            r = seek.getLength()
            if not r[0]:
                length = float(float(r[1]) / float(90000))
            r = seek.getPlayPosition()
            if not r[0]:
                time = float(float(r[1]) / float(90000))
        if time > 0 and length > 0:
            self.playPosition = time
            self.duration = length
            if time >= length - 2.5:
                print 'near end of file'
                if self.MovieWindow is not None:
                    self.MovieWindow.endReached = True
        else:
            self.playPosition = self.duration
        cachePos = self.playPosition
        if self.MovieWindow is not None:
            try:
                cachePos = float(self.duration / 100.0) * float(self.MovieWindow['bufferslider'].getValue())
                if cachePos < self.playPosition:
                    cachePos = self.playPosition
            except Exception as e:
                pass

        return (self.playPosition, self.duration, cachePos)

    def set_player_position(self, position):
        time, length, buffer = self.get_player_position()
        print '[AirPlayer] set_player_position: to:', position, ' from:', time, ' diff:', position - time
        if self.MovieWindow is not None:
            self.MovieWindow.setSeekState(self.MovieWindow.SEEK_STATE_PLAY)
            self.MovieWindow.doSeek(int(position * 90000))
        return

    def is_playing(self):
        if self.MovieWindow is not None:
            return self.MovieWindow.isPlaying()
        else:
            return False
            return

    def set_start_position(self, percentage_position):
        print '[AirPlayer] set_start_position: ', percentage_position

    def setVolume(self, value):
        if config.plugins.airplayer.allowiOSVolumeControl.value:
            print '[AirTunes] set Volume : ', value
            vcontrol = eDVBVolumecontrol.getInstance()
            if value < 0:
                value = 0
            if value > 100:
                value = 100
            vcontrol.setVolume(value, value)

    def setDownmix(self):
        self.downmix_ac3 = config.av.downmix_ac3.value
        config.av.downmix_ac3.value = True
        config.av.downmix_ac3.save()
