from math import pi
from .data import Data

class Function(Data):
    name = 'mod:fx'
    ADNA = [('x', lambda t: t, 'fx'), ('y', lambda t: t, 'fx'), ('start', -1, 'float'), ('stop', -1, 'float'), ('step', 1, 'float'), ('color', '#ff3085', 'rgba'), ('radius', 2, 'float'), ('linewidth', 2, 'float'), ('clip', False, 'bool'), ('key', True, 'bool')]

    def unit(self, axes):
        fit = axes.fit
        
        P = [[]]
        Fx = self['x']
        Fy = self['y']
        for t in axes[0].step(self['step'], ** {k: self[k] for k in ('start', 'stop') if k in self.attrs} ):
            try:
                x = Fx(t)
                y = Fy(t)
                P[-1].append(fit(x, y))
                continue
            except (ZeroDivisionError, ValueError):
                pass
            if P[-1]:
                P.append([])
        self._unitpoints = P
        return self
    
    def draw(self, cr):
        cr.set_source_rgba( * self['color'] )
        circle_t = 2*pi
        cr.set_line_width(self['linewidth'])
        r = self['radius']
        
        cr.save()
        if self['clip']:
            cr.rectangle(0, 0, * self._box )
            cr.clip()
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
        cr.restore()
    
    def freeze(self, axes):
        self._right = axes.h
        project = axes.project
        self._points = [[project( * coords ) for coords in segment] for segment in self._unitpoints]
        self._box = (axes.h, axes.k)

members = [Function]
