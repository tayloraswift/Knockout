from math import pi, atan2
from itertools import chain, accumulate
from bisect import bisect

from model.olivia import Flowing_text
from model.george import Subcell
from elements.elements import Block_element

from modules._graph import generate_key, GraphBlock

_namespace = 'mod:pie'

class PieChart(Block_element):
    namespace = _namespace
    tags = {_namespace + ':' + T for T in ('slice',)}
    DNA = {'slice': {}}
    
    ADNA = {_namespace: [('radius', 89, 'float'), ('center', 0.5, 'float')],
            'slice': [('prop', 1, 'float'), ('color', '#ff3085', 'rgba')]}
    documentation = [(0, namespace), (1, 'slice')]
    
    def _load(self, L):
        self._tree = L
        self.PP = L[0][2]
        self._radius, self._center_x = self._get_attributes(self.namespace)
        self.active = 0
        
        slices, labels = zip( * (( tuple(self._get_attributes('slice', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':slice'))
        total = sum(P for P, C in slices)
                       # percentage | arc length | color
        self._slices = [(P/total, P/total*2*pi, C) for P, C in slices]
        self._slices_t = list(accumulate(s[1] for s in self._slices))
        
        self._FLOW = [Flowing_text(text) for text in labels]

    def print_pie(self, cr):
        r = self._radius
        t = 0
        end = self._to_right
        for S, (k1, k2) in zip(self._slices, self._ky):
            percent, arc, color = S
            cr.move_to(0, 0)
            cr.arc(0, 0, r, t, t + arc)
            cr.close_path()
            cr.set_source_rgba( * color)
            cr.fill()
            t += arc
            
            # key
            cr.rectangle(end, k1 + 4, -4, k2 - k1 - 4)
            cr.fill()
        
    def pie_annot(self, cr):
        t = self._slices_t[self.active - 1]
        percent, arc, color = self._slices[self.active]
        cr.set_source_rgba( * color)
        cr.set_line_width(2)
        cr.arc( * self._center, self._radius + 13, t, t + arc)
        cr.stroke()
        cr.fill()

    def regions(self, x, y):
        if x**2 + y**2 <= (self._radius + 13)**2:
            t = atan2(y, x)
            if t < 0:
                t += 2*pi
            self.active = bisect(self._slices_t, t)
        else:
            self.active = min(len(self._slices) - 1, max(0, bisect(self._ki, y) - 1))
        return self.active

    def typeset(self, bounds, c, y, overlay):
        P_slice, = self._modstyles(overlay, 'slice')
        r = self._radius
        top = y
        left, right = bounds.bounds(y + r)
        px = left + (right - left)*self._center_x
        py = y + r
        
        # key
        self._ki, self._ky = generate_key(self._FLOW, Subcell(bounds, 0.5, 1), c, top, py, P_slice)
        
        bottom = max(py + r, self._FLOW[-1].y)
        
        self._center = px, py
        self._to_right = right - px
        
        return GraphBlock(self._FLOW, [],
                    (top, bottom, left, right), 
                    self.print_pie, self.pie_annot, 
                    self._center, self.regions, self.PP)
