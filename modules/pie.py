from math import pi, atan2
from itertools import accumulate
from bisect import bisect

from meredith.paragraph import Blockelement

from modules.mathplot.data import Data
from modules.mathplot import Plot_keys

_namespace = 'mod:pie'

class PieSlice(Data):
    name = _namespace + ':slice'
    DNA = Data.DNA + [('prop', 'float', 1), ('color', 'rgba', '#ff3085')]
    
class PieChart(Blockelement):
    name = _namespace
    DNA = Blockelement.DNA + [('radius', 'float', 89), ('center', 'float', 0.5), ('rotate', 'float', 0), ('key_shift', 'float', 4), ('key_bottom', 'float', 4), ('cl_key', 'blocktc', 'key')]
    
    def _load(self):
        self._pieslices = tuple(self.filter_nodes(PieSlice))
        total = sum(S['prop'] for S in self._pieslices)
                       #   percentage   |            arc length           | color
        self._slices = [(S['prop']/total, S['prop']/total*2*pi, S['color']) for S in self._pieslices]
        self._slices_t = list(accumulate(s[1] for s in self._slices))
        
        self._keys = Plot_keys(self._pieslices)
        self._planes = set(self._pieslices)
    
    def _paint_pie(self, cr):
        r = self['radius']
        t = self['rotate']
        for percent, arc, color in self._slices:
            cr.move_to(0, 0)
            cr.arc(0, 0, r, t, t + arc)
            cr.close_path()
            cr.set_source_rgba( * color )
            cr.fill()
            t += arc
        
    def _paint_pie_annot(self, cr, O):
        if O in self._planes:
            i = self._pieslices.index(O)
            t = self._slices_t[i - 1] + self['rotate']
            percent, arc, color = self._slices[i]
            cr.set_source_rgba( * color )
            cr.set_line_width(2)
            cr.arc(0, 0, self['radius'] + 13, t, t + arc)
            cr.stroke()
            cr.fill()

    def which(self, x, u, r):
        if (r > 1 or r < 0) and x <= self._extreme:
            dx = x - self._px
            du = u - self._pu
            
            if dx**2 + du**2 <= (self['radius'] + 13)**2:
                t = atan2(du, dx) - self['rotate']
                if t < 0:
                    t += 2*pi
                i = bisect(self._slices_t, t)
                cell = self._pieslices[i]
            else:
                i, cell = self._keys.which(u)
            return ((i, cell),) + cell.which(x, u, r - 1)
        else:
            return ()

    def _layout_block(self, frames, BSTYLE, overlay):
        self._frames = frames
        
        r = self['radius']
        u, x1, x2, y, c, pn = frames.fit(2*r)
        self._px = x1 + (x2 - x1)*self['center']
        self._pu = u - r
        center = self._px, y - r
        
        self._extreme = x2
        
        planes = []
        paint_functions = [(pn, (self._paint_pie,) + center)]
        # key
        u = self._keys.layout_keys(frames, overlay + self['cl_key'], planes, paint_functions, u - 2*r, u, self['key_shift'], self['key_bottom'])
        
        return u, [], [], planes, paint_functions, [(pn, (self._paint_pie_annot,) + center)], lambda O: O in self._planes, self._keys.get_color()

members = [PieChart, PieSlice]
