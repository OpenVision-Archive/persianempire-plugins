# -*- coding: utf-8 -*-
from __future__ import print_function
import base64
import urllib2

class BaseMediaBackend(object):

    def __init__(self, host = None, port = None, username = None, password = None):
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    def _http_request(self, req):
        if self._username and self._password:
            base64string = base64.encodestring('%s:%s' % (self._username, self._password))[:-1]
            req.add_header('Authorization', 'Basic %s' % base64string)
        try:
            return urllib2.urlopen(req).read()
        except urllib2.URLError as e:
            clsname = self.__class__.__name__
            name = clsname.replace('MediaBackend', '')
            print("[AirPlayer] Couldn't connect to ", name, ' at ', self.host_string())
            return None

        return None

    def host_string(self):
        return '%s:%d' % (self._host, self._port)

    def cleanup(self):
        raise NotImplementedError

    def stop_playing(self):
        raise NotImplementedError

    def show_picture(self, data):
        raise NotImplementedError

    def play_movie(self, url):
        raise NotImplementedError

    def notify_started(self):
        raise NotImplementedError

    def pause(self):
        raise NotImplementedError

    def play(self):
        raise NotImplementedError

    def get_player_position(self):
        raise NotImplementedError

    def is_playing(self):
        raise NotImplementedError

    def set_player_position(self, position):
        raise NotImplementedError

    def set_player_position_percentage(self, percentage_position):
        raise NotImplementedError

    def set_start_position(self, percentage_position):
        raise NotImplementedError
