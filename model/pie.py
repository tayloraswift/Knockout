from math import pi, atan2
from itertools import chain, accumulate
from bisect import bisect

from model.olivia import Atomic_text, Block
from edit.paperairplanes import interpret_rgba

def _print_attrs(name, attrs):
    if attrs:
        return '<' + name + ' ' + ' '.join(A + '="' + repr(V)[1:-1] + '"' for A, V in attrs.items()) + '>'  
    else:
        return '<' + name + '>'

class PieChart(object):
    def __init__(self, L):
        if 'radius' in L[0][1]:
            self._radius = int(L[0][1]['radius'])
        else:
            self._radius = 89
        self._chart = L
        self._title = next(E for tag, E in L[1] if tag[0] == 'module:pie:title')
        slices, self._labels = zip( * (( (int(tag[1]['prop']), interpret_rgba(tag[1]['color'])), E) for tag, E in L[1] if tag[0] == 'module:pie:slice'))
        total = sum(P for P, C in slices)
                     # percentage | arc length | color
        self._slices = [(P/total, P/total*2*pi, C) for P, C in slices]
        
        self._FLOW = [Atomic_text(text) for text in chain([self._title], self._labels)]

    def represent(self, serialize, indent):
        lines = [(indent, _print_attrs( * self._chart[0]))]
        for tag, E in self._chart[1]:
            lines.append((indent + 1, _print_attrs( * tag)))
            lines.extend(serialize(E, indent + 2))
            lines.append((indent + 1, '</' + tag[0] + '>'))
        lines.append((indent, '</module:pie>'))
        return lines

    def fill(self, bounds, c, y):
        r = self._radius
        top = y
        # title
        self._FLOW[0].cast(bounds, c, y)
        y = self._FLOW[0]._SLUGS[-1]['y'] + 22
        left, right = bounds.bounds(y + r)
        px = (right + left)/2
        py = y + r
        for S in self._FLOW[1:]:
            S.cast(bounds, c, y)
            y += 20
        bottom = py + r + 22
        
        return _MBlock(self._FLOW, top, bottom, left, right, self._slices, (px, py, self._radius))

class _MBlock(Block):
    def __init__(self, FLOW, top, bottom, left, right, slices, pie):
        Block.__init__(self, FLOW, top, bottom, left, right)
        self._slices = slices
        self._slices_t = list(accumulate(s[1] for s in slices))
        print(self._slices_t)
        self._pie = pie
        self._active = None
    
    def _print_pie(self, cr):
        x, y, r = self._pie
        t = 0
        for i, S in enumerate(self._slices):
            percent, arc, color = S
            cr.move_to(x, y)
            cr.arc(x, y, r, t, t + arc)
            cr.close_path()
            cr.set_source_rgba( * color)
            cr.fill()
            
            if i == self._active:
                cr.set_line_width(2)
                cr.arc(x, y, r + 13, t, t + arc)
                cr.stroke()
            
            t += arc
    
    def _target_slice(self, x, y):
        px, py, r = self._pie
        t = atan2(y - py, x - px)
        if t < 0:
            t += 2*pi
        return bisect(self._slices_t, t)
    
    def I(self, x, y):
        s = self._target_slice(x, y)
        self._active = s
        return self._FLOW[s + 1]
    
    def deposit(self, repository):
        for A in self._FLOW:
            A.deposit(repository)
        repository['_paint'].append(self._print_pie)
