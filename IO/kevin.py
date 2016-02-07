from html import parser, unescape
import ast
from itertools import chain

from bulletholes.counter import TCounter as Counter
from elements.elements import Paragraph, OpenFontpost, CloseFontpost, Image
from style import styles
from model import table

modules = {'table': {'tr', 'td'}}
moduletags = set(modules) | set(chain.from_iterable(modules.values()))
closing = {table.Table}

class Minion(parser.HTMLParser):
    def _trim(self):
        if self._breadcrumbs != [None]:
            last = len(self._O) - next(i for i, v in enumerate(reversed(self._O)) if type(v) is str)
            del self._O[last:]
        
    def feed(self, data):
        self._first = True
        self._O = []
        self._C = [(None, self._O)]
        self._breadcrumbs = [None]
        
        self.rawdata = self.rawdata + data
        self.goahead(0)
        
        self._trim()
        return self._O

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        O = self._C[-1][1]
        if tag == 'p':
            if 'class' in attrs:
                ptags = Counter(styles.PTAGS[T.strip()] for T in attrs['class'].split('&'))
            else:
                ptags = Counter({styles.PTAGS['body']: 1})
            O.append(Paragraph(ptags))
            
            self._breadcrumbs.append('p')
        
        elif tag == 'f':
            ftag = styles.FTAGS[attrs['class']]
            O.append(OpenFontpost(ftag))

        elif tag == 'ff':
            ftag = styles.FTAGS[attrs['class']]
            O.append(CloseFontpost(ftag))
        
        elif tag in moduletags:
            self._breadcrumbs.append(tag)
            if tag == 'td':
                T = table.CellPost(attrs)
            else:
                T = tag
            M = (T, [])
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
                raise RuntimeError
                
        elif tag in moduletags:
            if self._breadcrumbs[-1] == tag:
                self._breadcrumbs.pop()
            else:
                raise RuntimeError
            
            L = self._C.pop()
            
            if tag in modules:
                O = self._C[-1][1]
                O[-1] = table.Table(L)

    def handle_data(self, data):
        # this should be disabled on the last blob, unless we are sure the container is 'p'
        O = self._C[-1][1]
        container = self._breadcrumbs[-1]
        if container == 'p':
            O.extend(list(data))

class Kevin_from_TN(Minion): # to capture the first and last blobs
    def _trim(self):
        pass
    def handle_data(self, data):
        O = self._C[-1][1]
        container = self._breadcrumbs[-1]
        if container == 'p':
            O.extend(list(data))
        elif self._first: # register the first blob
            self._first = False
            self._breadcrumbs.append('p') # virtual paragraph container
            O.extend(list(data))

#with open('r:X.html', 'r') as fi:
#    doc = fi.read()

Q = Minion()
R = Kevin_from_TN()

#with open('V.txt', 'r') as fi:
   # d = ast.literal_eval(fi.read())

#styles.daydream()
#styles.faith(d)

#doc = doc.replace('\u000A\u000A', '</p><p>')
#doc = doc.replace('\u000A', '<br/>')

def deserialize(text, fragment=False):
    if fragment:
        parse = R
    else:
        parse = Q
    text = text.replace('<em>', '<f class="emphasis">')
    text = text.replace('</em>', '</f class="emphasis">')
    text = text.replace('<strong>', '<f class="strong">')
    text = text.replace('</strong>', '</f class="strong">')
    return parse.feed(text.replace('</f', '<ff'))

def serialize(L):
    return 'Red deserved AOTY at the Grammys'
