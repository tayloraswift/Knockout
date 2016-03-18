from html import parser, unescape, escape
from ast import literal_eval
from itertools import chain
import re

from bulletholes.counter import TCounter as Counter
from elements.elements import Paragraph, OpenFontpost, CloseFontpost, Inline_element, Block_element, Node
from model.wonder import words
from style import styles
from modules import modules, inlinetags, blocktags, textfacing
from state.exceptions import IO_Error
from IO.xml import count_styles

inlinecontainers = {'p'} | textfacing

def write_node(node, indent=0):
    return [[indent, '<' + node.print_A() + '>']] + write_html(node.content, indent + 1) + [[indent, '</' + node.name + '>']]

def write_inline_node(node, indent=0):
    if node.content:
        if not node.textfacing and all(isinstance(e, Node) for e in node.content):
            A = [[indent, '<' + node.print_A() + '>']]
            A.extend(chain.from_iterable(write_inline_node(N, indent + 1) for N in node.content))
            return A + [[indent, '</' + node.name + '>']]
        else:
            A = [[indent, '<' + node.print_A() + '>']]
            content = write_html(node.content, indent + 1)
            if content:
                A[-1][1] += content.pop(0)[1]
                A += content
            A[-1][1] += '</' + node.name + '>'
            return A
    else:
        return [[indent, '<' + node.print_A() + '/>']]
    
def write_html(L, indent=0):
    lines = []
    gaps = [i for i, v in enumerate(L) if isinstance(v, (Paragraph, Node))]
    lead = 0
    for C in (L[i:j] for i, j in zip([0] + gaps, gaps + [len(L)]) if j != i): # to catch last blob
        if isinstance(C[0], Node): # node
            if isinstance(C[0], Inline_element):
                LL = write_inline_node(C[0], indent)
                if lines:
                    lines[-1][1] += LL.pop(0)[1]
                lines += LL
                lines[-1][1] += ''.join(repr(c) if type(c) is not str else escape(c) if len(c) == 1 else c for c in C[1:])

            else:
                if isinstance(C[0], Block_element):
                    lines.append([indent, ''])
                    lead = 1
                lines += write_node(C[0], indent)
        else:
            lines.append([indent, ''])
            lines.append([indent, ''.join(repr(c) if type(c) is not str else escape(c) if len(c) == 1 else c for c in C)])
            lead = 1
    return lines[lead:]

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
        ptags = Counter({styles.PTAGS[T.strip()]: V for T, V in count_styles(attrs['class'])})
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
        self._C = [(None, None, self._O)]
        self._breadcrumbs = [None]
        
        self.rawdata = self.rawdata + data
        self.goahead(0)
        
        self._trim()
        return self._O

    def _breadcrumb_error(self):
        raise IO_Error('Syntax error: tag mismatch')
    
    def append_to(self):
        return self._C[-1][2]
    
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        O = self.append_to()
        
        if tag == 'p':
            self._first = False
            O.append(_create_paragraph(attrs))
            
            self._breadcrumbs.append('p')
        
        elif tag in modules:
            self._breadcrumbs.append(tag)
            if tag in blocktags:
                self._first = False
                M = tag, attrs, Text(), _create_paragraph(attrs)
            else:
                M = tag, attrs, Text()
            O.append(M)
            self._C.append(M)

    def _se(self, tag, attrs):
        attrs = dict(attrs)
        O = self.append_to()
        if tag == 'br':
            O.append('<br/>')
        elif tag in inlinetags:
            O.append(modules[tag](tag, attrs, Text()))
    
    def handle_startendtag(self, tag, attrs):
        if self._breadcrumbs[-1] in inlinecontainers:
            self._se(tag, attrs)

    def handle_endtag(self, tag):
        O = self.append_to()
        if tag == 'p':
            O.append('</p>')
            if self._breadcrumbs[-1] == 'p':
                self._breadcrumbs.pop()
            else:
                self._breadcrumb_error()
                
        elif tag in modules:
            if self._breadcrumbs[-1] == tag:
                self._breadcrumbs.pop()
            else:
                self._breadcrumb_error()
            
            nodedata = self._C.pop()
            O = self.append_to()
            O[-1] = modules[tag]( * nodedata )

    def handle_data(self, data):
        # this should be disabled on the last blob, unless we are sure the container is 'p'
        if self._breadcrumbs[-1] in inlinecontainers:
            O = self.append_to()
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
            O = self.append_to()
            O.extend(data)
        elif self._first and self._breadcrumbs[-1] is None: # register the first blob
            O = self.append_to()
            self._first = False
            self._breadcrumbs.append('p') # virtual paragraph container
            liquid = list(data)
            for i, v in enumerate(liquid):
                if v == '\n':
                    liquid[i] = '<br/>'
            O.extend(liquid)

Q = Minion()
R = Kevin_from_TN()

IN = dict((('<em>', '<fo class="emphasis"/>'), 
    ('</em>', '<fc class="emphasis"/>'),
    ('<strong>', '<fo class="strong"/>'),
    ('</strong>', '<fc class="strong"/>'),
    ('<sup>', '<fo class="sup"/>'),
    ('</sup>', '<fc class="sup"/>'),
    ('<sub>', '<fo class="sub"/>'),
    ('</sub>', '<fc class="sub"/>')))
OUT = {k: v for v, k in IN.items()}

inpattern = re.compile("|".join([re.escape(k) for k in IN.keys()]), re.M)
outpattern = re.compile("|".join([re.escape(k) for k in OUT.keys()]), re.M)

def deserialize(text, fragment=False):
    if fragment:
        return R.feed( inpattern.sub(lambda x: IN[x.group(0)], text) )
    else:
        return Q.feed( inpattern.sub(lambda x: IN[x.group(0)], text) )

def serialize(L):
    return outpattern.sub(lambda x: OUT[x.group(0)], '\n'.join('    ' * indent + line for indent, line in write_html(L)) )
