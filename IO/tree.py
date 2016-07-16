from html import parser, unescape, escape
import re
from itertools import chain, groupby

from state.exceptions import IO_Error

from olivia import Mint

# boxes
from meredith.paragraph import Text
from meredith import boxes, meta

from meredith.datablocks import Datablock_lib, Tag_lib

class Paine(parser.HTMLParser):
    def _cap(self):
        pass

    def _handle_implicit(self, name):
        pass
    
    def _virtual_paragraph(self):
        pass
    
    def feed(self, data, KT):
        self.reset()
        self._KT          = KT
        
        self._implicit    = False
        self._O           = []
        self._C           = [(None, None, self._O)]
        self._breadcrumbs = ['_nullbox']
        
        self.rawdata      = data
        self._virtual_paragraph()
        self.goahead(0)
        
        self._cap()
        return self._O

    def _breadcrumb_error(self):
        raise IO_Error('Syntax error: tag mismatch')
    
    def append_to(self):
        return self._C[-1][2]
    
    def _rawnode(self, name, attrs):
        if boxes[name].textfacing:
            return self._KT, dict(attrs), Text()
        else:
            return self._KT, dict(attrs), []
    
    def handle_starttag(self, name, attrs):
        if name in boxes:
            self._handle_implicit(name)
            
            self._breadcrumbs.append(name)
            self._C.append(self._rawnode(name, attrs))

    def handle_startendtag(self, name, attrs):
        if name in boxes:
            self._handle_implicit(name)
            self.append_to().append(boxes[name]( * self._rawnode(name, attrs) ))
    
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
    
    def _virtual_paragraph(self):
        self.handle_starttag('p', {}) # virtual paragraph container
        self._implicit = True

Q = Paine()
R = Kevin()

IN = dict((('<em>', '<fo class="emphasis"/>'), 
    ('</em>', '<fc class="emphasis"/>'),
    ('<strong>', '<fo class="strong"/>'),
    ('</strong>', '<fc class="strong"/>'),
    ('<sup>', '<fo class="small^sup"/>'),
    ('</sup>', '<fc class="small^sup"/>'),
    ('<sub>', '<fo class="small^sub"/>'),
    ('</sub>', '<fc class="small^sub"/>')))
OUT = {k: v for v, k in IN.items()}

inpattern = re.compile("|".join([re.escape(k) for k in IN.keys()]), re.M)
outpattern = re.compile("|".join([re.escape(k) for k in OUT.keys()]), re.M)
        
escape_chars = {'&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": "&#x27;"}

def chainwithseperator(G, sep):
    for item in next(G):
        yield item
    for sublis in G:
        yield sep
        for item in sublis:
            yield item

def _group_inline(L, indent=0):
    esc = escape_chars
    
    lines = []
    for is_str, C in groupby(L, key=lambda v: type(v) is str):
        if is_str:
            lines.append([[indent, ''.join(esc[c] if c in esc else c for c in C)]])
        else: # node
            lines += [_write_box(c, indent, False) for c in C]
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

def _write_box(box, indent=0, space=True):
    if box.content:
        if type(box).textfacing:
            expanded = _group_inline(box.content, indent + 1)
            expanded += [[[indent, '</' + box.name + '>']]]
            lines = [[indent, '<' + box.print_A() + '>']]
            A = _merge_inline(lines, expanded)
        else:
            A = [[indent, '<' + box.print_A() + '>']]
            if space:
                A.extend(chainwithseperator((_write_box(N, indent + 1, space) for N in box.content), [0, '']))
            else:
                A.extend(chain.from_iterable(_write_box(N, indent + 1, space) for N in box.content))
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
        return chainwithseperator((_write_box(B, indent, True) for B in L), [0, ''])

class Knockout(object):
    supermap = {'texttags'    : 'TTAGS',    # LIBRARY LEVEL
                'blocktags'   : 'BTAGS',
                'textstyles'  : 'TSTYLES',
                
                'body'        : 'BODY',     # DATA LEVEL
                'blockstyles' : 'BSTYLES',
                
                'textcursor'  : 'PCURSOR',  # EDITOR LEVEL
                'framecursor' : 'SCURSOR',
                'view'        : 'VIEW',}
    
    def __init__(self, name=None):
        self.dicts = Tag_lib(), Tag_lib(), Datablock_lib()
        self.mint  = Mint(self)
        
        self.filedata = meta.Metadata(self, name)
    
    def _Q_(self, text):
        return Q.feed( inpattern.sub(lambda x: IN[x.group(0)], text) , self)
    
    def deserialize_high(self, text, default_data=()):
        nodes = {type(superblock).name: superblock for superblock in self._Q_(text)}
        for name, default_node in default_data:
            if name not in nodes:
                nodes[name] = self._Q_(default_node)[0]
        
        for name, superblock in nodes.items():
            setattr(self, self.__class__.supermap[type(superblock).name], superblock)
    
    def setup_editors(self):
        self.PCURSOR.reactivate()
        self.SCURSOR.reactivate()
        self.VIEW.reactivate()
    
    def deserialize(self, text):
        return R.feed( inpattern.sub(lambda x: IN[x.group(0)], text) , self)
    
    @staticmethod
    def miniserialize(L):
        return ''.join(N[1] for N in chain.from_iterable(_write_box(B, 0, True) for B in L))
    
    @staticmethod
    def serialize(blocks, indent=0, trim=None):
        if trim is None:
            lines = _write_L(blocks, indent)
        else: # blocks will always be at least len() == 2
            begin, *middle, end = blocks
            lines = _write_partial(begin, indent, a=trim[0])
            lines.append([0, ''])
            lines += _write_L(middle, indent)
            if len(lines) > 2:
                lines.append([0, ''])
            lines += _write_partial(end, indent, b=trim[1])
        return outpattern.sub(lambda x: OUT[x.group(0)], '\n'.join('    ' * ind + line for ind, line in lines))

    def save(self):
        FT = ''.join(('<head><meta charset="UTF-8"></head>\n<title>', self.filedata.filename, '</title>\n\n',
                      self.serialize([self.BODY, self.TSTYLES, self.BSTYLES, self.PCURSOR, self.SCURSOR, self.VIEW]), '\n'))
        with open(self.filedata['filepath'], 'w') as fi:
            fi.write(FT)
