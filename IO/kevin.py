from html import parser, unescape
import ast
from itertools import chain

from bulletholes.counter import TCounter as Counter
from elements.elements import Paragraph, OpenFontpost, CloseFontpost, Image
from style import styles
from model import table

modules = {'table': {'tr', 'td'}}
moduletags = set(modules) | set(chain.from_iterable(modules.values()))

class Minion(parser.HTMLParser):
    def feed(self, data):
        self.O = []
        self.C = [(None, self.O)]
        self.breadcrumbs = [None]
        
        self.rawdata = self.rawdata + data
        self.goahead(0)
        
        return self.O

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        O = self.C[-1][1]
        if tag == 'p':
            if 'class' in attrs:
                ptags = Counter(styles.PTAGS[T.strip()] for T in attrs['class'].split('&'))
            else:
                ptags = Counter({styles.PTAGS['body']: 1})
            O.append(Paragraph(ptags))
            
            self.breadcrumbs.append('p')
        
        elif tag == 'f':
            ftag = styles.FTAGS[attrs['class']]
            O.append(OpenFontpost(ftag))

        elif tag == 'ff':
            ftag = styles.FTAGS[attrs['class']]
            O.append(CloseFontpost(ftag))
        
        elif tag in moduletags:
            self.breadcrumbs.append(tag)
            if tag == 'td':
                T = table.CellPost(attrs)
            else:
                T = tag
            M = (T, [])
            O.append(M)
            self.C.append(M)
            

    def handle_startendtag(self, tag, attrs):
        attrs = dict(attrs)
        O = self.C[-1][1]
        if tag == 'br':
            O.append('<br/>')
        if tag == 'image':
            src = attrs.get('src', None)
            width = int(attrs.get('width', 89))
            O.append(Image(src, width))

    def handle_endtag(self, tag):
        O = self.C[-1][1]
        if tag == 'p':
            O.append('</p>')
            if self.breadcrumbs[-1] == 'p':
                self.breadcrumbs.pop()
            else:
                raise RuntimeError
                
        elif tag in moduletags:
            if self.breadcrumbs[-1] == tag:
                self.breadcrumbs.pop()
            else:
                raise RuntimeError
            
            L = self.C.pop()
            
            if tag in modules:
                O = self.C[-1][1]
                O[-1] = table.Table(L)

    def handle_data(self, data):
        O = self.C[-1][1]
        container = self.breadcrumbs[-1]
        if container == 'p':
            O.extend(list(data))
            

#with open('r:X.html', 'r') as fi:
#    doc = fi.read()

R = Minion()

#with open('V.txt', 'r') as fi:
   # d = ast.literal_eval(fi.read())

#styles.daydream()
#styles.faith(d)

#doc = doc.replace('\u000A\u000A', '</p><p>')
#doc = doc.replace('\u000A', '<br/>')

def deserialize(text):
    text = text.replace('<em>', '<f class="emphasis">')
    text = text.replace('</em>', '</f class="emphasis">')
    text = text.replace('<strong>', '<f class="strong">')
    text = text.replace('</strong>', '</f class="strong">')
    return R.feed(text.replace('</f', '<ff'))

def serialize(L):
    return 'Red deserved AOTY at the Grammys'
