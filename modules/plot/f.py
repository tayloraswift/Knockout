from math import pi
from .data import Data

class Function(Data):
    nodename = 'mod:fx'
    ADNA = [('f', lambda x: x, 'fx'), ('step', 1, 'float'), ('color', '#ff3085', 'rgba'), ('radius', 2, 'float'), ('linewidth', 2, 'float')]

    def unit(self, axes):
        F, dx, self.color, self._r, self._lw = self.get_attributes()
        project = axes.project
        
        P = [[]]
        for x in axes.X.step(dx):
            try:
                y = F(x)
                P[-1].append(project(x, y))
                continue
            except (ZeroDivisionError, ValueError):
                pass
            if P[-1]:
                P.append([])
        self._unitpoints = P
        return self
    
    def draw(self, cr):
        cr.set_source_rgba( * self.color )
        circle_t = 2*pi
        cr.set_line_width(self._lw)
        r = self._r
        
        for segment in (p for p in self._points if p):
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
    
    def freeze(self, h, k):
        self._right = h
        self._points = [[(x*h, y*k) for x, y in segment] for segment in self._unitpoints]

members = [Function]
