from math import pi, atan2
from itertools import chain, accumulate
from bisect import bisect

from model.olivia import Atomic_text, Block
from IO.xml import print_attrs, print_styles
from elements.elements import Block_element

_namespace = 'mod:pie'

class _Pie(object):
    def __init__(self, slices, radius, active=0):
        self.slices = slices
        self.active = active
        self.r = radius
        self.center = (0, 0)

class PieChart(Block_element):
    namespace = _namespace
    tags = {_namespace + ':' + T for T in ('slice',)}
    DNA = {'slice': {}}
    
    ADNA = {_namespace: [('radius', 89, 'float')],
            'slice': [('prop', 1, 'float'), ('color', '#ff3085', 'rgba')]}
    documentation = [(0, _namespace), (1, 'slice')]
    
    def _load(self, L):
        self._tree = L
        self.PP = L[0][2]
        radius, = self._get_attributes(_namespace)
        slices, labels = zip( * (( tuple(self._get_attributes('slice', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':slice'))
        total = sum(P for P, C in slices)
                       # percentage | arc length | color
        self._pie = _Pie([(P/total, P/total*2*pi, C) for P, C in slices], radius)
        self._FLOW = [Atomic_text(text) for text in labels]
        
    def represent(self, indent):
        name, attrs = self._tree[0][:2]
        attrs.update(print_styles(self.PP))
        lines = [[indent, '<' + print_attrs(name, attrs) + '>']]
        for tag, E in self._tree[1]:
            lines.append([indent + 1, '<' + print_attrs( * tag ) + '>'])
            lines.extend(self._SER(E, indent + 2))
            lines.append([indent + 1, '</' + tag[0] + '>'])
        lines.append([indent, '</' + self.namespace + '>'])
        return lines

    def typeset(self, bounds, c, y, overlay):
        P_slice, = self._modstyles(overlay, 'slice')
        r = self._pie.r
        top = y
        y += 22
        left, right = bounds.bounds(y + r)
        px = (right + left)/2
        py = y + r
        for S in self._FLOW:
            S.cast(bounds, c, y, P_slice)
            y += 20
        bottom = py + r + 22
        
        self._pie.center = px, py
        return _MBlock(self._FLOW, (top, bottom, left, right), self._pie, self.PP)

class _MBlock(Block):
    def __init__(self, FLOW, box, pie, PP):
        Block.__init__(self, FLOW, * box, PP)
        self._slices = pie.slices
        self._slices_t = list(accumulate(s[1] for s in self._slices))
        self._pie = pie
    
    def _print_pie(self, cr):
        r = self._pie.r
        t = 0
        for i, S in enumerate(self._slices):
            percent, arc, color = S
            cr.move_to(0, 0)
            cr.arc(0, 0, r, t, t + arc)
            cr.close_path()
            cr.set_source_rgba( * color)
            cr.fill()
            t += arc

    def _print_annot(self, cr, O):
        if O is self._FLOW[self._pie.active]:
            r = self._pie.r
            i = self._pie.active
            t = self._slices_t[i - 1]
            percent, arc, color = self._slices[i]
            cr.set_source_rgba( * color)
            cr.set_line_width(2)
            cr.arc(0, 0, r + 13, t, t + arc)
            cr.stroke()
            self._handle(cr)
            cr.fill()

    def _target_slice(self, x, y):
        px, py = self._pie.center
        r = self._pie.r
        dx = x - px
        dy = y - py
        if dx**2 + dy**2 > (r + 13)**2:
            return self._pie.active
        else:
            t = atan2(dy, dx)
            if t < 0:
                t += 2*pi
            return bisect(self._slices_t, t)
    
    def I(self, x, y):
        if x <= self['right']:
            s = self._target_slice(x, y)
            self._pie.active = s
            return self._FLOW[s]
        else:
            return self['i']
    
    def deposit(self, repository):
        repository['_paint'].append((self._print_pie, * self._pie.center)) # come before to avoid occluding child elements
        repository['_paint_annot'].append((self._print_annot, * self._pie.center))
        for A in self._FLOW:
            A.deposit(repository)
