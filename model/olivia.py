import bisect

from itertools import groupby

from state import noticeboard

from model.wonder import words, character, _breaking_chars

from model.cat import typeset_chained, Glyphs_line

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
            lineindex = bisect.bisect(yy, y)

        return ll[lineindex]
    
    def target_glyph(self, x, y, l=None, c=None):
        if l is None:
            l = self._target_row(y, c)
        return self._SLUGS[l].I(x, y)

    ### FUNCTIONS USEFUL FOR DRAWING AND INTERFACE

    def paint_select(self, u, v):
        select = []
        u_l = self.index_to_line(u)
        v_l = self.index_to_line(v)
        page = self._SLUGS[v_l]['page']
        
        u_l, v_l = sorted((u_l, v_l))
        u, v = sorted((u, v))
        u_x = self.text_index_x(u, u_l)
        v_x = self.text_index_x(v, v_l)
        
        first = self._SLUGS[u_l]
        if not u_l - v_l:
                               # y, x1, x2
            select.append((first['y'], u_x, v_x, first['leading'], first['page']))
        
        else:
            last = self._SLUGS[v_l]
            select.append((first['y'], u_x, first['width'] + first['x'], first['leading'], first['page']))
            select.extend((line['y'], line['x'], line['width'] + line['x'], line['leading'], line['page']) for line in (self._SLUGS[l] for l in range(u_l + 1, v_l)))
            select.append((last['y'], last['x'], v_x, last['leading'], last['page']))

        return select

    # get line number given character index
    def index_to_line(self, index):
        return bisect.bisect(self._line_startindices, index) - 1
    
    # get x position of specific glyph
    def text_index_x(self, i, l):
        line = self._SLUGS[l]
        try:
            glyph = line['GLYPHS'][i - line['i']]
        except IndexError:
            glyph = line['GLYPHS'][-1]

        return glyph[1] + line['x']

    def line_indices(self, l):
        return self._SLUGS[l]['i'], self._SLUGS[l]['j'] - 1

    def stats(self, spell=False):
        if spell:
            self.word_count, self.misspellings = words(self.text, spell=True)
        else:
            self.word_count = words(self.text)

    def I(self, x, y):
        c = self._SLUGS[0]['c']
        lineobject = self._SLUGS[self._target_row(y, c)]
        
        ftx = self
        O = lineobject
        while 1:
            O = O.I(x, y)
            if type(O) is int:
                break
            else:
                ftx = O
        return O
    
    def target_select(self, x, y, page, i):
        c = self._SLUGS[0]['c']
        lineobject = self._SLUGS[self._target_row(y, c)]
        
        O = lineobject.I(x, y)
        if type(O) is not int:
            O = lineobject['i']
        
        return False, O

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
                c = self._SLUGS[self.index_to_line(i)]['c']
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
                c = self._SLUGS[self.index_to_line(i)]['c']
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
    
    def _dbuff(self, i):
        l = self.index_to_line(i)
        # avoid recalculating lines that weren't affected
        del self._SLUGS[l + 1:]

        if type(self._SLUGS[l]) is Glyphs_line:
            l -= 1
            l = max(0, l)
            if type(self._SLUGS[l]) is Glyphs_line:
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
        underscores = []
        for pair in self.misspellings:
            u, v = pair[:2]

            u_l = self.index_to_line(u)
            v_l = self.index_to_line(v)
            u_x = self.text_index_x(u, u_l)
            v_x = self.text_index_x(v, v_l)
            
            first = self._SLUGS[u_l]
            if not u_l - v_l:
                                   # y, x1, x2
                underscores.append((first['y'], u_x, v_x, first['page']))
            
            else:
                last = self._SLUGS[v_l]
                underscores.append((first['y'], u_x, first['GLYPHS'][-1][5] + first['x'], first['page']))
                underscores.extend((line['y'], line['x'], line['GLYPHS'][-1][5] + line['x'], line['page']) for line in (self._SLUGS[l] for l in range(u_l + 1, v_l)))
                underscores.append((last['y'], last['x'], v_x, last['page']))
        return underscores

    def extract_glyphs(self, refresh=False):
        if refresh:
            self._sorted_pages = {}

        if not self._sorted_pages:
            for page, pageslugs in ((p, list(ps)) for p, ps in groupby((line for line in self._SLUGS), key=lambda line: line['page'])):
                if page not in self._sorted_pages:
                    self._sorted_pages[page] = {'_annot': [], '_images': []}
                sorted_page = self._sorted_pages[page]
                
                for line in pageslugs:
                    line.deposit(sorted_page)

        return self._sorted_pages
