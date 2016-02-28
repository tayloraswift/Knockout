from math import pi, ceil
from modules._graph import Cartesian

_namespace = 'mod:f'

def f_numeric(start, stop, step):
    for i in range(ceil(abs((stop - start)/step))):
        yield start + i * step

class Function(Cartesian):
    namespace = _namespace
    tags = {_namespace + ':' + T for T in ('x', 'y', 'dataset')}
    
    ADNA = {_namespace: [('height', 89, 'int'), ('tickwidth', 0.5, 'float'), ('round', 13, 'int')],
            'x': [('start', 0, 'float'), ('step', 1, 'float'), ('minor', 1, 'int'), ('major', 2, 'int'), ('every', 2, 'int'), ('stop', 89, 'float')],
            'y': [('start', 0, 'float'), ('step', 22.25, 'float'), ('minor', 1, 'int'), ('major', 2, 'int'), ('every', '2', 'int'), ('stop', 89, 'float')],
            'dataset': [('f', lambda x: x, 'fx'), ('color', '#ff3085', 'rgba')]}
    documentation = [(0, _namespace), (1, 'x'), (1, 'y'), (1, 'dataset')]
    
    def process_data(self, functions, x0, dx, xx, y0, dy, yy):
        P = []
        for F in functions:
            g = []
            for x in f_numeric(x0, x0 + xx, dx):
                try:
                    y = F(x)
                except ZeroDivisionError:
                    y = 0
                g.append((self.U(x - x0)/xx, self._graphheight*self.V(y - y0)/yy))
            P.append(g)
        self._points = P
        
    def ink_graph(self, cr):
        # ticks
        # x
        tw = self._tw
        cr.set_source_rgb(0, 0, 0)
        for i, x in enumerate(self._origins):
            if self._xnumbers[i][2]:
                cr.rectangle(x, 0, tw, 8)
            elif self._xnumbers[i][1]:
                cr.rectangle(x, 0, tw, 4)
        # y
        for y, m, M, s, k in self._ynumbers:
            if M:
                cr.rectangle(0, -int(round(y)), -8, -tw)
            elif m:
                cr.rectangle(0, -int(round(y)), -4, -tw)
        cr.fill()
        
        # points
        end = self._origins[-1]
        circle_t = 2*pi
        cr.set_line_width(2)
        for pointset, color, (k1, k2) in zip(self._t_points, self._datacolors, self._ky):
            cr.set_source_rgba( * color )
            cr.move_to( * pointset[0] )
            for x, y in pointset[1:]:
                cr.line_to(x, y)
            cr.stroke()
            # key
            cr.rectangle(end, k1 + 4, -4, k2 - k1 - 4)
            cr.fill()
    
    def transform_data(self, width):
        # TRANSFORM POINTS
        self._t_points = [[(x*width, -y) for x, y in pointset] for pointset in self._points]
