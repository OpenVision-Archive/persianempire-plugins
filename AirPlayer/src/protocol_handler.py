#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import appletv
import lib.biplist
from twisted.web.resource import Resource
from twisted.internet import reactor
from httputil import HTTPHeaders
from Components.config import config
from Components.Network import iNetwork
from websocket import WebSocketSite, WebSocketHandler
import os.path
from Tools import Notifications
from Screens.MessageBox import MessageBox
from ctypes import *

class AirplayProtocolHandler(object):

    def __init__(self, port, media_backend):
        self._http_server = None
        self._media_backend = media_backend
        self._port = port
        self.reverseRequest = None
        self.sessionID = 'dummy'
        self._media_backend.setUpdateEventInfoFunc(self.sendEventInfo)
        self.reverseHandler = None
        self.event = None
        return

    def start(self):
        try:
            root = Resource()
            root.putChild('play', PlayHandler(self._media_backend, self))
            root.putChild('scrub', ScrubHandler(self._media_backend, self))
            root.putChild('rate', RateHandler(self._media_backend, self))
            root.putChild('photo', PhotoHandler(self._media_backend, self))
            root.putChild('authorize', AuthorizeHandler(self._media_backend, self))
            root.putChild('server-info', ServerInfoHandler(self._media_backend, self))
            root.putChild('slideshow-features', SlideshowFeaturesHandler(self._media_backend, self))
            root.putChild('playback-info', PlaybackInfoHandler(self._media_backend, self))
            root.putChild('stop', StopHandler(self._media_backend, self))
            root.putChild('setProterpy', SetProterpyHandler(self._media_backend, self))
            root.putChild('getProterpy', GetProterpyHandler(self._media_backend, self))
            self.reverseHandler = ReverseHandler()
            site = WebSocketSite(root)
            site.addHandler('/reverse', self.reverseHandler)
            port = self._port
            reactor.listenTCP(port, site, interface='0.0.0.0')
        except Exception as ex:
            print(('Exception(Can be ignored): ' + str(ex), __name__, 'W'))

    def sendEventInfo(self, event):
        print('[AirPlayer] REVERSE /event - event=%s' % event)
        try:
            if self.reverseHandler is not None and self.reverseHandler.transport is not None:
                header_template = 'POST /event HTTP/1.1\r\nContent-Type: text/x-apple-plist+xml\r\nContent-Length: %s\r\nx-apple-session-id: %s\r\n'
                xml = appletv.EVENT_INFO % event
                header = header_template % (len(xml), self.sessionID)
                req = '%s\r\n%s\r\n' % (header, xml)
                self.reverseHandler.transport.write(req)
        except Exception as ex:
            print(('Exception(Can be ignored): ' + str(ex), __name__, 'W'))

        return


class ReverseHandler(WebSocketHandler):

    def frameReceived(self, frame):
        print('[AirPlayer] REVERSE frame : %s' % frame)

    def connectionLost(self, reason):
        print('[AirPlayer] REVERSE connection lost: %s' % reason)


class BaseHandler(Resource):

    def __init__(self, media_backend, protocolHandler):
        self._media_backend = media_backend
        self._protocolHandler = protocolHandler
        self._session_id = None
        return

    def render(self, request):
        self._session_id = request.getHeader('x-apple-session-id')
        if self._session_id == None:
            self._session_id = 'dummy'
        else:
            self._protocolHandler.sessionID = self._session_id
        request.responseHeaders.removeHeader('Content-Type')
        request.responseHeaders.removeHeader('Server')
        Resource.render(self, request)
        return 1


class PlayHandler(BaseHandler):

    def render_POST(self, request):
        print('[AirPlayer] PlayHandler POST')
        if request.getHeader('Content-Type') == 'application/x-apple-binary-plist':
            body = lib.biplist.readPlistFromString(request.content.getvalue())
        else:
            body = HTTPHeaders.parse(request.content.getvalue())
        print('[AirPlayer] body:', body)
        if 'Content-Location' in body:
            url = body['Content-Location']
            print('[AirPlayer] Playing ', url)
            start = float(0.0)
            if 'Start-Position' in body:
                try:
                    str_pos = body['Start-Position']
                    start = float(str_pos)
                    print('[AirPlayer] start-position supplied: ', start, '%')
                except ValueError:
                    print('[AirPlayer] Invalid start-position supplied: ', str_pos)
                    start = float(0.0)

            else:
                start = float(0)
            self._media_backend.play_movie(url, start)
        request.setHeader('content-length', 0)
        request.finish()
        return 1


class ScrubHandler(BaseHandler):

    def render_GET(self, request):
        position, duration, bufferPosition = self._media_backend.get_player_position()
        if not position:
            duration = position = 0
        body = 'duration: %f\r\nposition: %f\r\n' % (duration, position)
        request.setHeader('content-length', len(body))
        request.write(body)
        request.finish()
        return 1

    def render_POST(self, request):
        if 'position' in request.args:
            try:
                str_pos = request.args['position'][0]
                position = float(str_pos)
            except ValueError:
                print('[AirPlayer] Invalid scrub value supplied: ', str_pos)
            else:
                self._media_backend.set_player_position(position)

        request.setHeader('content-length', 0)
        request.finish()
        return 1


class RateHandler(BaseHandler):

    def render_POST(self, request):
        print('[AirPlayer] RateHandler POST')
        if 'value' in request.args:
            play = bool(float(request.args['value'][0]))
            position, duration, bufferPosition = self._media_backend.get_player_position()
            if position < 3.0:
                print('[AirPlayer] playback not yet started skipping play/pause ')
                self._protocolHandler.sendEventInfo('playing')
            else:
                print('[AirPlayer] play? ', request.args['value'][0])
                if play:
                    self._media_backend.play()
                else:
                    self._media_backend.pause()
        request.setHeader('content-length', 0)
        request.finish()
        return 1


class PhotoHandler(BaseHandler):

    def render_POST(self, request):
        self.render_PUT(request)

    def render_PUT(self, request):
        print('[AirPlayer] PHOTOHandler POST')
        if request.content.read() is not None:
            request.content.seek(0)
            file(config.plugins.airplayer.path.value + '/pic.jpg', 'wb').write(request.content.read())
            if os.path.isfile(config.plugins.airplayer.path.value + '/pic.jpg'):
                self._media_backend.show_picture(request.content.read())
            else:
                Notifications.AddNotification(MessageBox, _('Your Photo could not be saved to %s ! Please change the Path in the Settings to a writable location!') % config.plugins.airplayer.path.value, type=MessageBox.TYPE_INFO, timeout=10)
        request.setHeader('content-length', 0)
        request.finish()
        return


class AuthorizeHandler(BaseHandler):

    def render_GET(self, request):
        print('[AirPlayer] AuthorizeHandler GET')
        request.setHeader('content-length', 0)
        request.finish()
        return 1

    def render_POST(self, request):
        print('[AirPlayer] AuthorizeHandler POST')
        request.setHeader('content-length', 0)
        request.finish()
        return 1


class StopHandler(BaseHandler):

    def render_POST(self, request):
        print('[AirPlayer] StopHandler POST')
        self._media_backend.stop_playing()
        request.setHeader('content-length', 0)
        request.finish()
        print('[AirPlayer] StopHandler done')
        return 1


class ServerInfoHandler(BaseHandler):

    def render_GET(self, request):
        mac = iNetwork.getAdapterAttribute(config.plugins.airplayer.interface.value, 'mac')
        if mac is None:
            mac = '01:02:03:04:05:06'
        mac = mac.upper()
        response = appletv.SERVER_INFO % mac
        request.setHeader('Content-Type', 'text/x-apple-plist+xml')
        request.setHeader('content-length', len(response))
        request.write(response)
        request.finish()
        return 1


class SlideshowFeaturesHandler(BaseHandler):

    def render_GET(self, request):
        request.setHeader('content-length', 0)
        request.finish()
        return 1


class PlaybackInfoHandler(BaseHandler):

    def render_GET(self, request):
        playing = self._media_backend.is_playing()
        position, duration, bufferPosition = self._media_backend.get_player_position()
        if not duration and self._media_backend.MovieWindow is not None and not self._media_backend.MovieWindow.endReached:
            position = duration = 0
            body = appletv.PLAYBACK_INFO_NOT_READY
        else:
            position = round(float(position), 2)
            duration = round(float(duration), 2)
            body = appletv.PLAYBACK_INFO % (duration,
             bufferPosition,
             position,
             int(playing),
             duration)
        request.setHeader('Content-Type', 'text/x-apple-plist+xml')
        request.setHeader('content-length', len(body))
        request.write(body)
        request.finish()
        return 1


class SetProterpyHandler(BaseHandler):

    def render_GET(self, request):
        request.setHeader('content-length', 0)
        request.finish()
        return 1

    def render_POST(self, request):
        request.setHeader('content-length', 0)
        request.finish()
        return 1


class GetProterpyHandler(BaseHandler):

    def render_GET(self, request):
        request.setHeader('content-length', 0)
        request.finish()
        return 1

    def render_POST(self, request):
        request.setHeader('content-length', 0)
        request.finish()
        return 1
