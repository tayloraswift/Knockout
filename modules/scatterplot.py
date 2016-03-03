from math import pi
from modules._graph import Cartesian, cart_ADNA

_namespace = 'mod:scatter'

class Scatterplot(Cartesian):
    namespace = _namespace
    tags = {_namespace + ':' + T for T in ('x', 'y', 'dataset')}
    
    ADNA = {_namespace: cart_ADNA['GRAPH'],
            'x': cart_ADNA['x'],
            'y': cart_ADNA['y'],
            'dataset': [('data', (), '2D'), ('color', '#ff3085', 'rgba')]}
    documentation = [(0, _namespace), (1, 'x'), (1, 'y'), (1, 'dataset')]
    
    def process_data(self, datavalues, x0, dx, xx, y0, dy, yy):
        return [[((self.U(x) - x0)/xx, self._graphheight*(self.V(y) - y0)/yy) for x, y in VV] for VV in datavalues]
    
    def _draw_data(self, cr, data):
        circle_t = 2*pi
        for x, y in data:
            cr.move_to(x, y)
            cr.arc(x, y, 2, 0, circle_t)
            cr.close_path()
    
    def transform_data(self, width):
        # TRANSFORM POINTS
        return list(zip([[(x*width, -y) for x, y in pointset] for pointset in self._data_unscaled], self._datacolors, self._ky))
