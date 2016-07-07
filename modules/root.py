from layout.otline import cast_mono_line
from meredith.box import Box, Inline

_namespace = 'mod:root'

class Index(Box):
    name = _namespace + ':i'
    textfacing = True

class Radicand(Box):
    name = _namespace + ':rad'
    textfacing = True

class Root(Inline):
    name = _namespace
    
    DNA = [('cl_radicand', 'texttc', 'small')]
    
    def _load(self):
        self._index, self._radicand = self.find_nodes(Index, Radicand)
    
    def _draw_radix(self, cr):
        cr.set_source_rgba( * self._color )
        cr.move_to(self._radix[0][0], self._radix[0][1])
        for u, v in self._radix[1:]:
            cr.line_to(u, v)
        cr.close_path()
        cr.fill()
    
    def _cast_inline(self, LINE, runinfo, F, FSTYLE):
        self._color = FSTYLE['color']
        y = FSTYLE['shift']
        
        rad = cast_mono_line(LINE, self._radicand.content, runinfo, F)
        rad_asc = rad['ascent']
        rad_desc = rad['descent']
        
        rfs = FSTYLE['fontsize']
        iy = y - rfs * 0.44 - FSTYLE['shift']
        ix = rfs*0.05
        jx = ix - rad_desc * 0.4
        kx = jx + (rad_asc - rad_desc)*0.3

        self._radix = [(ix - rfs*0.050, iy),
                (ix + rfs*0.105, iy - rfs*0.02), #crest
                (ix + rfs*0.14, iy + rfs*0.08),
                (jx + rfs*0.135, y - rad_desc - rfs*0.35), # inner vertex
                (kx + rfs*0.05, y - rad_asc - rfs*0.04),
                
                (kx + rad['advance'] + rfs*0.35, y - rad_asc - rfs*0.04), # overbar
                (kx + rad['advance'] + rfs*0.345, y - rad_asc),
                
                (kx + rfs*0.09, y - rad_asc),
                (jx + rfs*0.15, y - rad_desc - rfs*0.24), # outer vertex
                (jx + rfs*0.08, y - rad_desc - rfs*0.24), # outer vertex
                (ix + rfs*0.06, iy + rfs*0.15),
                (ix + rfs*0.010, iy + rfs*0.04), # lip
                (ix - rfs*0.050, iy + rfs*0.03),
                ]

        rad['x'] = kx + rfs * 0.2
        rad['y'] = y
              
        if self._index is None:
            NL = [rad]
        else:
            index = cast_mono_line(LINE, self._index.content, runinfo, F + self['cl_radicand'])
            index['x'] = jx - index['advance']*0.5
            index['y'] = y - rfs * 0.6
            NL = [index, rad]
        
        width = kx + rfs * 0.35 + rad['advance']
        
        return NL, width, rad_asc + rfs*0.2, rad_desc, (self._draw_radix, 0, 0, 0)

members = (Root, Index, Radicand)
