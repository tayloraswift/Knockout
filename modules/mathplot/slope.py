from math import sqrt

from .data import Data

class Slope(Data):
    name = 'mod:plot:slope'
    DNA = Data.DNA + [('m', ('f', ('x', 'y')), 'x + y'), ('dx', 'float', 1), ('dy', 'float', 1), ('pill_width', 'float', 1), ('pill_length', 'float', 5), ('color', 'rgba', '#ff0085')]
    
    def compact(self, system, height):
        P = []
        Fxy = self['m']
        to = system.to
        # fill in x
        for y in system[1].step(self['dy']):
            for x in system[0].step(self['dx']):
                try:
                    gx, gy = to(x, y)
                    P.append((gx, gy * height, Fxy(x, y)))
                except (ZeroDivisionError, ValueError):
                    pass
        self._compacted = P
    
    def inflate(self, width, * I ):
        pl = self['pill_length']
        inflated = []
        for x, y, m in ((x*width, y, m) for x, y, m in self._compacted):
            factor = pl/sqrt(1 + m**2)
            dx = factor
            dy = -m*factor # because screen coordinates are opposite the virtual space (“downward sloping” is positive)
            inflated.append(((x - dx, y - dy), (x + dx, y + dy)))
        self._inflated = inflated
        return (), ((0, self.paint),), ()
    
    def paint(self, cr):
        cr.set_source_rgba( * self['color'] )
        cr.set_line_width(self['pill_width'])
        for p1, p2 in self._inflated:
            cr.move_to( * p1 )
            cr.line_to( * p2 )
        cr.stroke()

members = Slope,
