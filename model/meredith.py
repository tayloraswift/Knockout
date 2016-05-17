from bisect import bisect
from itertools import groupby

from elements.box import Box
from elements.style import Blockstyle
from elements import datablocks
from elements.datatypes import Tagcounter

from model.lines import Glyphs_line, cast_liquid_line
from model.page import Page

class Sorted_pages(dict):
    def __missing__(self, key):
        self[key] = {'_annot': [], '_images': [], '_paint': [], '_paint_annot': []}
        return self[key]

class Meredith(Box):
    name = 'body'
    DNA  = [('width',   'int',  816),
            ('height',  'int',  1056),
            ('dual',    'bool', False)]
    
    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        self._sorted_pages = Sorted_pages()
    
    def layout_all(self):
        self.medium = Page(self['width'], self['height'], self['dual'])
        for section in self.content:
            section.layout()

    def transfer(self):
        if not self._sorted_pages:
            self._sorted_pages.annot = []
            for section in self.content:
                section.transfer(self._sorted_pages)
        return self._sorted_pages

class Plane(Box):
    name = '_plane_'
    plane = True

    def which(self, x, u):
        b = max(0, bisect(self._UU, u) - 1)
        block = self.content[b]
        return ((b, block), * block.which(x, u))

class Section(Plane):
    name = 'section'
    
    DNA  = [('repeat',      'int set',    ''),
            ('frames',    'frames',     '')]
    
    def layout(self):
        calc_bstyle = datablocks.BSTYLES.project_b
        frames = self['frames']
        frames.start(0)
        first = True
        UU = []
        for block in self.content:
            BSTYLE = calc_bstyle(block)
            if first:
                first = False
            else:
                frames.space(gap + BSTYLE['margin_top'])
            block.layout(frames, BSTYLE)
            UU.append(block.u)
            gap = BSTYLE['margin_bottom']
        self._UU = UU
    
    def transfer(self, S):
        for block in self.content:
            block.transfer(S)
        annot = {}
        for page, P in S.items():
            annot[page] = (P.pop('_annot'), P.pop('_paint_annot'))
            P['_annot'] = []
            P['_paint_annot'] = []
        S.annot.append(annot)
        

class Paragraph_block(Blockstyle):
    name = 'p'
    textfacing = True

    def __init__(self, * II, ** KII ):
        Blockstyle.__init__(self, * II, ** KII )
        self.implicit_ = None
    
    def layout(self, frames, BSTYLE):
        F = Tagcounter()
        leading = BSTYLE['leading']
        indent_range = BSTYLE['indent_range']
        D, SIGN, K = BSTYLE['indent']
        
        R_indent = BSTYLE['margin_right']
        
        i = 0
        l = 0
        
        LINES = []
        LIQUID = self.content
        total = len(self.content)
        while True:
            u, left, right, y, pn = frames.fit(leading)
            
            # calculate indentation
            if l in indent_range:
                if K:
                    INDLINE = cast_mono_line({'l': l, 'page': pn},
                        LIQUID[i : i + K + (not bool(l))], 
                        0,
                        PP,
                        F.copy()
                        )
                    L_indent = BSTYLE['margin_left'] + D + INDLINE['advance'] * SIGN
                else:
                    L_indent = BSTYLE['margin_left'] + D
            else:
                L_indent = BSTYLE['margin_left']

            # generate line objects
            x1 = left + L_indent
            x2 = right - R_indent
            if x1 > x2:
                x1, x2 = x2, x1
            # initialize line
            LINE = Glyphs_line({'observer': None, 'left': left, 'start': x1, 'y': y, 'u': u, 'l': l, 'page': pn, 'wheels': None}) # restore wheels later
            cast_liquid_line(LINE,
                    LIQUID[i : i + 1989], 
                    i, 
                    
                    x2 - x1, 
                    BSTYLE['leading'],
                    self,
                    F.copy(), 
                    
                    hyphenate = BSTYLE['hyphenate']
                    )

            # alignment
            if BSTYLE['align_to'] and LINE['GLYPHS']:
                searchtext = LIQUID[i : i + len(LINE['GLYPHS'])]
                ai = -1
                for aligner in '\t' + BSTYLE['align_to']:
                    try:
                        ai = searchtext.index(aligner)
                        break
                    except ValueError:
                        continue
                anchor = x1 + (x2 - x1) * BSTYLE['align']
                LINE['x'] = anchor - LINE['_X_'][ai]
            else:
                if not BSTYLE['align']:
                    LINE['x'] = x1
                else:
                    rag = LINE['width'] - LINE['advance']
                    LINE['x'] = x1 + rag * BSTYLE['align']

            # print counters
            if not l and BSTYLE['show_count'] is not None:
                wheelprint = cast_mono_line({'l': l, 'page': pn}, 
                                    BSTYLE['show_count'](WHEELS), 0, PP, F.copy())
                wheelprint['x'] = LINE['x'] - wheelprint['advance'] - BSTYLE['leading']*0.5
                LINE.merge(wheelprint)
            
            l += 1
            LINES.append(LINE)
            
            i = LINE['j']
            if i == total:
                break
            F = LINE['F']

        self._LINES = LINES
        self._UU = [line['u'] for line in LINES]
        self._search_j = [line['j'] for line in LINES]
        self.u = LINES[0]['u'] - leading

    def which(self, x, u):
        line = self._LINES[bisect(self._UU, u)]
        return ((line.I(x), None),)
    
    def _where(self, i):
        l = bisect(self._search_j, i)
        line = self._LINES[l]
        glyph = line['GLYPHS'][i - line['i']]
        return l, line, glyph[1] + line['x']
    
    def highlight(self, a=None, b=None):
        select = []
        if a is not None and b is not None:
            a, b = sorted((a, b))
        
        if a is None:
            l1 = 0
            first = self._LINES[0]
            leading = first['leading']
            x1 = first['left'] - leading
            
        else:
            l1, first, x1 = self._where(a)
            leading = first['leading']
        
        if b is None:
            l2 = len(self._LINES) - 1
            last = self._LINES[-1]
            x2 = last['start'] + last['width']

        else:
            l2, last, x2 = self._where(b)

        y2 = last['y']
        pn2 = last['page']
                
        if l1 == l2:
            select.append((first['y'], x1, x2, leading, first['page']))
        
        else:
            select.append((first['y'],  x1,             first['start'] + first['width'],    leading, first['page']))
            select.extend((line['y'],   line['start'],  line['start'] + line['width'],      leading, line['page']) for line in (self._LINES[l] for l in range(l1 + 1, l2)))
            select.append((last['y'],   last['start'],  x2,                                 leading, last['page']))

        return select

    def run_stats(self, spell):
        self.content.stats(spell)
        return self.content.word_count

    def transfer(self, S):
        for page, lines in ((p, list(ps)) for p, ps in groupby((line for line in self._LINES), key=lambda line: line['page'])):
            sorted_page = S[page]
            for line in lines:
                line.deposit(sorted_page)

members = (Meredith, Section, Paragraph_block)
