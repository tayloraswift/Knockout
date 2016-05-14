from html import parser, unescape, escape
import re
from itertools import chain

from state.exceptions import IO_Error

from model.wonder import words

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

# boxes
from elements import box, style
from model import meredith

boxes = {B.name: B for B in chain.from_iterable(M.members for M in (box, style, meredith))}

class Paine(parser.HTMLParser):

    def feed(self, data):
        self.reset()
        self._first = True
        self._O = []
        self._C = [(None, self._O)]
        self._breadcrumbs = ['_nullbox']
        
        self.rawdata = data
        self.goahead(0)
        
        print(self._O[4])
        return self._O

    def _breadcrumb_error(self):
        raise IO_Error('Syntax error: tag mismatch')
    
    def append_to(self):
        return self._C[-1][1]
    
    def handle_starttag(self, name, attrs):
        if name in boxes:
            self._breadcrumbs.append(name)
            if name in {'p'}:
                M = dict(attrs), Text()
            else:
                M = dict(attrs), []
            self._C.append(M)

    def handle_endtag(self, name):
        if name in boxes:
            if self._breadcrumbs[-1] == name:
                self._breadcrumbs.pop()
            else:
                self._breadcrumb_error()
            
            B = boxes[name]( * self._C.pop() )
            self.append_to().append(B)
            
    def handle_startendtag(self, name, attrs):
        if name in boxes:
            self.append_to().append(boxes[name]( dict(attrs) ))

    def handle_data(self, data):
        if boxes[self._breadcrumbs[-1]].textfacing:
            O = self.append_to()
            O.extend(data)

Q = Paine()
#R = Kevin_from_TN()

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
