from math import pi
from .data import Data

class Function(Data):
    name = 'mod:fx'
    DNA = Data.DNA + [('x', ('f', ('t|x',)), lambda t: t), ('y', ('f', ('t|x',)), lambda t: t), ('z', ('f', ('t|x',)), lambda t: t), ('range', 'open range', ':'), ('step', 'float', 1), ('color', 'rgba', '#ff3085'), ('radius', 'float', 2), ('line_width', 'float', 2), ('clip', 'bool', False)]

    def compact(self, system, height):
        to = system.to
        
        P = [[]]
        Fx = self['x']
        Fy = self['y']
        Fz = self['z']
        
        for t in system[0].step(self['step'], * self['range'] ):
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
        self._z_center = system.z_center
        self._clip_k = height

    def inflate(self, width, * I ):
        self._inflated = [[(x*width, y) for x, y in segment] for segment in self._compact]
        self._clip_h = width
        return (), ((self._z_center, self.paint),), ()
    
    def paint(self, cr, render):
        cr.set_source_rgba( * self['color'] )
        circle_t = 2*pi
        cr.set_line_width(self['line_width'])
        r = self['radius']
        
        cr.save()
        if self['clip']:
            cr.rectangle(0, 0, self._clip_h, self._clip_k)
            cr.clip()
        for n, segment in ((len(p), iter(p)) for p in self._inflated if p):
            if n > 1:
                cr.move_to( * next(segment) )
                for x, y in segment:
                    cr.line_to(x, y)
                cr.stroke()
            else:
                cr.arc( * next(segment), r, 0, circle_t)
                cr.close_path()
                cr.fill()
        cr.restore()

members = [Function]
