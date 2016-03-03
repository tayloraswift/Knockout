from math import pi, ceil
from modules._graph import Cartesian, cart_ADNA

_namespace = 'mod:f'

def f_numeric(start, stop, step):
    for i in range(ceil(abs((stop - start)/step))):
        yield start + i * step

class Function(Cartesian):
    namespace = _namespace
    tags = {_namespace + ':' + T for T in ('x', 'y', 'dataset')}
    
    ADNA = {_namespace: cart_ADNA['GRAPH'],
            'x': cart_ADNA['x'],
            'y': cart_ADNA['y'],
            'dataset': [('f', lambda x: x, 'fx'), ('color', '#ff3085', 'rgba')]}
    documentation = [(0, _namespace), (1, 'x'), (1, 'y'), (1, 'dataset')]
    
    def process_data(self, functions, x0, dx, xx, y0, dy, yy):
        P = []
        for F in functions:
            g = [[]]
            for x in f_numeric(x0, x0 + xx, dx):
                try:
                    y = F(x)
                    g[-1].append(((self.U(x) - x0)/xx, self._graphheight*(self.V(y) - y0)/yy))
                    continue
                except (ZeroDivisionError, ValueError):
                    pass
                if g[-1]:
                    g.append([])
                
            P.append(g)
        return P
    
    def _draw_data(self, cr, data):
        circle_t = 2*pi
        cr.set_line_width(2)
        if data and not data[-1]:
            data = data[:-1]
        for segment in data:
            cr.move_to( * segment[0] )
            curve = segment[1:]
            if curve:
                for x, y in curve:
                    cr.line_to(x, y)
                cr.stroke()
            else:
                cr.arc( * segment[0], 2, 0, circle_t)
                cr.close_path()
                cr.fill()
    
    def transform_data(self, width):
        # TRANSFORM POINTS
        return list(zip([[[(x*width, -y) for x, y in segment] for segment in pointset] for pointset in self._data_unscaled], self._datacolors, self._ky))
