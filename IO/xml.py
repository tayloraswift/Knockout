from itertools import chain
from html import parser

def print_attrs(name, attrs): 
    if attrs:
        return name + ' ' + ' '.join(A + '="' + repr(V)[1:-1] + '"' for A, V in attrs.items())
    else:
        return name

def print_styles(PP):
    S = {}
    ptags = '&'.join(chain.from_iterable((P.name for i in range(V)) for P, V in PP.P.items()))
    if ptags != 'body':
        S['class'] = ptags
    if PP.EP:
        S['style'] = repr(PP.EP.polaroid()[0])
    return S

class _Tagreader(parser.HTMLParser):
    def feed(self, data):
        self.reset()
        self._TAG = None
        
        self.rawdata = self.rawdata + data
        self.goahead(0)
        
        return self._TAG
        
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self._TAG = (tag, attrs)

    def handle_startendtag(self, tag, attrs):
        attrs = dict(attrs)
        self._TAG = (tag, attrs)

_T = _Tagreader()

def read_tag(string):
    return _T.feed(string)
