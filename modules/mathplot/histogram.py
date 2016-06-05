from itertools import chain, groupby
from .data import Data

_namespace = 'mod:hist'

def _rectangle(p1, p2):
    return p1, (p1[0], p2[1]), p2, (p2[0], p1[1])

class Bars(Data):
    name = _namespace + ':bars'
    DNA = Data.DNA + [('data', '1D', ()), ('color', 'rgba', '#ff3085'), ('colorneg', 'rgba', '#ff5040'), ('key', 'bool', True)]

    def __init__(self, * I, ** KI):
        Data.__init__(self, * I, ** KI)
        if 'colorneg' not in self.attrs:
            self['colorneg'] = self['color']
            self._bi = False
        else:
            self._bi = True

    def paint_key(self, cr):
        if self._bi:
            height = self._key_height*0.5
            cr.set_source_rgba( * self['colorneg'] )
            cr.rectangle(0, height, 4, height)
            cr.fill()
        else:
            height = self._key_height
        cr.set_source_rgba( * self['color'] )
        cr.rectangle(0, 0, 4, height)
        cr.fill()
        
class Histogram(Data):
    name = _namespace
    DNA = Data.DNA + [('start', 'float', 0), ('step', 'float', 1)]

    def compact(self, system, height):
        start = self['start']
        dx = self['step']
        self._barsets = tuple(self.filter_nodes(Bars))
        if self._barsets:
            if 'start' not in self.attrs:
                start = system[0]['range'][0]
            
            to = system.to
            
            data_colors = tuple((tuple(B['data']), B['color'], B['colorneg']) for B in self._barsets)
            bins = max(len(D[0]) for D in data_colors)
            P = []
            tide = [0] * bins
            for barset, color, colorneg in data_colors:
                for sign, G in groupby(enumerate(barset), lambda k: k[1] >= 0):
                    segments = []
                    for i, k in G:
                        d1 = (start + i*dx, tide[i])
                        d2 = (d1[0] + dx, d1[1] + k)
                        segments.append(tuple((x, y*height) for x, y in (to( * P ) for P in _rectangle(d1, d2))))
                        tide[i] += k
                    if sign:
                        P.append((segments, color))
                    else:
                        P.append((segments, colorneg))
            
            self._compact = P
        else:
            self._compact = []
    
    def paint(self, cr):
        for barset, color in self._inflated:
            cr.set_source_rgba( * color )
            for P1, P2, P3, P4 in barset:
                cr.move_to( * P1 )
                cr.line_to( * P2 )
                cr.line_to( * P3 )
                cr.line_to( * P4 )
                cr.close_path()
            cr.fill()
    
    def inflate(self, width, * I ):
        self._inflated = [(tuple(tuple((x*width, y) for x, y in poly) for poly in segments), color) for segments, color in self._compact]
        return (), (self.paint,), ()

    def get_legend(self):
        return chain.from_iterable(barset.get_legend() for barset in self._barsets)
    
members = [Histogram, Bars]
