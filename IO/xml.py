from itertools import chain
from html import parser
from bulletholes.counter import TCounter as Counter

def print_attrs(name, attrs, imply={}):
    if attrs:
        E = ' '.join(A + '="' + V + '"' for A, V in sorted(attrs.items()) if A not in imply or imply[A] != V)
        if E:
            return name + ' ' + E
    return name

def print_styles(PP):
    S = {}
    ptags = '&'.join(chain.from_iterable((P.name for i in range(V)) if V > 0 else 
                        ('~' + P.name for i in range(abs(V))) for P, V in sorted(PP.P.items(), key=lambda k: k[0].name)))
    if ptags != 'body':
        S['class'] = ptags
    if PP.EP:
        S['style'] = repr(PP.EP.polaroid()[0])
    return S

def count_styles(S):
    if S:
        C = Counter(T for T in S.split('&') if T[0] != '~')
        C -= Counter(T[1:] for T in S.split('&') if T[0] == '~')
        return C.items()
    else:
        return ()

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
