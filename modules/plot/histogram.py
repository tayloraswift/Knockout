from itertools import chain
from .data import Data

_namespace = 'mod:hist'

class Bars(Data):
    nodename = _namespace + ':bars'
    ADNA = [('data', (), '1D'), ('color', '#ff3085', 'rgba')]
    
class Histogram(Data):
    nodename = _namespace
    ADNA = [('start', 0, 'float'), ('step', 1, 'float')]

    def unit(self, axes):
        start, dx = self.get_attributes()
        self._barsets = tuple(e.freeze_attrs() for e in self.filter_nodes(Bars, inherit=False))
        if self._barsets:
            if 'start' not in self.attrs:
                start = axes.X.a
            
            project = axes.project
            
            data_colors = tuple((tuple(B.data), B.color) for B in self._barsets)
            bins = max(len(D) for D, C in data_colors)
            P = []
            tide = [0] * bins
            for barset, color in data_colors:
                segments = []
                for i, height in enumerate(barset):
                    d1 = (start + i*dx, tide[i])
                    d2 = (d1[0] + dx, d1[1] + height)
                    p1 = project( * d1 )
                    p2 = project( * d2 )
                                   # x1   , x2 - x1      , y1   , y2 - y1
                    segments.append((p1[0], p2[0] - p1[0], p1[1], p2[1] - p1[1]))
                    tide[i] += height
                P.append((segments, color))
            
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
    
    def freeze(self, h, k):
        for barset in self._barsets:
            barset.freeze(h)
        self._points = [(tuple((x1*h, y1*k, xw*h, yw*k) for x1, xw, y1, yw in segments), color) for segments, color in self._unitpoints]

    def key(self):
        return chain.from_iterable(barset.key() for barset in self._barsets)
    
members = [Histogram, Bars]
