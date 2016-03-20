from itertools import chain, groupby
from .data import Data

_namespace = 'mod:hist'

def _rectangle(p1, p2):
    return p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1]

class Bars(Data):
    name = _namespace + ':bars'
    ADNA = [('data', (), '1D'), ('color', '#ff3085', 'rgba'), ('colorneg', '#ff5040', 'rgba'), ('key', True, 'bool')]

    def __init__(self, * args, ** kwargs):
        Data.__init__(self, * args, ** kwargs)
        if 'colorneg' not in self.attrs:
            self['colorneg'] = self['color']
            self._bi = False
        else:
            self._bi = True
    
    def _key_icon(self, cr, k1, k2):
        height = (k2 - k1)
        if self._bi:
            height = height*0.5
            cr.set_source_rgba( * self['colorneg'] )
            cr.rectangle(self._right, k1 + height, -4, height)
            cr.fill()
        cr.set_source_rgba( * self['color'] )
        cr.rectangle(self._right, k1, -4, height)
        cr.fill()
        
class Histogram(Data):
    name = _namespace
    ADNA = [('start', 0, 'float'), ('step', 1, 'float'), ('key', True, 'bool')]

    def unit(self, axes):
        start = self['start']
        dx = self['step']
        self._barsets = tuple(self.filter_nodes(Bars, inherit=False))
        if self._barsets:
            if 'start' not in self.attrs:
                start = axes[0].a
            
            fit = axes.fit
            
            data_colors = tuple((tuple(B['data']), B['color'], B['colorneg']) for B in self._barsets)
            bins = max(len(D[0]) for D in data_colors)
            P = []
            tide = [0] * bins
            for barset, color, colorneg in data_colors:
                for sign, G in groupby(enumerate(barset), lambda k: k[1] >= 0):
                    segments = []
                    for i, height in G:
                        d1 = (start + i*dx, tide[i])
                        d2 = (d1[0] + dx, d1[1] + height)
                        segments.append((fit( * d1 ), fit( * d2 )))
                        tide[i] += height
                    if sign:
                        P.append((segments, color))
                    else:
                        P.append((segments, colorneg))
            
            self._unitpoints = P
        else:
            self._unitpoints = []
        return self
    
    def draw(self, cr):
        for barset, color in self._points:
            cr.set_source_rgba( * color )
            for rectangle in barset:
                cr.rectangle( * rectangle )
            cr.fill()
    
    def freeze(self, axes):
        for barset in self._barsets:
            barset.freeze(axes.h)
        project = axes.project
        self._points = [(tuple(_rectangle(project( * p1 ), project( * p2 )) for p1, p2 in segments), color) for segments, color in self._unitpoints]

    def key(self):
        if self['key']:
            return chain.from_iterable(barset.key() for barset in self._barsets)
        else:
            return ()
    
members = [Histogram, Bars]
