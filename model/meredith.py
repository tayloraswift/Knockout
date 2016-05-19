from bisect import bisect
from itertools import groupby, chain
from math import inf as infinity

from elements.box import Box
from elements.style import Blockstyle
from elements import datablocks
from elements.datatypes import Tagcounter

from model.lines import Glyphs_line, cast_liquid_line

from state.exceptions import LineOverflow

class Sorted_pages(dict):
    def __missing__(self, key):
        self[key] = {'_annot': [], '_images': [], '_paint': [], '_paint_annot': []}
        return self[key]

class Meredith(Box):
    name = 'body'
    DNA  = [('width',   'int',  816),
            ('height',  'int',  1056),
            ('dual',    'bool', False),
            ('grid',    'pagegrid', '')]
    
    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        self._sorted_pages = Sorted_pages()
    
    def layout_all(self):
        self._recalc_page()
        self._sorted_pages.clear()
        for section in self.content:
            section.layout()

    def transfer(self):
        if any(section.rebuilt for section in self.content) or not self._sorted_pages:
            self._sorted_pages.clear()
            self._sorted_pages.annot = []
            for section in self.content:
                section.transfer(self._sorted_pages)
        return self._sorted_pages

    # Page functions
    
    def _recalc_page(self):
        self._HALFGAP = int(50)
        self._WIDTH_HALFGAP = self['width'] + self._HALFGAP
        self._HEIGHT_HALFGAP = self['height'] + self._HALFGAP
    
    def gutter_horizontal(self, x, y):
        if (-5 < x < self['width'] + 5) and (-20 <= y <= -10 or self['height'] + 10 <= y <= self['height'] + 20):
            return True
        else:
            return False

    def gutter_vertical(self, x, y):
        if (-5 < y < self['height'] + 5) and (-20 <= x <= -10 or self['width'] + 10 <= x <= self['width'] + 20):
            return True
        else:
            return False
    
    def XY_to_page(self, x, y):
        if self['dual']:
            E = int((y + self._HALFGAP) // self._HEIGHT_HALFGAP) * 2
            if x > self._WIDTH_HALFGAP:
                return E
            else:
                return E - 1
        else:
            return int((y + self._HALFGAP) // self._HEIGHT_HALFGAP)
    
    def normalize_XY(self, x, y, pp):
        if self['dual']:
            y -= (pp + 1)//2 * self._HEIGHT_HALFGAP
            if pp % 2 == 0:
                x -= self._WIDTH_HALFGAP
            return x, y
        else:
            return x, y - pp * self._HEIGHT_HALFGAP
    
    def map_X(self, x, pp):
        if self['dual']:
            return x + self._WIDTH_HALFGAP * ( not (pp % 2))
        else:
            return x

    def map_Y(self, y, pp):
        if self['dual']:
            return y + (pp + 1)//2 * self._HEIGHT_HALFGAP
        else:
            return y + pp * self._HEIGHT_HALFGAP

class Plane(Box):
    name = '_plane_'
    plane = True

    def which(self, x, u, r=-1):
        if r:
            b = max(0, bisect(self._UU, u) - 1)
            block = self.content[b]
            return ((b, block), * block.which(x, u, r - 1))
        else:
            return ()

    def where(self, address):
        i, * address = address
        return self.content[i].where(address)

class Section(Plane):
    name = 'section'
    
    DNA  = [('repeat',      'int set',    ''),
            ('frames',    'frames',     '')]

    def __init__(self, * II, ** KII ):
        Plane.__init__(self, * II, ** KII )
        self._UU = []
    
    def layout(self, b=0, cascade=False):
        calc_bstyle = datablocks.BSTYLES.project_b
        frames = self['frames']
        if b:
            frames.start(self.content[b].u)
        else:
            frames.start(0)
        BSTYLE = calc_bstyle(self.content[b])
        self.content[b].layout(frames, BSTYLE)
        gap = BSTYLE['margin_bottom']
        
        UU = self._UU
        del UU[b:]
        UU.append(self.content[b].u)
        halt = False
        for db, block in enumerate(self.content[b + 1:]):
            if not halt:
                BSTYLE = calc_bstyle(block)
                frames.space(gap + BSTYLE['margin_top'])
                gap = BSTYLE['margin_bottom']
                halt = block.layout(frames, BSTYLE, cascade)
                if halt == -1:
                    UU.append(block.u)
                    for blk in self.content[b + 2 + db:]:
                        blk.erase()
                    break
            UU.append(block.u)
        self.rebuilt = True
    
    def transfer(self, S):
        for block in self.content:
            block.transfer(S)
        annot = {}
        for page, P in S.items():
            annot[page] = (P.pop('_annot'), P.pop('_paint_annot'))
            P['_annot'] = []
            P['_paint_annot'] = []
        S.annot.append(annot)
        self.rebuilt = False

    def highlight_spelling(self):
        return chain.from_iterable(block.highlight_spelling() for block in self.content)

class Paragraph_block(Blockstyle):
    name = 'p'
    textfacing = True

    def __init__(self, * II, ** KII ):
        Blockstyle.__init__(self, * II, ** KII )
        self.implicit_ = None
        self.u = infinity
    
    def insert(self, text, at):
        self.content[at:at] = text
        n = len(text)
        self.content.misspellings = [pair if pair[1] < at else (pair[0] + n, pair[1] + n, pair[2]) if pair[0] > at else (pair[0], pair[1] + n, pair[2]) for pair in self.content.misspellings]
    
    def layout(self, frames, BSTYLE, cascade=False):
        F = Tagcounter()
        leading = BSTYLE['leading']
        indent_range = BSTYLE['indent_range']
        D, SIGN, K = BSTYLE['indent']
        
        R_indent = BSTYLE['margin_right']
        
        i = 0
        l = 0
        
        LINES = []
        LIQUID = self.content
        total = len(LIQUID) + 1 # for imaginary </p> cap
        
        try:
            u, left, right, y, c, pn = frames.fit(leading)
            if cascade and u - leading == self.u:
                return True
            else:
                self.u = u - leading
        except LineOverflow:
            self.erase()
            return -1
        
        while True:
            
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
            LINE = Glyphs_line({'observer': [], 'left': left, 'start': x1, 'y': y, 'c': c, 'u': u, 'l': l, 'page': pn, 'wheels': None}) # restore wheels later
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
            
            try:
                u, left, right, y, c, pn = frames.fit(leading)
            except LineOverflow:
                self._polish(LINES)
                return -1
            F = LINE['F']

        self._polish(LINES)
        return False

    def _polish(self, LINES):
        leading = LINES[0]['leading']
        flag = (-2, -leading, 0, LINES[0]['fstyle'], LINES[0]['F'], 0)
        LINES[0]['observer'].append(flag)
        self._left_edge = LINES[0]['left'] - leading*0.5
        self._LINES = LINES
        self._UU = [line['u'] - leading for line in LINES]
        self._search_j = [line['j'] for line in LINES]
        
        self._whole_location = -1, self._LINES[0], flag

    def erase(self):
        self._LINES = []
        self._UU = []
        self._search_j = []
        self.u = infinity

    def which(self, x, u, r):
        if r:
            l = max(0, bisect(self._UU, u) - 1)
            if l or r > 0 or x > self._left_edge:
                line = self._LINES[l]
                return ((line.I(x), None),)
        return ()
    
    def where(self, address):
        if address:
            l = bisect(self._search_j, address[0])
            line = self._LINES[l]
            glyph = line['GLYPHS'][address[0] - line['i']]
            return l, line, glyph
        else:
            return self._whole_location
    
    def _cursor(self, i):
        if i >= 0:
            l, line, glyph = self.where((i,))
            return l, line, glyph[1] + line['x']
        elif i == -1:
            l = 0
            line = self._LINES[0]
            x = line['left'] - line['leading']
        else:
            l = len(self._LINES) - 1
            line = self._LINES[l]
            x = line['start'] + line['width']
        return l, line, x
    
    def highlight(self, a, b):
        select = []

        if a != -1 and b != -2:
            a, b = sorted((a, b))
        
        try:
            l1, first, x1 = self._cursor(a)
            l2, last, x2 = self._cursor(b)
        except IndexError:
            return select
        
        leading = first['leading']
        y2 = last['y']
        pn2 = last['page']
                
        if l1 == l2:
            select.append((first['y'], x1, x2, leading, first['page']))
        
        else:
            select.append((first['y'],  x1,             first['start'] + first['width'],    leading, first['page']))
            select.extend((line['y'],   line['start'],  line['start'] + line['width'],      leading, line['page']) for line in (self._LINES[l] for l in range(l1 + 1, l2)))
            select.append((last['y'],   last['start'],  x2,                                 leading, last['page']))

        return select

    def highlight_spelling(self):
        select = []
        if self._LINES:
            for a, b, word in self.content.misspellings:
                try:
                    l1, first, x1 = self._cursor(a)
                    l2, last, x2 = self._cursor(b)
                except IndexError:
                    continue
                y2 = last['y']
                pn2 = last['page']
                        
                if l1 == l2:
                    select.append((first['y'], x1, x2, first['page']))
                
                else:
                    select.append((first['y'],  x1,             first['GLYPHS'][-1][5] + first['x'],    first['page']))
                    select.extend((line['y'],   line['start'],  line['GLYPHS'][-1][5] + line['x'],      line['page']) for line in (self._LINES[l] for l in range(l1 + 1, l2)))
                    select.append((last['y'],   last['start'],  x2,                                     last['page']))
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
