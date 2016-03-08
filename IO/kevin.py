from html import parser, unescape, escape
from ast import literal_eval

from bulletholes.counter import TCounter as Counter
from elements.elements import Paragraph, OpenFontpost, CloseFontpost, Inline_element, Block_element
from model.wonder import words
from style import styles
from modules import modules, moduletags, inlinecontainers, inlinetags, blocktags
from state.exceptions import IO_Error

class Text(list):
    def __init__(self, * args):
        list.__init__(self, * args)

        # STATS
        self.word_count = '—'
        self.misspellings = []
        self.stats(True)
    
    def stats(self, spell=False):
        if spell:
            self.word_count, self.misspellings = words(self, spell=True)
        else:
            self.word_count = words(self)

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
        self._O = Text()
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
        
        if tag == 'p':
            self._first = False
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
            if tag in blocktags:
                self._first = False
                M = ((tag, attrs, _create_paragraph(attrs)), Text())
            else:
                M = ((tag, attrs), Text())
            O.append(M)
            self._C.append(M)

    def _se(self, tag, attrs):
        attrs = dict(attrs)
        O = self._C[-1][1]
        if tag == 'br':
            O.append('<br/>')
        elif tag in inlinetags:
            O.append(modules[tag](((tag, attrs), Text()), deserialize, ser))
    
    def handle_startendtag(self, tag, attrs):
        if self._breadcrumbs[-1] in inlinecontainers:
            self._se(tag, attrs)

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
                O[-1] = modules[tag](L, deserialize, ser)

    def handle_data(self, data):
        # this should be disabled on the last blob, unless we are sure the container is 'p'
        if self._breadcrumbs[-1] in inlinecontainers:
            O = self._C[-1][1]
            O.extend(data)

class Kevin_from_TN(Minion): # to capture the first and last blobs
    def _trim(self):
        pass
    
    def _breadcrumb_error(self):
        if self._first:
            self._first = False
        else:
            raise IO_Error('Syntax error: tag mismatch')
    
    def handle_startendtag(self, tag, attrs):
        if self._breadcrumbs[-1] in inlinecontainers:
            self._se(tag, attrs)
        elif self._first: # register the first blob
            self._first = False
            self._breadcrumbs.append('p') # virtual paragraph container
            self._se(tag, attrs)
            
    def handle_data(self, data):
        if self._breadcrumbs[-1] in inlinecontainers:
            O = self._C[-1][1]
            O.extend(data)
        elif self._first and self._breadcrumbs[-1] is None: # register the first blob
            O = self._C[-1][1]
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
    gaps = [0] + [i for i, v in enumerate(L) if isinstance(v, (Paragraph, Block_element, Inline_element))]
    lead = 0
    for C in (L[i:j] for i, j in zip(gaps, gaps[1:] + [len(L)]) if j != i): # to catch last blob
        if isinstance(C[0], Block_element):
            lines.append([indent, ''])
            lines += C[0].represent(indent)
            lead = 1
        elif isinstance(C[0], Inline_element):
            LL = C[0].represent(indent)
            if lines:
                lines[-1][1] += LL.pop(0)[1]
            lines += LL
            lines[-1][1] += ''.join(repr(c) if type(c) is not str else escape(c) if len(c) == 1 else c for c in C[1:])
        else:
            lines.append([indent, ''])
            lines.append([indent, ''.join(repr(c) if type(c) is not str else escape(c) if len(c) == 1 else c for c in C)])
            lead = 1
    return lines[lead:]

def serialize(L):
    return '\n'.join('    ' * indent + line for indent, line in ser(L, 0))
