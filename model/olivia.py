from bisect import bisect
from itertools import groupby, chain

from state import noticeboard
from model.wonder import words
from model.cat import typeset_chained, typeset_liquid, Glyphs_line

class _Empty_F(object):
    def __init__(self):
        self.members = set()
    
    def __getitem__(self, i):
        return None

class Block(dict):
    def __init__(self, FLOW, top, bottom, left, right, PP):
        self._FLOW = FLOW
        self['x'] = left
        self['left'] = left
        self['right'] = right
        self['width'] = right - left
        self['y'] = bottom
        self['leading'] = bottom - top
        self['GLYPHS'] = [(-2, 0, bottom, _Empty_F(), None, right - left)]
        self['P_BREAK'] = True
        self['PP'] = PP

    def _handle(self, cr):
        ym = self['y'] - self['leading']/2
        r = self['right']
        cr.move_to(r + 6, ym + 20)
        cr.rel_line_to(6, -20)
        cr.rel_line_to(-6, -20)
        cr.rectangle(r, ym - 20, 2, 40)
        cr.rectangle(r + 4, ym - 20, 2, 40)
        cr.close_path()
        
    def collect_text(self):
        return list(chain.from_iterable(A.collect_text() for A in self._FLOW))
    
    def deposit(self, repository):
        for A in self._FLOW:
            A.deposit(repository)

def _deposit_misspellings(underscores, tract):
    for pair in tract.misspellings:
        u, v = pair[:2]

        u_l = tract._index_to_line(u)
        v_l = tract._index_to_line(v)
        u_x = tract._text_index_x(u, u_l)
        v_x = tract._text_index_x(v, v_l)
        
        first = tract._SLUGS[u_l]
        if not u_l - v_l:
                               # y, x1, x2
            underscores.append((first['y'], u_x, v_x, first['page']))
        
        else:
            last = tract._SLUGS[v_l]
            underscores.append((first['y'], u_x, first['GLYPHS'][-1][5] + first['x'], first['page']))
            underscores.extend((line['y'], line['x'], line['GLYPHS'][-1][5] + line['x'], line['page']) for line in tract._SLUGS[u_l + 1: v_l] if line['GLYPHS'])
            underscores.append((last['y'], last['x'], v_x, last['page']))

class Atomic_text(object):
    def __init__(self, text):
        self.text = text
        self._SLUGS = []

        # STATS
        self.word_count = '—'
        self.misspellings = []
        
    def _precompute_search(self):
        self._line_startindices = [line['i'] for line in self._SLUGS]
        self._line_yl = { cc: list(h[:2] for h in list(g)) for cc, g in groupby( ((LINE['y'], LINE['l'], LINE['c']) for LINE in self._SLUGS if LINE['GLYPHS']), key=lambda k: k[2]) }

    def cast(self, bounds, c, y):
        self._c = c
        self._SLUGS[:] = typeset_liquid(bounds, self.text, {'j': 0, 'l': -1, 'P_BREAK': True}, 0, y, c, False)
        if self._SLUGS:
            self.y = self._SLUGS[-1]['y']
        else:
            self.y = y
        self._precompute_search()
                
    def _target_row(self, y, c):
        try:
            yy, ll = zip( * self._line_yl[c])
        except KeyError:
            return self._SLUGS[-1]['l']
        # find the clicked line
        lineindex = None
        if y >= yy[-1]:
            lineindex = len(yy) - 1
        else:
            lineindex = bisect(yy, y)
        return ll[lineindex]

    ### FUNCTIONS USEFUL FOR DRAWING AND INTERFACE

    def paint_select(self, u, v):
        select = []
        u_l = self._index_to_line(u)
        v_l = self._index_to_line(v)
        
        u_l, v_l = sorted((u_l, v_l))
        u, v = sorted((u, v))
        u_x = self._text_index_x(u, u_l)
        v_x = self._text_index_x(v, v_l)
        
        first = self._SLUGS[u_l]
        if u_l == v_l:
                               # y, x1, x2
            select.append((first['y'], u_x, v_x, first['leading'], first['page']))
        
        else:
            last = self._SLUGS[v_l]
            select.append((first['y'], u_x, first['width'] + first['left'], first['leading'], first['page']))
            select.extend((line['y'], line['left'], line['width'] + line['left'], line['leading'], line['page']) for line in (self._SLUGS[l] for l in range(u_l + 1, v_l)))
            select.append((last['y'], last['left'], v_x, last['leading'], last['page']))

        return select

    # get line number given character index
    def _index_to_line(self, index):
        return bisect(self._line_startindices, index) - 1
    
    # get x position of specific glyph
    def _text_index_x(self, i, l):
        line = self._SLUGS[l]
        try:
            glyph = line['GLYPHS'][i - line['i']]
        except IndexError:
            glyph = line['GLYPHS'][-1]

        return glyph[1] + line['x']

    def line_indices(self, i):
        lineobject = self._SLUGS[self._index_to_line(i)]
        return lineobject['i'], lineobject['j'] - 1

    def line_at(self, i):
        return self._SLUGS[self._index_to_line(i)]

    def stats(self, spell=False):
        if spell:
            self.word_count, self.misspellings = words(self.text, spell=True)
        else:
            self.word_count = words(self.text)

    def I(self, x, y):
        return self._SLUGS[self._target_row(y, self._c)].I(x, y)
    
    def target_select(self, x, y, page, i):
        lineobject = self._SLUGS[self._target_row(y, self._c)]
        O = lineobject.I(x, y)
        if type(O) is not int:
            O = lineobject['i']
        
        return False, O

    def line_jump(self, i, direction):
        l = self._index_to_line(i)
        x = self._text_index_x(i, l)
        try:
            if direction: #down
                lineobject = next(S for S in self._SLUGS[l + 1:] if S['GLYPHS'])
            else:
                lineobject = next(S for S in reversed(self._SLUGS[:l]) if S['GLYPHS'])
        except StopIteration:
            return i
        O = lineobject.I(x, lineobject['y'] - lineobject['leading'])
        if type(O) is not int:
            O = lineobject['i']
        return O

    def collect_text(self):
        mods = list(chain.from_iterable(map(lambda Q: Q.collect_text(), filter(lambda S: type(S) is not Glyphs_line, self._SLUGS))))
        return [self] + mods

    def deposit(self, repository):
        for S in self._SLUGS:
            S.deposit(repository)

class Chained_text(Atomic_text):
    def __init__(self, text, channels):
        self.channels = channels
        self._sorted_pages = {}
        Atomic_text.__init__(self, text)
    
    def target(self, x, y, page, i):
        # chained text contains multiple channels
        c = self.channels.target_channel(x, y, page, 20)
        if c is None:
            if i is not None:
                c = self._SLUGS[self._index_to_line(i)]['c']
                imperfect = True
            else:
                return True, None, None, None
        else:
            imperfect = False
        
        lineobject = self._SLUGS[self._target_row(y, c)]
        
        ftx = self
        O = lineobject
        si = lineobject.I(x, y)
        
        if type(si) is not int:
            O = si
            ftx = O
            si = lineobject['i']
            
            while 1:
                O = O.I(x, y)
                if type(O) is int:
                    break
                else:
                    ftx = O
        else:
            O = si

        return imperfect, ftx, O, si

    def target_select(self, x, y, page, i):
        # chained text contains multiple channels
        c = self.channels.target_channel(x, y, page, 20)
        if c is None:
            if i is not None:
                c = self._SLUGS[self._index_to_line(i)]['c']
                imperfect = True
            else:
                return True, None
        else:
            imperfect = False
        
        lineobject = self._SLUGS[self._target_row(y, c)]
        
        O = lineobject.I(x, y)
        if type(O) is not int:
            O = lineobject['i']

        return imperfect, O
    
    def partial_recalculate(self, i):
        l = max(self._index_to_line(i) - 1, 0)
        # avoid recalculating lines that weren't affected
        del self._SLUGS[l + 1:]

        trace = self._SLUGS.pop()
        c = trace['c']
        y = trace['y'] - trace['leading']
        
        arguments = self.channels.channels, self.text, c, y
        if self._SLUGS:
            arguments += (self._SLUGS[-1],)
        self._SLUGS.extend(typeset_chained( * arguments))
        self._precompute_search()
        self._sorted_pages = {}

    def deep_recalculate(self):
        self._SLUGS[:] = typeset_chained(self.channels.channels, self.text)
        self._precompute_search()
        self._sorted_pages.clear()

    def paint_misspellings(self):
        tree = self.collect_text()
        underscores = []
        for tract in tree:
            _deposit_misspellings(underscores, tract)
        return underscores

    def extract_glyphs(self, refresh=False):
        if refresh:
            self._sorted_pages = {}

        if not self._sorted_pages:
            for page, pageslugs in ((p, list(ps)) for p, ps in groupby((line for line in self._SLUGS), key=lambda line: line['page'])):
                if page not in self._sorted_pages:
                    self._sorted_pages[page] = {'_annot': [], '_images': [], '_paint': [], '_paint_annot': []}
                sorted_page = self._sorted_pages[page]
                
                for line in pageslugs:
                    line.deposit(sorted_page)

        return self._sorted_pages
