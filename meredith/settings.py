import cairo

from math import sqrt

from itertools import chain

from olivia.basictypes import interpret_int

from meredith.box import Null, Box

class FontRendering(Box):
    DNA = [('hinting', 'int', 0), ('antialias', 'int', 0)]
    
    def after(self, A):
        self.fontoptions.set_hint_style(self['hinting'])
        self.fontoptions.set_antialias(self['antialias'])

FO = cairo.FontOptions()

fontsettings = FontRendering({'hinting': FO.get_hint_style(), 'antialias': FO.get_antialias()})
fontsettings.fontoptions = FO

class View(Null):
    name = 'view'
    
    def __init__(self, attrs, content=None):
        self.mode = attrs['mode']
        
        self.H    = interpret_int(attrs['h'])
        self.K    = interpret_int(attrs['k'])
        
        self.Hc   = interpret_int(attrs['hc'])
        self.Kc   = interpret_int(attrs['kc'])
                
        self._displacement = 0, 0
        
        self._zoom_levels = 0.1, 0.13, 0.15, 0.2, 0.22, 0.3, 0.4, 0.5, 0.6, 0.8, 0.89, 1, 1.25, 1.5, 1.75, 1.989, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30
        
        self.zoom_level   = interpret_int(attrs['zoom'])
        self.A    = self._zoom_levels[self.zoom_level]
    
    def reset_functions(self, map_X, map_Y):
        self._map_X = map_X
        self._map_Y = map_Y

    def print_A(self):
        return ' '.join(chain((self.name,), (''.join((a, '="', str(v), '"')) for a, v in (('h'   , self.H ), 
                                                                                          ('k'   , self.K ),
                                                                                          ('hc'  , self.Hc),
                                                                                          ('kc'  , self.Kc),
                                                                                          ('zoom', self.zoom_level),
                                                                                          ('mode', self.mode)
                                                                                          ))))
    # TRANSFORMATION FUNCTIONS
    def X_to_screen(self, x, pp):
        return int(self.A * (self._map_X(x, pp) + self.H - self.Hc) + self.Hc)

    def Y_to_screen(self, y, pp):
        return int(self.A * (self._map_Y(y, pp) + self.K - self.Kc) + self.Kc)
    
    def T_1(self, x, y):
        return (x - self.Hc) / self.A - self.H + self.Hc , (y - self.Kc) / self.A - self.K + self.Kc
    
    def transform_canvas(self, cr, page):
        A = self.A
        # Transform goes
        # x' = A (x + m - c) + c
        # x' = Ax + (Am - Ac + c)
        
        # Scale first (on bottom) is significantly faster in cairo
        cr.translate(A*self._map_X(self.H - self.Hc, page) + self.Hc, A*self._map_Y(self.K - self.Kc, page) + self.Kc)
        cr.scale(A, A)
    
    # UI INTERACTION
    def move_vertical(self, amount):
        self.K += int(amount / sqrt(self.A))

    def pan(self, dx, dy, h0, k0):
        self.H = int(round( (dx)/self.A + h0))
        self.K = int(round( (dy)/self.A + k0))
        
        # heaven knows why this expression works, but hey it works
        displacement = (self.H - h0) * self.A, (self.K - k0) * self.A
        
        if displacement != self._displacement:
            self._displacement = displacement
            return True
        else:
            return False
    
    def zoom(self, x, y, direction):
        if direction:
            if self.zoom_level > 0:
                self.zoom_level -= 1
        elif self.zoom_level < len(self._zoom_levels) - 1:
            self.zoom_level += 1
        
        dhc = x - self.Hc
        self.Hc += dhc
        self.H  -= int(dhc * (1 - self.A) / self.A)
        
        dkc = y - self.Kc
        self.Kc += dkc
        self.K  -= int(dkc * (1 - self.A) / self.A)
        
        self.A   = self._zoom_levels[self.zoom_level]

    def set_mode(self, mode):
        self.mode = mode

members = View,
