from model.cat import cast_mono_line, calculate_vmetrics
from elements.elements import Inline_element
from model.olivia import Inline
from edit.paperairplanes import interpret_int

_namespace = 'mod:root'

class Root(Inline_element):
    namespace = _namespace
    tags = {_namespace + ':' + T for T in ('index', 'radicand')}
    DNA = {'index': {},
            'radicand': {}}
    
    def _load(self, L):
        self._tree = L
        index = next(E for tag, E in L[1] if tag[0] == self.namespace + ':index')
        radicand = next(E for tag, E in L[1] if tag[0] == self.namespace + ':radicand')
        
        self._INLINE = [index, radicand]
    
    def _draw_radix(self, cr, x, y):
        cr.set_source_rgba( * self._color )
        cr.move_to(self._radix[0][0] + x, self._radix[0][1] + y)
        for u, v in self._radix[1:]:
            cr.line_to(x + u, y + v)
        cr.close_path()
        cr.fill()
    
    def cast_inline(self, x, y, leading, PP, F, FSTYLE):
        self._color = FSTYLE['color']
        F_index, F_rad = self._modstyles(F, 'index', 'radicand')

        index = cast_mono_line(self._INLINE[0], 13, PP, F_index)
        rad = cast_mono_line(self._INLINE[1], 13, PP, F_rad)
        
        

        
        rad_asc, rad_desc = calculate_vmetrics(rad)

        k = x + index['advance']
        
        rfs = FSTYLE['fontsize']
        iy = y - rfs * 0.44
        ix = k - rfs * 0.30
        jx = ix - rad_desc * 0.4
        kx = jx + (rad_asc - rad_desc)*0.3
        
        index['x'] = x
        index['y'] = y - rfs * 0.6
        
        rad['x'] = k + rfs * 0.35
        rad['y'] = y

        self._radix = [(ix - rfs*0.050, iy),
                (ix + rfs*0.105, iy - rfs*0.02), #crest
                (ix + rfs*0.14, iy + rfs*0.08),
                (jx + rfs*0.135, y - rad_desc - rfs*0.35), # inner vertex
                (kx + rfs*0.05, y - rad_asc - rfs*0.04),
                
                (kx + rad['advance'] + rfs*0.45, y - rad_asc - rfs*0.04), # overbar
                (kx + rad['advance'] + rfs*0.445, y - rad_asc),
                
                (kx + rfs*0.09, y - rad_asc),
                (jx + rfs*0.15, y - rad_desc - rfs*0.24), # outer vertex
                (jx + rfs*0.08, y - rad_desc - rfs*0.24), # outer vertex
                (ix + rfs*0.06, iy + rfs*0.15),
                (ix + rfs*0.010, iy + rfs*0.04), # lip
                (ix - rfs*0.050, iy + rfs*0.03),
                ]
        
        index['x'] = x
        index['y'] = y - rfs * 0.6
        
        rad['x'] = kx + rfs * 0.30
        rad['y'] = y
        
        width = kx - x + rfs * 0.45 + rad['advance']
        
        return _MInline([index, rad], width, rad_asc, rad_desc, self._draw_radix)
        
    def __len__(self):
        return 8

class _MInline(Inline):
    def __init__(self, lines, width, A, D, draw):
        Inline.__init__(self, lines, width, A, D)
        self._draw = draw

    def deposit_glyphs(self, repository, x, y):
        for line in self._LINES:
            line.deposit(repository, x, y)
        repository['_paint'].append(lambda cr: self._draw(cr, x, y))
