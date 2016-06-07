from math import pi
from .data import Data

class Function(Data):
    name = 'mod:fx'
    DNA = Data.DNA + [('x', 'fx', lambda t: t), ('y', 'fx', lambda t: t), ('z', 'fx', lambda t: t), ('range', 'open range', ':'), ('step', 'float', 1), ('color', 'rgba', '#ff3085'), ('radius', 'float', 2), ('line_width', 'float', 2), ('clip', 'bool', False)]

    def compact(self, system, height):
        to = system.to
        
        P = [[]]
        Fx = self['x']
        Fy = self['y']
        Fz = self['z']
        
        domain = {}
        start, stop = self['range']
        if start is not None:
            domain['start'] = start
        if stop is not None:
            domain['stop'] = stop
        
        for t in system[0].step(self['step'], ** domain ):
            try:
                x = Fx(t)
                y = Fy(t)
                z = Fz(t)
                hx, hy = to(x, y, z)
                P[-1].append((hx, hy*height))
                continue
            except (ZeroDivisionError, ValueError):
                pass
            if P[-1]:
                P.append([])
        self._compact = P
        
        self._clip_k = height

    def inflate(self, width, * I ):
        self._inflated = [[(x*width, y) for x, y in segment] for segment in self._compact]
        self._clip_h = width
        return (), (self.paint,), ()
    
    def paint(self, cr):
        cr.set_source_rgba( * self['color'] )
        circle_t = 2*pi
        cr.set_line_width(self['line_width'])
        r = self['radius']
        
        cr.save()
        if self['clip']:
            cr.rectangle(0, 0, self._clip_h, self._clip_k)
            cr.clip()
        for segment in (p for p in self._inflated if p):
            cr.move_to( * segment[0] )
            curve = segment[1:]
            if curve:
                for x, y in curve:
                    cr.line_to(x, y)
                cr.stroke()
            else:
                cr.arc( * segment[0], r, 0, circle_t)
                cr.close_path()
                cr.fill()
        cr.restore()

members = [Function]
