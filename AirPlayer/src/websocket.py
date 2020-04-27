#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from twisted.web.http import datetimeToString
from twisted.web.server import Request, Site, version, unquote

class WebSocketRequest(Request):

    def process(self):
        if self.requestHeaders.getRawHeaders('Upgrade') == ['PTTH/1.0'] and self.requestHeaders.getRawHeaders('Connection') == ['Upgrade']:
            return self.processWebSocket()
        else:
            return Request.process(self)

    def processWebSocket(self):
        self.site = self.channel.site
        self.setHeader('server', version)
        self.setHeader('date', datetimeToString())
        self.prepath = []
        self.postpath = map(unquote, self.path[1:].split('/'))
        self.renderWebSocket()

    def _checkClientHandshake(self):

        def finish():
            self.channel.transport.loseConnection()

        if self.queued:
            return finish()
        handler = self.site.handlers.get(self.uri)
        if not handler:
            return finish()
        transport = WebSocketTransport(self)
        handler.registerTransport(transport)
        transport._attachHandler(handler)
        return handler

    def renderWebSocket(self):
        print('renderWebSocket')
        check = self._checkClientHandshake()
        if check is None:
            return
        else:
            handler = check
            self.startedWriting = True
            handshake = ['HTTP/1.1 101 Switching Protocols',
             'Date: %s' % datetimeToString(),
             'Upgrade: PTTH/1.0',
             'Connection: Upgrade']
            for header in handshake:
                self.write('%s\r\n' % header)

            self.write('\r\n')
            self.channel.setRawMode()
            self.channel._transferDecoder = WebSocketFrameDecoder(self, handler)
            return


class WebSocketSite(Site):
    requestFactory = WebSocketRequest

    def __init__(self, resource, logPath = None, timeout = 43200, supportedProtocols = None):
        Site.__init__(self, resource, logPath, timeout)
        self.handlers = {}
        self.supportedProtocols = supportedProtocols or []

    def addHandler(self, name, handlerFactory):
        if not name.startswith('/'):
            raise ValueError('Invalid resource name.')
        self.handlers[name] = handlerFactory


class WebSocketTransport(object):
    _handler = None

    def __init__(self, request):
        self._request = request
        self._request.notifyFinish().addErrback(self._connectionLost)

    def _attachHandler(self, handler):
        self._handler = handler

    def _connectionLost(self, reason):
        self._handler.connectionLost(reason)

    def write(self, frame):
        self._request.write(frame)

    def loseConnection(self):
        self._request.transport.loseConnection()


class WebSocketHandler(object):

    def __init__(self):
        pass

    def registerTransport(self, transport):
        self.transport = transport

    def frameReceived(self, frame):
        pass

    def frameLengthExceeded(self):
        self.transport.loseConnection()

    def connectionLost(self, reason):
        pass


class WebSocketFrameDecoder(object):
    MAX_LENGTH = 16384

    def __init__(self, request, handler):
        self.request = request
        self.handler = handler
        self._data = []
        self._currentFrameLength = 0

    def dataReceived(self, data):
        if not data:
            return
        while True:
            endIndex = data.find('\xff')
            if endIndex != -1:
                self._currentFrameLength += endIndex
                if self._currentFrameLength > self.MAX_LENGTH:
                    self.handler.frameLengthExceeded()
                    break
                self._currentFrameLength = 0
                frame = ''.join(self._data) + data[:endIndex]
                self._data[:] = []
                if frame[0] != '\x00':
                    self.request.transport.loseConnection()
                    break
                self.handler.frameReceived(frame[1:])
                data = data[endIndex + 1:]
                if not data:
                    break
                if data[0] != '\x00':
                    self.request.transport.loseConnection()
                    break
            else:
                self._currentFrameLength += len(data)
                if self._currentFrameLength > self.MAX_LENGTH + 1:
                    self.handler.frameLengthExceeded()
                else:
                    self._data.append(data)
                break


___all__ = ['WebSocketHandler', 'WebSocketSite']
