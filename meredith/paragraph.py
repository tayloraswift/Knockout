from bisect import bisect
from itertools import groupby, chain
from math import inf as infinity

from meredith.box import Box
from meredith import datablocks
from olivia import Tagcounter
from meredith.styles import Blockstyle, block_styling_attrs

from layout.line import Glyphs_line, cast_liquid_line, cast_mono_line

from state.exceptions import LineOverflow

from edit.wonder import words

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
            section.layout(section['frames'])

    def transfer(self):
        if any(section.rebuilt for section in self.content) or not self._sorted_pages:
            self._sorted_pages.clear()
            self._sorted_pages.annot = []
            for section in self.content:
                section.transfer(self._sorted_pages)
        return self._sorted_pages

    def after(self, A):
        self._recalc_page()
    
    def add_section(self):
        self.content.append(Section({}, [Paragraph_block({}, Text(list('{new}')))]))
        self.layout_all()
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

    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        self._UU = []
    
    def layout(self, frames=None, b=0, u=0, cascade=False, overlay=None):
        calc_bstyle = datablocks.BSTYLES.project_b
        if frames is None:
            frames = self['frames']
        if overlay is not None:
            for block in self.content:
                block.implicit_ = overlay
        if b:
            frames.start(self.content[b - 1].u_bottom)
            gap = calc_bstyle(self.content[b - 1])['margin_bottom']
            wheels = self.content[b - 1].wheels
        else:
            frames.start(u)
            gap = -calc_bstyle(self.content[0])['margin_top']
            wheels = Wheels()
        
        UU = self._UU
        del UU[b:]
        halt = False
        for db, block in enumerate(self.content[b:]):
            BSTYLE = calc_bstyle(block)
            frames.space(gap + BSTYLE['margin_top'])
            gap = BSTYLE['margin_bottom']
            try:
                if not halt:
                    halt, wheels = block.layout(frames, BSTYLE, wheels, cascade and db, overlay)
            except LineOverflow:
                UU.append(block.u)
                for blk in self.content[b + db:]:
                    blk.erase()
                if self.__class__ is not Section:
                    raise LineOverflow
                else:
                    break
            UU.append(block.u)
        self.rebuilt = True
    
    def which(self, x, u, r=-1):
        if r:
            b = max(0, bisect(self._UU, u) - 1)
            block = self.content[b]
            return ((b, block), * block.which(x, u, r - 1))
        else:
            return ()

    def highlight_spelling(self):
        return chain.from_iterable(block.highlight_spelling() for block in self.content)
    
    def transfer(self, S):
        for block in self.content:
            block.transfer(S)

class Section(Plane):
    name = 'section'
    
    DNA  = [('repeat',      'int',    1),
            ('frames',    'frames',     '10,10 10,100 ; 100,10 100,100 ; 0')]

    def __init__(self, * II, ** KII ):
        Plane.__init__(self, * II, ** KII )
        
        if self['repeat'] > 1:
            pass
    
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

class Wheels(list):
    def __init__(self, dense = [0 for _ in range(13)], iso = {}):
        list.__init__(self, dense)
        self._iso = iso.copy()
    
    def increment(self, position, f):
        if f is None:
            return self
        else:
            W = self.copy()
            if position < len(W):
                W[position] = f(W[position])
                if position >= 0:
                    W[position + 1:] = (0 for _ in range(len(W) - position - 1))
            return W
    
    def __getitem__(self, i):
        if type(i) is not slice and i < 0:
            return self._iso.get(i, 0)
        else:
            return list.__getitem__(self, i)
    
    def __setitem__(self, i, v):
        if type(i) is not slice and i < 0:
            self._iso[i] = v
        else:
            list.__setitem__(self, i, v)
    
    def copy(self):
        return Wheels(self, self._iso)

class Blockelement(Blockstyle):
    planelevel = True
    
    IMPLY = {'class': 'body'}

    def __init__(self, * II, ** KII ):
        Blockstyle.__init__(self, * II, ** KII )
        self._OBSERVERLINES = []
        self._LINES = []
        
        self.implicit_ = None
        self.u = infinity
        
        self._load()
    
    def _load(self):
        pass

    def after(self, A):
        if A in block_styling_attrs:
            datablocks.BSTYLES.block_projections.clear()
            datablocks.BSTYLES.text_projections.clear()
        datablocks.DOCUMENT.layout_all()

    def which(self, x, u, r):
        return ()

    def where(self, address):
        if address:
            i, * address = address
            return self.content[i].where(address)
        else:
            return self._whole_location
    
    def layout(self, frames, BSTYLE, wheels, cascade, overlay):
        frames.save_u()
        u, left, right, y, c, pn = frames.fit(BSTYLE['leading'])
        
        frames.restore_u()
        if cascade and u - BSTYLE['leading'] == self.u:
            self.layout_observer(BSTYLE, wheels, self.line0)
            return True, self.wheels
        else:
            self.line0 = cast_mono_line({'l': 0, 'c': c, 'page': pn},
                            [], 
                            BSTYLE['leading'],
                            self,
                            Tagcounter())
            self.line0.update({'u': u, 'left': left, 'start': left, 'width': right - left, 'x': left, 'y': y})
            self.layout_observer(BSTYLE, wheels, self.line0)
            self.u = u - BSTYLE['leading']
            self.u_bottom = self._layout_block(frames, BSTYLE, cascade, overlay)
            return False, self.wheels
    
    def layout_observer(self, BSTYLE, wheels, LINE):
        self._OBSERVERLINES = []
        
        wheels = wheels.increment(BSTYLE['incr_place_value'], BSTYLE['incr_assign'])
        
        # print para flag
        flag = (-2, -BSTYLE['leading'], 0, LINE['fstyle'], LINE['F'], 0)
        self._OBSERVERLINES.append(Glyphs_line({'x': LINE['left'], 'y': LINE['y'], 'page': LINE['page'], 
                                    'GLYPHS': [flag], 'BLOCK': self, 'observer': []}))
        # print counters
        if BSTYLE['show_count'] is not None:
            
            wheelprint = cast_mono_line({'l': 0, 'c': LINE['c'], 'page': LINE['page']}, 
                                BSTYLE['show_count'](wheels), 0, self, LINE['F'])
            wheelprint['x'] = LINE['left'] + BSTYLE['margin_left'] - wheelprint['advance'] - BSTYLE['leading']*0.5
            wheelprint['y'] = LINE['y']
            self._OBSERVERLINES.append(wheelprint)
        
        self.left_edge = LINE['left'] - BSTYLE['leading']*0.5
        self._whole_location = -1, LINE, flag
        self.wheels = wheels

    def erase(self):
        self._LINES = []
        self._OBSERVERLINES = []
        self.u = infinity
    
    def transfer(self, S):
        raise NotImplementedError

    def _cursor(self, i):
        l = 0
        line = self.line0
        if i == -1:
            x = line['left']
        else:
            x = line['left'] + line['width']
        return l, line, x
    
    def highlight(self, a, b):
        try:
            l1, first, x1 = self._cursor(a)
            l2, last, x2 = self._cursor(b)
        except IndexError:
            return []
        
        return [(first['y'] - first['leading'], x1, x2, self.u - self.u_bottom, first['page'])]
    
class Paragraph_block(Blockelement):
    name = 'p'
    textfacing = True
    
    def _layout_block(self, frames, BSTYLE, cascade, overlay):
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
        while True:
            u, left, right, y, c, pn = frames.fit(leading)
            
            # calculate indentation
            if l in indent_range:
                if K:
                    INDLINE = cast_mono_line({'l': l, 'c': c, 'page': pn},
                        LIQUID[i : i + K + (not bool(l))], 
                        0,
                        self,
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
            LINE = Glyphs_line({'observer': [], 'left': left, 'start': x1, 'y': y, 'c': c, 'u': u, 'l': l, 'page': pn})
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
            
            l += 1
            LINES.append(LINE)
            
            i = LINE['j']
            if i == total:
                break
            
            F = LINE['F']


        self._LINES = LINES
        self._UU = [line['u'] - leading for line in LINES]
        self._search_j = [line['j'] for line in LINES]
        # shift left edge
        self.left_edge = LINES[0]['x'] - BSTYLE['leading']*0.5
        return LINES[-1]['u']

    def erase(self):
        self._LINES = []
        self._OBSERVERLINES = []
        self._UU = []
        self._search_j = []
        self.u = infinity
    
    def insert(self, at, text):
        self.content[at:at] = text
        n = len(text)
        self.content.misspellings = [pair if pair[1] < at else (pair[0] + n, pair[1] + n, pair[2]) if pair[0] > at else (pair[0], pair[1] + n, pair[2]) for pair in self.content.misspellings]
    
    def delete(self, a, b):
        del self.content[a:b]
        n = a - b
        self.content.misspellings = [pair if pair[1] < a else (pair[0] + n, pair[1] + n, pair[2]) if pair[0] > b else (0, 0, None) for pair in self.content.misspellings]
    
    def bridge(self, I, J, positive, negative, sign):
        paragraph = self.content
        S = paragraph[I:J]
        #DA = 0

        P_2 = len(paragraph)

        if sign:
            TAGS = (negative, positive)
            paragraph.insert(0, TAGS[0].copy())
            #DA += 1
            
            P_2 += 1
            I += 1
            J += 1
        else:
            TAGS = (positive, negative)
        
        CAP = (type(TAGS[0]), type(TAGS[1]))
        
        # if selection falls on top of range
        if I > 0 and type(paragraph[I - 1]) is CAP[0]:
            I -= next(i for i, c in enumerate(paragraph[I - 2::-1]) if type(c) is not CAP[0]) + 1

        if J < P_2 and type(paragraph[J]) is CAP[1]:
            J += next(i for i, c in enumerate(paragraph[J + 1:]) if type(c) is not CAP[1]) + 1

        ftag = TAGS[0]['class']
        ftags = [(i, type(e)) for i, e in enumerate(paragraph) if type(e) in CAP and e['class'] == ftag]
        if sign:
            ftags += [(P_2 + 1, CAP[1]), (None, None)]
        else:
            ftags += [(None, None)]
        
        pairs = []
        for i in reversed(range(len(ftags) - 2)):
            if (ftags[i][1], ftags[i + 1][1]) == CAP:
                pairs.append((ftags[i][0], ftags[i + 1][0]))
                del ftags[i:i + 2]
        
        # ERROR CHECKING
        if ftags != [(None, None)]:
            print ('INVALID TAG SEQUENCE, REMNANTS: ' + str(ftags))
        
        instructions = []
        drift_i = 0
        drift_j = 0

        for pair in pairs:
            if pair[1] <= I or pair[0] >= J:
                pass
            elif pair[0] >= I and pair[1] <= J:
                instructions += [(pair[0], False), (pair[1], False)]
                #DA -= 2
                
                drift_j += -2
            elif I < pair[1] <= J:
                instructions += [(pair[1], False), (I, True, TAGS[1].copy())]
                if not sign:
                    drift_i += 1
            elif I <= pair[0] < J:
                instructions += [(pair[0], False), (J, True, TAGS[0].copy())]
                if not sign:
                    drift_j += -1
            elif pair[0] < I and pair[1] > J:
                instructions += [(I, True, TAGS[1].copy()), (J, True, TAGS[0].copy())]
                #DA += 2
                
                if sign:
                    drift_j += 2
                else:
                    drift_i += 1
                    drift_j += 1

        if instructions:
            activity = True
            
            instructions.sort(reverse=True)
            for instruction in instructions:
                if instruction[1]:
                    paragraph.insert(instruction[0], instruction[2])
                else:
                    del paragraph[instruction[0]]
        else:
            activity = False
        
        if sign:
            if paragraph[0] == TAGS[0].copy():
                del paragraph[0]
                #DA -= 1
                
                drift_i -= 1
                drift_j -= 1

            else:
                paragraph.insert(0, TAGS[1].copy())
                #DA += 1
                
                drift_j += 1

        
        if activity:
            I += drift_i
            J += drift_j
            
            self.u = infinity
            paragraph.stats(spell=True)
            return True, I, J
        else:
            return False, I, J

    def which(self, x, u, r):
        if r:
            l = max(0, bisect(self._UU, u) - 1)
            if l or r > 0 or x > self.left_edge:
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
        for page, lines in ((p, list(ps)) for p, ps in groupby(chain(self._OBSERVERLINES, self._LINES), key=lambda line: line['page'])):
            sorted_page = S[page]
            for line in lines:
                line.deposit(sorted_page)

    def copy_empty(self):
        if str(self['class']) != 'body':
            A = {'class': self.attrs['class']}
        else:
            A = {}
        return self.__class__(A, Text())

members = (Meredith, Section, Paragraph_block)
