import bisect

from itertools import groupby

from state import noticeboard

from model.wonder import words, character, _breaking_chars

from model.cat import typeset_chained, Glyphs_line

class Flowing_text(object):
    def __init__(self, text, channels=None):
        self.text = text
        self.channels = channels
        
        self._SLUGS = []
        
        self._sorted_pages = {}
        
        # STATS
        self.word_count = '—'
        self.misspellings = []
        
    def _precompute_search(self):
        self._line_startindices = [line['i'] for line in self._SLUGS]
        self._line_yl = { cc: list(h[:2] for h in list(g)) for cc, g in groupby( ((LINE['y'], LINE['l'], LINE['c']) for LINE in self._SLUGS if LINE['GLYPHS']), key=lambda k: k[2]) }

    def _target_row(self, x, y, c):
        yy, ll = zip( * self._line_yl[c])
        # find the clicked line
        lineindex = None
        if y >= yy[-1]:
            lineindex = len(yy) - 1
        else:
            lineindex = bisect.bisect(yy, y)

        return ll[lineindex]
    
    def target_glyph(self, x, y, l=None, c=None):
        if l is None:
            l = self._target_row(x, y, c)
        return self._SLUGS[l].I(x, y)

    ### FUNCTIONS USEFUL FOR DRAWING AND INTERFACE
    
    def line_indices(self, l):
        return self._SLUGS[l]['i'], self._SLUGS[l]['j'] - 1

    def stats(self, spell=False):
        if spell:
            self.word_count, self.misspellings = words(self.text, spell=True)
        else:
            self.word_count = words(self.text)

class Chained_text(Flowing_text):
    def _dbuff(self, l):
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
    
    def extract_glyphs(self, refresh=False):
        if refresh:
            self._sorted_pages = {}

        if not self._sorted_pages:
            for page, pageslugs in ((p, list(ps)) for p, ps in groupby((line for line in self._SLUGS), key=lambda line: line['page'])):
                if page not in self._sorted_pages:
                    self._sorted_pages[page] = {'_annot': [], '_images': [], '_lines': ([], [])}
                sorted_page = self._sorted_pages[page]
                sorted_page['_lines'][0].extend(pageslugs)
                sorted_page['_lines'][1].extend(line['l'] for line in pageslugs)
                
                for line in pageslugs:
                    line.deposit(sorted_page)

        return self._sorted_pages
