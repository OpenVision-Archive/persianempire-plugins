import markupbase
import re

__all__ = ['SGMLParser']
interesting = re.compile('[&<]')
incomplete = re.compile('&([a-zA-Z][a-zA-Z0-9]*|#[0-9]*)?|<([a-zA-Z][^<>]*|/([a-zA-Z][^<>]*)?|![^<>]*)?')
entityref = re.compile('&([a-zA-Z][-.a-zA-Z0-9]*)[^a-zA-Z0-9]')
charref = re.compile('&#([0-9]+)[^0-9]')
starttagopen = re.compile('<[>a-zA-Z]')
shorttagopen = re.compile('<[a-zA-Z][-.a-zA-Z0-9]*/')
shorttag = re.compile('<([a-zA-Z][-.a-zA-Z0-9]*)/([^/]*)/')
piclose = re.compile('>')
endbracket = re.compile('[<>]')
commentclose = re.compile('--\\s*>')
tagfind = re.compile('[a-zA-Z][-_.a-zA-Z0-9]*')
attrfind = re.compile('\\s*([a-zA-Z_][-:.a-zA-Z_0-9]*)(\\s*=\\s*(\\\'[^\\\']*\\\'|"[^"]*"|[-a-zA-Z0-9./:;+*%?!&$\\(\\)_#=~\\\'"]*))?')

class SGMLParseError(RuntimeError):
    """Exception raised for all parse errors."""
    pass


class SGMLParser(markupbase.ParserBase):

    def __init__(self, verbose = 0):
        """Initialize and reset this instance."""
        self.verbose = verbose
        self.reset()

    def reset(self):
        """Reset this instance. Loses all unprocessed data."""
        self.rawdata = ''
        self.stack = []
        self.lasttag = '???'
        self.nomoretags = 0
        self.literal = 0
        markupbase.ParserBase.reset(self)

    def setnomoretags(self):
        """Enter literal mode (CDATA) till EOF.
        
        Intended for derived classes only.
        """
        self.nomoretags = self.literal = 1

    def setliteral(self, *args):
        """Enter literal mode (CDATA).
        
        Intended for derived classes only.
        """
        self.literal = 1

    def feed(self, data):
        """Feed some data to the parser.
        
                Call this as often as you want, with as little or as much text
                as you want (may include '
        ').  (This just saves the text,
                all the processing is done by goahead().)
                """
        self.rawdata = self.rawdata + data
        self.goahead(0)

    def close(self):
        """Handle the remaining data."""
        self.goahead(1)

    def error(self, message):
        raise SGMLParseError(message)

    def goahead(self, end):
        rawdata = self.rawdata
        i = 0
        n = len(rawdata)
        while i < n:
            if self.nomoretags:
                self.handle_data(rawdata[i:n])
                i = n
                break
            match = interesting.search(rawdata, i)
            if match:
                j = match.start()
            else:
                j = n
            if i < j:
                self.handle_data(rawdata[i:j])
            i = j
            if i == n:
                break
            if rawdata[i] == '<':
                if starttagopen.match(rawdata, i):
                    if self.literal:
                        self.handle_data(rawdata[i])
                        i = i + 1
                        continue
                    k = self.parse_starttag(i)
                    if k < 0:
                        break
                    i = k
                    continue
                if rawdata.startswith('</', i):
                    k = self.parse_endtag(i)
                    if k < 0:
                        break
                    i = k
                    self.literal = 0
                    continue
                if self.literal:
                    if n > i + 1:
                        self.handle_data('<')
                        i = i + 1
                    else:
                        break
                    continue
                if rawdata.startswith('<!--', i):
                    k = self.parse_comment(i)
                    if k < 0:
                        break
                    i = k
                    continue
                if rawdata.startswith('<?', i):
                    k = self.parse_pi(i)
                    if k < 0:
                        break
                    i = i + k
                    continue
                if rawdata.startswith('<!', i):
                    k = self.parse_declaration(i)
                    if k < 0:
                        break
                    i = k
                    continue
            elif rawdata[i] == '&':
                if self.literal:
                    self.handle_data(rawdata[i])
                    i = i + 1
                    continue
                match = charref.match(rawdata, i)
                if match:
                    name = match.group(1)
                    self.handle_charref(name)
                    i = match.end(0)
                    if rawdata[i - 1] != ';':
                        i = i - 1
                    continue
                match = entityref.match(rawdata, i)
                if match:
                    name = match.group(1)
                    self.handle_entityref(name)
                    i = match.end(0)
                    if rawdata[i - 1] != ';':
                        i = i - 1
                    continue
            else:
                self.error('neither < nor & ??')
            match = incomplete.match(rawdata, i)
            if not match:
                self.handle_data(rawdata[i])
                i = i + 1
                continue
            j = match.end(0)
            if j == n:
                break
            self.handle_data(rawdata[i:j])
            i = j

        if end and i < n:
            self.handle_data(rawdata[i:n])
            i = n
        self.rawdata = rawdata[i:]

    def parse_comment(self, i, report = 1):
        rawdata = self.rawdata
        if rawdata[i:i + 4] != '<!--':
            self.error('unexpected call to parse_comment()')
        match = commentclose.search(rawdata, i + 4)
        if not match:
            return -1
        if report:
            j = match.start(0)
            self.handle_comment(rawdata[i + 4:j])
        return match.end(0)

    _decl_otherchars = '='

    def parse_pi(self, i):
        rawdata = self.rawdata
        if rawdata[i:i + 2] != '<?':
            self.error('unexpected call to parse_pi()')
        match = piclose.search(rawdata, i + 2)
        if not match:
            return -1
        j = match.start(0)
        self.handle_pi(rawdata[i + 2:j])
        j = match.end(0)
        return j - i

    __starttag_text = None

    def get_starttag_text(self):
        return self.__starttag_text

    def parse_starttag(self, i):
        self.__starttag_text = None
        start_pos = i
        rawdata = self.rawdata
        if shorttagopen.match(rawdata, i):
            match = shorttag.match(rawdata, i)
            if not match:
                return -1
            tag, data = match.group(1, 2)
            self.__starttag_text = '<%s/' % tag
            tag = tag.lower()
            k = match.end(0)
            self.finish_shorttag(tag, data)
            self.__starttag_text = rawdata[start_pos:match.end(1) + 1]
            return k
        else:
            match = endbracket.search(rawdata, i + 1)
            if not match:
                return -1
            j = match.start(0)
            attrs = []
            if rawdata[i:i + 2] == '<>':
                k = j
                tag = self.lasttag
            else:
                match = tagfind.match(rawdata, i + 1)
                if not match:
                    self.error('unexpected call to parse_starttag')
                k = match.end(0)
                tag = rawdata[i + 1:k].lower()
                self.lasttag = tag
            while k < j:
                match = attrfind.match(rawdata, k)
                if not match:
                    break
                attrname, rest, attrvalue = match.group(1, 2, 3)
                if not rest:
                    attrvalue = attrname
                elif attrvalue[:1] == "'" == attrvalue[-1:] or attrvalue[:1] == '"' == attrvalue[-1:]:
                    attrvalue = attrvalue[1:-1]
                attrs.append((attrname.lower(), attrvalue))
                k = match.end(0)

            if rawdata[j] == '>':
                j = j + 1
            self.__starttag_text = rawdata[start_pos:j]
            self.finish_starttag(tag, attrs)
            return j

    def parse_endtag(self, i):
        rawdata = self.rawdata
        match = endbracket.search(rawdata, i + 1)
        if not match:
            return -1
        j = match.start(0)
        tag = rawdata[i + 2:j].strip().lower()
        if rawdata[j] == '>':
            j = j + 1
        self.finish_endtag(tag)
        return j

    def finish_shorttag(self, tag, data):
        self.finish_starttag(tag, [])
        self.handle_data(data)
        self.finish_endtag(tag)

    def finish_starttag(self, tag, attrs):
        try:
            method = getattr(self, 'start_' + tag)
        except AttributeError:
            try:
                method = getattr(self, 'do_' + tag)
            except AttributeError:
                self.unknown_starttag(tag, attrs)
                return -1

            self.handle_starttag(tag, method, attrs)
            return 0

        self.stack.append(tag)
        self.handle_starttag(tag, method, attrs)
        return 1

    def finish_endtag(self, tag):
        if not tag:
            found = len(self.stack) - 1
            if found < 0:
                self.unknown_endtag(tag)
                return
        else:
            if tag not in self.stack:
                try:
                    method = getattr(self, 'end_' + tag)
                except AttributeError:
                    self.unknown_endtag(tag)
                else:
                    self.report_unbalanced(tag)

                return
            found = len(self.stack)
            for i in range(found):
                if self.stack[i] == tag:
                    found = i

        while len(self.stack) > found:
            tag = self.stack[-1]
            try:
                method = getattr(self, 'end_' + tag)
            except AttributeError:
                method = None

            if method:
                self.handle_endtag(tag, method)
            else:
                self.unknown_endtag(tag)
            del self.stack[-1]

        return

    def handle_starttag(self, tag, method, attrs):
        method(attrs)

    def handle_endtag(self, tag, method):
        method()

    def report_unbalanced(self, tag):
        if self.verbose:
            print '*** Unbalanced </' + tag + '>'
            print '*** Stack:', self.stack

    def handle_charref(self, name):
        """Handle character reference, no need to override."""
        try:
            n = int(name)
        except ValueError:
            self.unknown_charref(name)
            return

        if not 0 <= n <= 255:
            self.unknown_charref(name)
            return
        self.handle_data(chr(n))

    entitydefs = {'lt': '<',
     'gt': '>',
     'amp': '&',
     'quot': '"',
     'apos': "'"}

    def handle_entityref(self, name):
        """Handle entity references.
        
        There should be no need to override this method; it can be
        tailored by setting up the self.entitydefs mapping appropriately.
        """
        table = self.entitydefs
        if table.has_key(name):
            self.handle_data(table[name])
        else:
            self.unknown_entityref(name)
            return

    def handle_data(self, data):
        pass

    def handle_comment(self, data):
        pass

    def handle_decl(self, decl):
        pass

    def handle_pi(self, data):
        pass

    def unknown_starttag(self, tag, attrs):
        pass

    def unknown_endtag(self, tag):
        pass

    def unknown_charref(self, ref):
        pass

    def unknown_entityref(self, ref):
        pass


class TestSGMLParser(SGMLParser):

    def __init__(self, verbose = 0):
        self.testdata = ''
        SGMLParser.__init__(self, verbose)

    def handle_data(self, data):
        self.testdata = self.testdata + data
        if len(`(self.testdata)`) >= 70:
            self.flush()

    def flush(self):
        data = self.testdata
        if data:
            self.testdata = ''
            print 'data:', `data`

    def handle_comment(self, data):
        self.flush()
        r = `data`
        if len(r) > 68:
            r = r[:32] + '...' + r[-32:]
        print 'comment:', r

    def unknown_starttag(self, tag, attrs):
        self.flush()
        if not attrs:
            print 'start tag: <' + tag + '>'
        else:
            print 'start tag: <' + tag,
            for name, value in attrs:
                print name + '=' + '"' + value + '"',

            print '>'

    def unknown_endtag(self, tag):
        self.flush()
        print 'end tag: </' + tag + '>'

    def unknown_entityref(self, ref):
        self.flush()
        print '*** unknown entity ref: &' + ref + ';'

    def unknown_charref(self, ref):
        self.flush()
        print '*** unknown char ref: &#' + ref + ';'

    def close(self):
        SGMLParser.close(self)
        self.flush()


def test(args = None):
    import sys
    if not args:
        args = sys.argv[1:]
    if args and args[0] == '-s':
        args = args[1:]
        klass = SGMLParser
    else:
        klass = TestSGMLParser
    if args:
        file = args[0]
    else:
        file = 'test.html'
    if file == '-':
        f = sys.stdin
    else:
        try:
            f = open(file, 'r')
        except IOError as msg:
            print file, ':', msg
            sys.exit(1)

    data = f.read()
    if f is not sys.stdin:
        f.close()
    x = klass()
    for c in data:
        x.feed(c)

    x.close()


if __name__ == '__main__':
    test()
