#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

class HTTPHeaders(dict):

    def __init__(self, *args, **kwargs):
        dict.__init__(self)
        self._as_list = {}
        self.update(*args, **kwargs)

    def add(self, name, value):
        norm_name = HTTPHeaders._normalize_name(name)
        if norm_name in self:
            dict.__setitem__(self, norm_name, self[norm_name] + ',' + value)
            self._as_list[norm_name].append(value)
        else:
            self[norm_name] = value

    def get_list(self, name):
        norm_name = HTTPHeaders._normalize_name(name)
        return self._as_list.get(norm_name, [])

    def get_all(self):
        for name, list in self._as_list.iteritems():
            for value in list:
                yield (name, value)

    def parse_line(self, line):
        name, value = line.split(':', 1)
        self.add(name, value.strip())

    @classmethod
    def parse(cls, headers):
        h = cls()
        for line in headers.splitlines():
            if line:
                h.parse_line(line)

        return h

    def __setitem__(self, name, value):
        norm_name = HTTPHeaders._normalize_name(name)
        dict.__setitem__(self, norm_name, value)
        self._as_list[norm_name] = [value]

    def __getitem__(self, name):
        return dict.__getitem__(self, HTTPHeaders._normalize_name(name))

    def __delitem__(self, name):
        norm_name = HTTPHeaders._normalize_name(name)
        dict.__delitem__(self, norm_name)
        del self._as_list[norm_name]

    def get(self, name, default = None):
        return dict.get(self, HTTPHeaders._normalize_name(name), default)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v

    _NORMALIZED_HEADER_RE = re.compile('^[A-Z0-9][a-z0-9]*(-[A-Z0-9][a-z0-9]*)*$')

    @staticmethod
    def _normalize_name(name):
        if HTTPHeaders._NORMALIZED_HEADER_RE.match(name):
            return name
        return '-'.join([ w.capitalize() for w in name.split('-') ])


def doctests():
    import doctest
    return doctest.DocTestSuite()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
