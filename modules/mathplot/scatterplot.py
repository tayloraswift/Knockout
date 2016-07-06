from math import pi, sqrt
from .data import Data

class Scatterplot(Data):
    name = 'mod:scatter'
    DNA = Data.DNA + [('data', 'multi_D', ()), ('color', 'rgba', '#ff3085'), ('radius', 'float', 2)]

    def compact(self, system, height):
        to = system.to
        self._compact = [(x, y*height) for x, y in (to( * coord ) for coord in self['data'])]

    def inflate(self, width, * I ):
        self._inflated = [(x*width, y) for x, y in self._compact]
        return (), (self.paint,), ()
    
    def paint(self, cr):
        cr.set_source_rgba( * self['color'] )
        circle_t = 2*pi
        r = self['radius']
        for x, y in self._inflated:
            cr.move_to(x, y)
            cr.arc(x, y, r, 0, circle_t)
            cr.close_path()
        cr.fill()

class Bubbleplot(Data):
    name = 'mod:bubble'
    DNA = Data.DNA + [('data', 'multi_D', ()), ('color', 'rgba', '#ff3085'), ('radius', ('f', ('x',)), lambda a: sqrt(abs(a)))]

    def compact(self, system, height):
        to = system.to
        size = self['radius']
        self._compact = [((x, y*height), r) for (x, y), r in ((to( * coord[:-1] ), size(coord[-1])) if len(coord) > 2 else (to( * coord ), size(-1)) for coord in self['data'])]

    def inflate(self, width, * I ):
        self._inflated = [((x*width, y), r) for (x, y), r in self._compact]
        return (), (self.paint,), ()
    
    def paint(self, cr):
        cr.set_source_rgba( * self['color'] )
        circle_t = 2*pi
        for (x, y), size in self._inflated:
            cr.move_to(x, y)
            cr.arc(x, y, size, 0, circle_t)
            cr.close_path()
            cr.fill()

members = [Scatterplot, Bubbleplot]
