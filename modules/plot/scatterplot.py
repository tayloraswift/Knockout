from math import pi
from .data import Data

class Scatterplot(Data):
    name = 'mod:scatter'
    ADNA = [('data', (), 'multi_D'), ('color', '#ff3085', 'rgba'), ('radius', 2, 'float'), ('key', True, 'bool')]

    def unit(self, axes):
        fit = axes.fit
        self._unitpoints = [fit( * coord ) for coord in self['data']]
        return self
    
    def draw(self, cr):
        cr.set_source_rgba( * self['color'] )
        circle_t = 2*pi
        r = self['radius']
        for x, y in self._points:
            cr.move_to(x, y)
            cr.arc(x, y, r, 0, circle_t)
            cr.close_path()
        cr.fill()
    
    def freeze(self, axes):
        self._right = axes.h
        project = axes.project
        self._points = [project( * coords ) for coords in self._unitpoints]

members = [Scatterplot]
