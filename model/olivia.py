from bisect import bisect
from itertools import groupby, chain

from state import noticeboard
from model.wonder import words

from model.cat import typeset_chained, typeset_liquid, Glyphs_line
from elements.elements import Block_element

class _Empty_F(object):
    def __init__(self):
        self.members = set()
    
    def __getitem__(self, i):
        return None

class Inline(object):
    def __init__(self, lines, width, A, D):
        self.LINES = lines
        self.width = width
        self.ascent = A
        self.descent = D
    
    def deposit_glyphs(self, repository, x, y):
        for line in self.LINES:
            line.deposit(repository, x, y)

class Block(dict):
    def __init__(self, COMPOSITIONS, top, bottom, left, right, PP):
        self._COMPOSITIONS = COMPOSITIONS
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
    
    # search functions
    def deep_search(self, x, y):
        i = self.target(x, y)
        if i is not None:
            CMP = self._COMPOSITIONS[i]
            return ( * CMP.deep_search(x, y), i)
        else:
            return None
    
    def collect_text(self):
        return list(chain.from_iterable(A.collect_text() for A in self._COMPOSITIONS))
    
    def deposit(self, repository):
        for A in self._COMPOSITIONS:
            A.deposit(repository)

class Composition(object):
    def __init__(self, manuscript):
        self.manuscript = manuscript
        self.LINES = []
        
    def pack(self, channel, text, c, y, overlay=None):
        self.LINES[:] = typeset_liquid(channel, text, {'j': 0, 'l': -1, 'P_BREAK': True}, 0, y, c, overlay=overlay)
        if self.LINES:
            self.y = self.LINES[-1]['y']
        else:
            self.y = y
        self._precompute_search()
    
    def _precompute_search(self):
        self._line_startindices = [line['i'] for line in self.LINES]
        self._line_y, self._line_l = zip( * ((LINE['y'], LINE['l']) for LINE in self.LINES if LINE['GLYPHS']) )

    def _target_row(self, y, * args):
        if y >= self._line_y[-1]:
            l = len(self._line_y) - 1
        else:
            l = bisect(self._line_y, y)
        return self._line_l[l]

    # get line number given character index
    def _index_to_line(self, index):
        return bisect(self._line_startindices, index) - 1
    
    # get x position of specific glyph
    def _text_index_x(self, i, l):
        line = self.LINES[l]
        try:
            glyph = line['GLYPHS'][i - line['i']]
        except IndexError:
            glyph = line['GLYPHS'][-1]

        return glyph[1] + line['x']

    def paint_select(self, u, v):
        select = []
        u_l = self._index_to_line(u)
        v_l = self._index_to_line(v)
        
        u_l, v_l = sorted((u_l, v_l))
        u, v = sorted((u, v))
        u_x = self._text_index_x(u, u_l)
        v_x = self._text_index_x(v, v_l)
        
        first = self.LINES[u_l]
        if u_l == v_l:
                               # y, x1, x2
            select.append((first['y'], u_x, v_x, first['leading'], first['page']))
        
        else:
            last = self.LINES[v_l]
            select.append((first['y'], u_x, first['width'] + first['left'], first['leading'], first['page']))
            select.extend((line['y'], line['left'], line['width'] + line['left'], line['leading'], line['page']) for line in (self.LINES[l] for l in range(u_l + 1, v_l)))
            select.append((last['y'], last['left'], v_x, last['leading'], last['page']))

        return select

    def paint_misspellings(self, misspellings):
        underscores = []
        for pair in misspellings:
            u, v = pair[:2]

            u_l = self._index_to_line(u)
            v_l = self._index_to_line(v)
            u_x = self._text_index_x(u, u_l)
            v_x = self._text_index_x(v, v_l)
            
            first = self.LINES[u_l]
            if not u_l - v_l:
                                   # y, x1, x2
                underscores.append((first['y'], u_x, v_x, first['page']))
            
            else:
                last = self.LINES[v_l]
                underscores.append((first['y'], u_x, first['GLYPHS'][-1][5] + first['x'], first['page']))
                underscores.extend((line['y'], line['x'], line['GLYPHS'][-1][5] + line['x'], line['page']) for line in self.LINES[u_l + 1: v_l] if line['GLYPHS'])
                underscores.append((last['y'], last['x'], v_x, last['page']))
        return underscores
    
    def line_indices(self, i):
        lineobject = self.LINES[self._index_to_line(i)]
        return lineobject['i'], lineobject['j'] - 1

    def line_at(self, i):
        return self.LINES[self._index_to_line(i)]

    # search functions
    def deep_search(self, x, y, * args):
        item = self.LINES[self._target_row(y, * args)]
        if type(item) is Glyphs_line:
            return self, item.I(x, y)
        else:
            OI = item.deep_search(x, y)
            if OI is None:
                return self, item['i']
            else:
                return ( * OI, item['i'])
    
    def shallow_search(self, x, y, * args):
        item = self.LINES[self._target_row(y, * args)]
        if type(item) is Glyphs_line:
            return item.I(x, y)
        else:
            return item['i']

    def line_jump(self, i, direction):
        l = self._index_to_line(i)
        x = self._text_index_x(i, l)
        try:
            if direction: #down
                item = next(S for S in self.LINES[l + 1:] if S['GLYPHS'])
            else:
                item = next(S for S in reversed(self.LINES[:l]) if S['GLYPHS'])
        except StopIteration:
            return i
        
        if type(item) is Glyphs_line:
            return item.I(x, -1)
        else:
            return item['i']

    def collect_text(self):
        mods = list(chain.from_iterable(map(lambda Q: Q.collect_text(), filter(lambda S: type(S) is not Glyphs_line, self.LINES))))
        return [self] + mods

    def deposit(self, repository):
        for S in self.LINES:
            S.deposit(repository)
    
class _Chained_composition(Composition):
    def pack(self, channels, text):
        self.LINES = typeset_chained(channels, text)
        self._precompute_search()

    def pack_partial(self, channels, text, i):
        l = max(self._index_to_line(i) - 1, 0)
        # avoid recalculating lines that weren't affected
        del self.LINES[l + 1:]

        trace = self.LINES.pop()
        c = trace['c']
        y = trace['y'] - trace['leading']
        
        arguments = channels, text, c, y
        if self.LINES:
            arguments += (self.LINES[-1],)
        self.LINES.extend(typeset_chained( * arguments))
        self._precompute_search()
    
    def _precompute_search(self):
        self._line_startindices = [line['i'] for line in self.LINES]
        self._line_yl = { cc: list(h[:2] for h in g) for cc, g in groupby( ((LINE['y'], LINE['l'], LINE['c']) for LINE in self.LINES if LINE['GLYPHS']), key=lambda k: k[2]) }

    def _target_row(self, y, c):
        try:
            yy, ll = zip( * self._line_yl[c] )
        except KeyError:
            return self.LINES[-1]['l']
        # find the clicked line
        lineindex = None
        if y >= yy[-1]:
            l = len(yy) - 1
        else:
            l = bisect(yy, y)
        return ll[l]

class Atomic_text(object):
    def __init__(self, text):
        self.text = text

        # STATS
        self.word_count = '—'
        self.misspellings = []
        self.stats(True)
    
    def stats(self, spell=False):
        if spell:
            self.word_count, self.misspellings = words(self.text, spell=True)
        else:
            self.word_count = words(self.text)

class Chained_text(Atomic_text):
    sign = '<section>\n'
    def __init__(self, text, channels):
        self.channels = channels
        self._sorted_pages = {}
        Atomic_text.__init__(self, text)
        
        self.composition = _Chained_composition(self)

    def partial_recalculate(self, i):
        self.composition.pack_partial(self.channels.channels, self.text, i)
        self._sorted_pages.clear()

    def deep_recalculate(self):
        self.composition.pack(self.channels.channels, self.text)
        self._sorted_pages.clear()

    def paint_misspellings(self):
        return chain.from_iterable(CMP.paint_misspellings(CMP.manuscript.misspellings) for CMP in self.composition.collect_text())
    
    def extract_glyphs(self, refresh=False):
        if refresh:
            self._sorted_pages = {}

        if not self._sorted_pages:
            for page, pageslugs in ((p, list(ps)) for p, ps in groupby((line for line in self.composition.LINES), key=lambda line: line['page'])):
                if page not in self._sorted_pages:
                    self._sorted_pages[page] = {'_annot': [], '_images': [], '_paint': [], '_paint_annot': []}
                sorted_page = self._sorted_pages[page]
                
                for line in pageslugs:
                    line.deposit(sorted_page)

        return self._sorted_pages

class Repeat_text(Chained_text):
    sign = '<section repeat="True">\n'
    def __init__(self, text, channels):
        Chained_text.__init__(self, text, channels)
        self.start = 1
        self.until = 13
        self.repeats = [self.composition]
        self.repeats.extend(_Chained_composition(self) for _ in range(self.until - self.start))
        
        ic = self.channels.channels
        self.channel_repeats = [[C.shallow_copy_to_page(k) for C in ic] for k in range(self.start, self.until + 1)]

    def deep_recalculate(self):
        for R, C in zip(self.repeats, self.channel_repeats):
            R.pack(C, self.text)
        self._sorted_pages.clear()

    def partial_recalculate(self, i):
        for R, C in zip(self.repeats, self.channel_repeats):
            R.pack_partial(C, self.text, i)
        self._sorted_pages.clear()
    
    def extract_glyphs(self, refresh=False):
        if refresh:
            self._sorted_pages = {}

        if not self._sorted_pages:
            for p, pageslugs in enumerate(R.LINES for R in self.repeats):
                page = p + self.start
                self._sorted_pages[page] = {'_annot': [], '_images': [], '_paint': [], '_paint_annot': []}
                for line in pageslugs:
                    line.deposit(self._sorted_pages[page])

        return self._sorted_pages
