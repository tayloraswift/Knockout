from html import parser, unescape, escape
from itertools import chain
from ast import literal_eval

from bulletholes.counter import TCounter as Counter
from elements.elements import Paragraph, OpenFontpost, CloseFontpost, Image
from style import styles
from modules import table, pie, fraction, bounded
from state.exceptions import IO_Error

INLINE = (fraction, fraction.Fraction), (bounded, bounded.Bounded)
BLOCK = (table, table.Table), (pie, pie.PieChart)

def _load_module(mods):
    M = {}
    for mod, mobj in mods:
        M[mod.namespace] = mobj, mod.tags
    return M

modules = _load_module(INLINE + BLOCK)
moduletags = set(modules) | set(chain.from_iterable(v[1] for v in modules.values()))
inlinetags = {'p'}.union( * (I[0].tags for I in INLINE))
blocknames = set(B[0].namespace for B in BLOCK)

blocktypes = set(B[1] for B in BLOCK)
inlinetypes = set(I[1] for I in INLINE)
newline_on = {Paragraph} | blocktypes | inlinetypes

def _create_paragraph(attrs):
    if 'class' in attrs:
        ptags = Counter(styles.PTAGS[T.strip()] for T in attrs['class'].split('&'))
    else:
        ptags = Counter({styles.PTAGS['body']: 1})
    if 'style' in attrs:
        EP = styles.cast_parastyle(literal_eval(attrs['style']), ())
    else:
        EP = styles.DB_Parastyle()
    return Paragraph(ptags, EP)

class Minion(parser.HTMLParser):
    def _trim(self):
        if self._breadcrumbs != [None]:
            last = len(self._O) - next(i for i, v in enumerate(reversed(self._O)) if type(v) is str)
            del self._O[last:]

    def feed(self, data):
        self.reset()
        self._first = True
        self._O = []
        self._C = [(None, self._O)]
        self._breadcrumbs = [None]
        
        self.rawdata = self.rawdata + data
        self.goahead(0)
        
        self._trim()
        return self._O

    def _breadcrumb_error(self):
        raise IO_Error('Syntax error: tag mismatch')
        
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        O = self._C[-1][1]
        self._first = False
        if tag == 'p':
            O.append(_create_paragraph(attrs))
            
            self._breadcrumbs.append('p')
        
        elif tag == 'f':
            ftag = styles.FTAGS[attrs['class']]
            O.append(OpenFontpost(ftag))

        elif tag == 'ff':
            ftag = styles.FTAGS[attrs['class']]
            O.append(CloseFontpost(ftag))
        
        elif tag in moduletags:
            self._breadcrumbs.append(tag)
            if tag in blocknames:
                M = ((tag, attrs, _create_paragraph(attrs)), [])
            else:
                M = ((tag, attrs), [])
            O.append(M)
            self._C.append(M)

    def handle_startendtag(self, tag, attrs):
        attrs = dict(attrs)
        O = self._C[-1][1]
        if tag == 'br':
            O.append('<br/>')
        if tag == 'image':
            src = attrs.get('src', None)
            width = int(attrs.get('width', 89))
            O.append(Image(src, width))

    def handle_endtag(self, tag):
        O = self._C[-1][1]
        if tag == 'p':
            O.append('</p>')
            if self._breadcrumbs[-1] == 'p':
                self._breadcrumbs.pop()
            else:
                self._breadcrumb_error()
                
        elif tag in moduletags:
            if self._breadcrumbs[-1] == tag:
                self._breadcrumbs.pop()
            else:
                self._breadcrumb_error()
            
            L = self._C.pop()
            if tag in modules:
                O = self._C[-1][1]
                O[-1] = modules[tag][0](L, deserialize, ser)

    def handle_data(self, data):
        # this should be disabled on the last blob, unless we are sure the container is 'p'
        O = self._C[-1][1]
        container = self._breadcrumbs[-1]
        if container in inlinetags:
            O.extend(list(data))

class Kevin_from_TN(Minion): # to capture the first and last blobs
    def _trim(self):
        pass
    
    def _breadcrumb_error(self):
        if self._first:
            self._first = False
        else:
            raise IO_Error('Syntax error: tag mismatch')
    
    def handle_data(self, data):
        O = self._C[-1][1]
        container = self._breadcrumbs[-1]
        if container in inlinetags:
            O.extend(list(data))
        elif self._first: # register the first blob
            self._first = False
            self._breadcrumbs.append('p') # virtual paragraph container
            liquid = list(data)
            for i, v in enumerate(liquid):
                if v == '\n':
                    liquid[i] = '<br/>'
            O.extend(liquid)

Q = Minion()
R = Kevin_from_TN()

def deserialize(text, fragment=False):
    if fragment:
        parse = R
    else:
        text.replace('\n', '')
        parse = Q
    text = text.replace('<em>', '<f class="emphasis">')
    text = text.replace('</em>', '</f class="emphasis">')
    text = text.replace('<strong>', '<f class="strong">')
    text = text.replace('</strong>', '</f class="strong">')
    text = text.replace('<sup>', '<f class="sup">')
    text = text.replace('</sup>', '</f class="sup">')
    text = text.replace('<sub>', '<f class="sub">')
    text = text.replace('</sub>', '</f class="sub">')
    return parse.feed(text.replace('</f', '<ff'))

def ser(L, indent):
    lines = []
    gaps = [0] + [i for i, v in enumerate(L) if type(v) in newline_on]
    lead = 0
    for C in (L[i:j] for i, j in zip(gaps, gaps[1:] + [len(L)]) if j != i): # to catch last blob
        if type(C[0]) in blocktypes:
            lines.append([indent, ''])
            lines.extend(C[0].represent(indent))
            lead = 1
        elif type(C[0]) in inlinetypes:
            LL = C[0].represent(indent)
            if lines:
                lines[-1][1] += LL.pop(0)[1]
            lines.extend(LL)
            lines[-1][1] += ''.join(repr(c) if type(c) is not str else escape(c) if len(c) == 1 else c for c in C[1:])
        else:
            lines.append([indent, ''])
            lines.append([indent, ''.join(repr(c) if type(c) is not str else escape(c) if len(c) == 1 else c for c in C)])
            lead = 1
    return lines[lead:]

def serialize(L):
    return '\n'.join('    ' * indent + line for indent, line in ser(L, 0))
