from math import pi, atan2
from itertools import chain, accumulate
from bisect import bisect

from model.olivia import Flowing_text
from model.george import Subcell
from elements.elements import Block_element

from modules.plot import Plot_key, GraphBlock
from modules.plot.data import Data

_namespace = 'mod:pie'

class PieSlice(Data):
    nodename = _namespace + ':slice'
    ADNA = [('prop', 1, 'float'), ('color', '#ff3085', 'rgba')]

    def freeze(self, h, k):
        self._right = h
    
class PieChart(Block_element):
    nodename = _namespace
    DNA = {'slice': {}}
    ADNA = [('radius', 89, 'float'), ('center', 0.5, 'float')]
    documentation = [(0, nodename), (1, 'slice')]
    
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
        t = 0
        for percent, arc, color in self._slices:
            cr.move_to(0, 0)
            cr.arc(0, 0, r, t, t + arc)
            cr.close_path()
            cr.set_source_rgba( * color )
            cr.fill()
            t += arc
            
        self._KEY.draw(cr)
        
    def pie_annot(self, cr):
        t = self._slices_t[self.active - 1]
        percent, arc, color = self._slices[self.active]
        cr.set_source_rgba( * color )
        cr.set_line_width(2)
        cr.arc( * self._center, self['radius'] + 13, t, t + arc)
        cr.stroke()
        cr.fill()

    def regions(self, x, y):
        if x**2 + y**2 <= (self['radius'] + 13)**2:
            t = atan2(y, x)
            if t < 0:
                t += 2*pi
            self.active = bisect(self._slices_t, t)
        else:
            self.active = self._KEY.target(y) - 2
        return self.active

    def typeset(self, bounds, c, y, overlay):
        P_slice, = self.styles(overlay, 'slice')
        r = self['radius']
        top = y
        left, right = bounds.bounds(y + r)
        px = left + (right - left)*self['center']
        py = y + r
        
        for PL in self._pieslices:
            PL.freeze(right - px, 0)
        # key
        self._KEY = Plot_key(self._keys, Subcell(bounds, 0.5, 1), c, top, py, P_slice)
        
        bottom = max(py + r, self._FLOW[-1].y)
        
        self._center = px, py
        
        return GraphBlock(self._FLOW, [],
                    (top, bottom, left, right), 
                    self.print_pie, self.pie_annot, 
                    self._center, self.regions, self.PP)

members = [PieChart, PieSlice]
inline = False
