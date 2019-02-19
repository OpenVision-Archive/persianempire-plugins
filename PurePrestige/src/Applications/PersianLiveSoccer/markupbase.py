import re
import string

_declname_match = re.compile('[a-zA-Z][-_.a-zA-Z0-9]*\\s*').match
_declstringlit_match = re.compile('(\\\'[^\\\']*\\\'|"[^"]*")\\s*').match
del re

class ParserBase:
    """Parser base class which provides some common support methods used
    by the SGML/HTML and XHTML parsers."""

    def __init__(self):
        if self.__class__ is ParserBase:
            raise RuntimeError('markupbase.ParserBase must be subclassed')

    def error(self, message):
        raise NotImplementedError('subclasses of ParserBase must override error()')

    def reset(self):
        self.lineno = 1
        self.offset = 0

    def getpos(self):
        """Return current line number and offset."""
        return (self.lineno, self.offset)

    def updatepos(self, i, j):
        if i >= j:
            return j
        rawdata = self.rawdata
        nlines = string.count(rawdata, '\n', i, j)
        if nlines:
            self.lineno = self.lineno + nlines
            pos = string.rindex(rawdata, '\n', i, j)
            self.offset = j - (pos + 1)
        else:
            self.offset = self.offset + j - i
        return j

    _decl_otherchars = ''

    def parse_declaration(self, i):
        rawdata = self.rawdata
        j = i + 2
        if rawdata[j:j + 1] in ('-', ''):
            return -1
        n = len(rawdata)
        decltype, j = self._scan_name(j, i)
        if j < 0:
            return j
        if decltype == 'doctype':
            self._decl_otherchars = ''
        while j < n:
            c = rawdata[j]
            if c == '>':
                data = rawdata[i + 2:j]
                if decltype == 'doctype':
                    self.handle_decl(data)
                else:
                    self.unknown_decl(data)
                return j + 1
            if c in '"\'':
                m = _declstringlit_match(rawdata, j)
                if not m:
                    return -1
                j = m.end()
            elif c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
                name, j = self._scan_name(j, i)
            elif c in self._decl_otherchars:
                j = j + 1
            elif c == '[':
                if decltype == 'doctype':
                    j = self._parse_doctype_subset(j + 1, i)
                else:
                    self.error("unexpected '[' char in declaration")
            else:
                self.error('unexpected %s char in declaration' % `(rawdata[j])`)
            if j < 0:
                return j

        return -1

    def _parse_doctype_subset(self, i, declstartpos):
        rawdata = self.rawdata
        n = len(rawdata)
        j = i
        while j < n:
            c = rawdata[j]
            if c == '<':
                s = rawdata[j:j + 2]
                if s == '<':
                    return -1
                if s != '<!':
                    self.updatepos(declstartpos, j + 1)
                    self.error('unexpected char in internal subset (in %s)' % `s`)
                if j + 2 == n:
                    return -1
                if j + 4 > n:
                    return -1
                if rawdata[j:j + 4] == '<!--':
                    j = self.parse_comment(j, report=0)
                    if j < 0:
                        return j
                    continue
                name, j = self._scan_name(j + 2, declstartpos)
                if j == -1:
                    return -1
                if name not in ('attlist', 'element', 'entity', 'notation'):
                    self.updatepos(declstartpos, j + 2)
                    self.error('unknown declaration %s in internal subset' % `name`)
                meth = getattr(self, '_parse_doctype_' + name)
                j = meth(j, declstartpos)
                if j < 0:
                    return j
            elif c == '%':
                if j + 1 == n:
                    return -1
                s, j = self._scan_name(j + 1, declstartpos)
                if j < 0:
                    return j
                if rawdata[j] == ';':
                    j = j + 1
            elif c == ']':
                j = j + 1
                while j < n and rawdata[j] in string.whitespace:
                    j = j + 1

                if j < n:
                    if rawdata[j] == '>':
                        return j
                    self.updatepos(declstartpos, j)
                    self.error('unexpected char after internal subset')
                else:
                    return -1
            elif c in string.whitespace:
                j = j + 1
            else:
                self.updatepos(declstartpos, j)
                self.error('unexpected char %s in internal subset' % `c`)

        return -1

    def _parse_doctype_element(self, i, declstartpos):
        name, j = self._scan_name(i, declstartpos)
        if j == -1:
            return -1
        rawdata = self.rawdata
        if '>' in rawdata[j:]:
            return string.find(rawdata, '>', j) + 1
        return -1

    def _parse_doctype_attlist(self, i, declstartpos):
        rawdata = self.rawdata
        name, j = self._scan_name(i, declstartpos)
        c = rawdata[j:j + 1]
        if c == '':
            return -1
        if c == '>':
            return j + 1
        while 1:
            name, j = self._scan_name(j, declstartpos)
            if j < 0:
                return j
            c = rawdata[j:j + 1]
            if c == '':
                return -1
            if c == '(':
                if ')' in rawdata[j:]:
                    j = string.find(rawdata, ')', j) + 1
                else:
                    return -1
                while rawdata[j:j + 1] in string.whitespace:
                    j = j + 1

                if not rawdata[j:]:
                    return -1
            else:
                name, j = self._scan_name(j, declstartpos)
            c = rawdata[j:j + 1]
            if not c:
                return -1
            if c in '\'"':
                m = _declstringlit_match(rawdata, j)
                if m:
                    j = m.end()
                else:
                    return -1
                c = rawdata[j:j + 1]
                if not c:
                    return -1
            if c == '#':
                if rawdata[j:] == '#':
                    return -1
                name, j = self._scan_name(j + 1, declstartpos)
                if j < 0:
                    return j
                c = rawdata[j:j + 1]
                if not c:
                    return -1
            if c == '>':
                return j + 1

    def _parse_doctype_notation(self, i, declstartpos):
        name, j = self._scan_name(i, declstartpos)
        if j < 0:
            return j
        rawdata = self.rawdata
        while 1:
            c = rawdata[j:j + 1]
            if not c:
                return -1
            if c == '>':
                return j + 1
            if c in '\'"':
                m = _declstringlit_match(rawdata, j)
                if not m:
                    return -1
                j = m.end()
            else:
                name, j = self._scan_name(j, declstartpos)
                if j < 0:
                    return j

    def _parse_doctype_entity(self, i, declstartpos):
        rawdata = self.rawdata
        if rawdata[i:i + 1] == '%':
            j = i + 1
            while 1:
                c = rawdata[j:j + 1]
                if not c:
                    return -1
                if c in string.whitespace:
                    j = j + 1
                else:
                    break

        else:
            j = i
        name, j = self._scan_name(j, declstartpos)
        if j < 0:
            return j
        while 1:
            c = self.rawdata[j:j + 1]
            if not c:
                return -1
            if c in '\'"':
                m = _declstringlit_match(rawdata, j)
                if m:
                    j = m.end()
                else:
                    return -1
            else:
                if c == '>':
                    return j + 1
                name, j = self._scan_name(j, declstartpos)
                if j < 0:
                    return j

    def _scan_name(self, i, declstartpos):
        rawdata = self.rawdata
        n = len(rawdata)
        if i == n:
            return (None, -1)
        else:
            m = _declname_match(rawdata, i)
            if m:
                s = m.group()
                name = s.strip()
                if i + len(s) == n:
                    return (None, -1)
                return (string.lower(name), m.end())
            self.updatepos(declstartpos, i)
            self.error('expected name token')
            return None

    def unknown_decl(self, data):
        pass
