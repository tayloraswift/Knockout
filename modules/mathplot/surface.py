from itertools import chain
from .data import Data

from IO.vectorcache import Vector_cache

def yield_for_haylor(Fx, Fy, Fz, to, height, u, iter_v):
    for v in iter_v:
        try:
            x = Fx(u, v)
            y = Fy(u, v)
            z = Fz(u, v)
            hx, hy = to(x, y, z)
            yield (x, y, z), (hx, hy*height)
            
        except (ZeroDivisionError, ValueError):
            yield (0, 0, 0), (0, 0)

def tile(A):
    h = len(A)
    if h:
        kk = list(range(len(A[0]) - 1))
    return chain.from_iterable(((A[i][j], A[i + 1][j], A[i + 1][j + 1], A[i][j + 1]) for j in kk) for i in range(h - 1))

def mesh(I, iter_u, iter_v):
    iter_v = list(iter_v)
    return [list(yield_for_haylor( * I , u, iter_v)) for u in iter_u]

def _apply_height(screen, height):
    return screen[0], screen[1]*height

class Parametric_Surface(Data):
    name = 'mod:surface'
    DNA = Data.DNA + [('x', ('f', ('u', 'v')), lambda u, v: u), ('y', ('f', ('u', 'v')), lambda u, v: v), ('z', ('f', ('u', 'v')), lambda u, v: 0), 
                      ('range_u', 'open range', ':'), ('range_v', 'open range', ':'), 
                      ('step_u', 'float', 1), ('step_v', 'float', 0), 
                      ('color', 'gradient', '0: #ff3085 | 1: #ff00aa')]

    def compact(self, system, height):
        to = system.to
        ah = _apply_height
        
        if not self['step_v']:
            step_v = self['step_u']
        else:
            step_v = self['step_v']
        iter_u = system[0].step(self['step_u'], * self['range_u'] )
        iter_v = system[1].step(step_v        , * self['range_v'] )
        
        MESH = mesh((self['x'], self['y'], self['z'], to, height), iter_u, iter_v)
        
        polygons  = []
        
        gradient  = self['color'].calc_color
        z0        = system[-1]['range'][0]
        inv_zrange= 1/(system[-1]['range'][1] - z0)
        get_color = lambda x, y, z: gradient((z - z0)*inv_zrange)
        get_Z     = system.Z
        for vertices in tile(MESH):
            numeric, screen = zip( * vertices )
            mx, my, mz = tuple(sum(dim)*0.25 for dim in zip( * numeric ))
            polygons.append((get_Z(mx, my, mz), get_color(mx, my, mz), screen))
        
        self._compact  = sorted(polygons)
        self._z_center = system.z_center
        self._k = -height

    def inflate(self, width, * I ):
        self._inflated = [(color, [(x*width, y) for x, y in polygon]) for Z, color, polygon in self._compact]
        return (), ((self._z_center, Vector_cache(self._paint_full, width, self._k).paint),), ()
    
    def _paint_full(self, cr):
        for color, polygon in self._inflated:
            polygon = iter(polygon)
            cr.set_source_rgba( * color )
            cr.move_to( * next(polygon) )
            for p in polygon:
                cr.line_to( * p )
            cr.fill()
members = [Parametric_Surface]
