from math import pi, atan2
from itertools import chain, accumulate
from bisect import bisect

from meredith.paragraph import Blockelement
from olivia.frames import Subcell

from modules.plot.data import Data
from state.exceptions import LineOverflow

_namespace = 'mod:pie'

class PieSlice(Data):
    name = _namespace + ':slice'
    DNA = Data.DNA + [('prop', 'float', 1), ('color', 'rgba', '#ff3085')]

    def freeze(self, h, k):
        self._right = h
    
class PieChart(Blockelement):
    name = _namespace
    DNA = Blockelement.DNA + [('radius', 89, 'float'), ('center', 0.5, 'float'), ('rotate', 0, 'float')]
    
    def _load(self):
        self.active = 0
        
        self._pieslices = tuple(self.filter_nodes(PieSlice, inherit=False))
        total = sum(S['prop'] for S in self._pieslices)
                       #   percentage   |            arc length           | color
        self._slices = [(S['prop']/total, S['prop']/total*2*pi, S['color']) for S in self._pieslices]
        self._slices_t = list(accumulate(s[1] for s in self._slices))
        
        self._keys = list(chain.from_iterable(PL.key() for PL in self._pieslices))
        self._FLOW = [K[0] for K in self._keys]

    def print_pie(self, cr):
        r = self['radius']
        t = self['rotate']
        for percent, arc, color in self._slices:
            cr.move_to(0, 0)
            cr.arc(0, 0, r, t, t + arc)
            cr.close_path()
            cr.set_source_rgba( * color )
            cr.fill()
            t += arc
            
        self._KEY.draw(cr)
        
    def pie_annot(self, cr):
        t = self._slices_t[self.active - 1] + self['rotate']
        percent, arc, color = self._slices[self.active]
        cr.set_source_rgba( * color )
        cr.set_line_width(2)
        cr.arc( * self._center, self['radius'] + 13, t, t + arc)
        cr.stroke()
        cr.fill()

    def regions(self, x, y):
        if x**2 + y**2 <= (self['radius'] + 13)**2:
            t = atan2(y, x) - self['rotate']
            if t < 0:
                t += 2*pi
            self.active = bisect(self._slices_t, t)
        else:
            self.active = self._KEY.target(y)
        return self.active

    def typeset(self, bounds, c, y, y2, overlay):
        P_slice, P_right = self.styles(overlay, 'slice', '_right')
        r = self['radius']
        top = y
        left, right = bounds.bounds(y + r)
        px = left + (right - left)*self['center']
        py = y + r
        if py + r > y2:
            raise LineOverflow
        
        for PL in self._pieslices:
            PL.freeze(right - px, 0)
        # key
        self._KEY = Plot_key(self._keys, Subcell(bounds, 0.5, 1), c, top, py, P_slice + P_right)
        
        bottom = max(py + r, self._FLOW[-1].y)
        
        self._center = px, py
        
        return GraphBlock(self._FLOW, [],
                    (top, bottom, left, right), 
                    self.print_pie, self.pie_annot, 
                    self._center, self.regions, self.PP)

members = [PieChart, PieSlice]
