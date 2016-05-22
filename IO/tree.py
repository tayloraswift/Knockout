from html import parser, unescape, escape
import re
from itertools import chain, groupby

from state.exceptions import IO_Error

# boxes
from meredith import box, elements, styles, paragraph

boxes = {B.name: B for B in chain.from_iterable(M.members for M in (box, styles, elements, paragraph))}

Text = paragraph.Text

class Paine(parser.HTMLParser):
    def _cap(self):
        pass

    def _handle_implicit(self, name):
        pass

    def feed(self, data):
        self.reset()
        self._first = True
        self._implicit = False
        self._O = []
        self._C = [(None, self._O)]
        self._breadcrumbs = ['_nullbox']
        
        self.rawdata = data
        self.goahead(0)
        
        self._cap()
        return self._O

    def _breadcrumb_error(self):
        raise IO_Error('Syntax error: tag mismatch')
    
    def append_to(self):
        return self._C[-1][1]
    
    def handle_starttag(self, name, attrs):
        if name in boxes:
            self._handle_implicit(name)
            
            self._breadcrumbs.append(name)
            if boxes[name].textfacing:
                M = dict(attrs), Text()
            else:
                M = dict(attrs), []
            self._C.append(M)

    def handle_startendtag(self, name, attrs):
        if name in boxes:
            if not boxes[name].inline or boxes[self._breadcrumbs[-1]].textfacing:
                self.append_to().append(boxes[name]( dict(attrs) ))
    
    def handle_endtag(self, name):
        if name in boxes:
            if self._breadcrumbs[-1] == name:
                self._breadcrumbs.pop()
            else:
                self._breadcrumb_error()
            
            B = boxes[name]( * self._C.pop() )
            self.append_to().append(B)
    
    def handle_data(self, data):
        if boxes[self._breadcrumbs[-1]].textfacing:
            O = self.append_to()
            O.extend(data)

class Kevin(Paine): # to capture the first and last blobs
    def _cap(self):
        if self._breadcrumbs == ['_nullbox', 'p']:
            self.handle_endtag('p')
    
    def _handle_implicit(self, name):
        if self._implicit and not boxes[name].inline and self._breadcrumbs == ['_nullbox', 'p']: # nullify implicit paragraph if not needed
            self._C.pop()
            self._breadcrumbs.pop()
            self._implicit = False
    
    def handle_startendtag(self, name, attrs):
        if name in boxes:
            if not boxes[name].inline or boxes[self._breadcrumbs[-1]].textfacing:
                self._handle_implicit(name)
            elif self._first and self._breadcrumbs[-1] == '_nullbox': # register the first blob
                self.handle_starttag('p', {}) # virtual paragraph container
                self._first = False
                self._implicit = True
            else:
                return
            self.append_to().append(boxes[name]( dict(attrs) ))
    
    def handle_data(self, data):
        if boxes[self._breadcrumbs[-1]].textfacing:
            pass
        elif self._first and self._breadcrumbs[-1] == '_nullbox': # register the first blob
            self.handle_starttag('p', {}) # virtual paragraph container
            self._first = False
            self._implicit = True
        else:
            return
        O = self.append_to()
        O.extend(data)

Q = Paine()
R = Kevin()

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

escape_chars = {'&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": "&#x27;"}

def _group_inline(L, indent=0):
    esc = escape_chars
    
    lines = []
    for is_str, C in groupby(L, key=lambda v: type(v) is str):
        if is_str:
            lines.append([[indent, ''.join(esc[c] if c in esc else c for c in C)]])
        else: # node
            lines += [_write_box(c, indent) for c in C]
    
    return lines

def _merge_inline(lines, expanded):
    for E in expanded:
        lines[-1].append(E.pop(0)[1])
        lines += E
    return [[k[0], ''.join(k[1:])] for k in lines]

def _write_partial(box, indent=0, a=None, b=None):
    if a is None: # front half
        expanded = _group_inline(box.content[:b], indent + 1)
        lines = [[indent, '<' + box.print_A() + '>']]
    else:
        expanded = _group_inline(box.content[a:], indent + 1)
        expanded += [[[indent, '</' + box.name + '>']]]
        lines = [[indent]]
    return _merge_inline(lines, expanded)

def _write_box(box, indent=0):
    if box.content:
        if type(box).textfacing:
            expanded = _group_inline(box.content, indent + 1)
            expanded += [[[indent, '</' + box.name + '>']]]
            lines = [[indent, '<' + box.print_A() + '>']]
            A = _merge_inline(lines, expanded)
        else:
            A = [[indent, '<' + box.print_A() + '>']]
            A.extend(chain.from_iterable(_write_L(N.content, indent + 1) for N in box.content))
            A += [[indent, '</' + box.name + '>']]
        return A
    else:
        return [[indent, '<' + box.print_A() + '/>']]

def _write_L(L, indent=0):
    if not L:
        return []
    elif type(L[0]) is str or type(L[0]).inline:
        return _merge_inline([[indent]], _group_inline(L, indent))
    else:
        return list(chain.from_iterable(_write_box(B, indent) for B in L))

def serialize(blocks, indent=0, trim=None):
    if trim is None:
        lines = _write_L(blocks, indent)
    else: # blocks will always be at least len() == 2
        begin, *middle, end = blocks
        lines = _write_partial(begin, indent, a=trim[0])
        lines += _write_L(middle, indent)
        lines += _write_partial(end, indent, b=trim[1])
    return outpattern.sub(lambda x: OUT[x.group(0)], '\n'.join('    ' * ind + line for ind, line in lines))
