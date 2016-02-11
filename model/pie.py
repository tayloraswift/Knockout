from math import pi
from itertools import chain

from model.olivia import Atomic_text, Block
from edit.paperairplanes import interpret_rgba

def _print_attrs(name, attrs):
    if attrs:
        return '<' + name + ' ' + ' '.join(A + '="' + repr(V)[1:-1] + '"' for A, V in attrs.items()) + '>'  
    else:
        return '<' + name + '>'

class PieChart(object):
    def __init__(self, L):
        self._chart = L
        self._title = next(E for tag, E in L[1] if tag[0] == 'module:pie:title')
        slices, self._labels = zip( * (( (int(tag[1]['prop']), interpret_rgba(tag[1]['color'])), E) for tag, E in L[1] if tag[0] == 'module:pie:slice'))
        total = sum(P for P, C in slices)
                     # percentage | arc length | color
        self._slices = [(P/total, P/total*2*pi, C) for P, C in slices]
        
        self._FLOW = [Atomic_text(text) for text in chain([self._title], self._labels)]

    def represent(self, serialize, indent):
        lines = [(indent, '<module:pie>')]
        for tag, E in self._chart[1]:
            lines.append((indent + 1, _print_attrs( * tag)))
            lines.extend(serialize(E, indent + 2))
            lines.append((indent + 1, '</' + tag[0] + '>'))
        lines.append((indent, '</module:pie>'))
        return lines

    def _print_pie(self, cr, x, y):
        t = 0
        for percent, arc, color in self._slices:
            cr.move_to(x, y)
            cr.arc(x, y, 89, t, t + arc)
            cr.close_path()
            cr.set_source_rgba( * color)
            cr.fill()
            t += arc
    
    def fill(self, bounds, c, y):
        top = y
        # title
        self._FLOW[0].cast(bounds, c, y)
        y += 20
        for S in self._FLOW[1:]:
            S.cast(bounds, c, y)
            y += 20
        bottom = y
        left, right = bounds.bounds(top)
        return _MBlock(self._FLOW, top, bottom, left, right, lambda cr: self._print_pie(cr, (right + left)/2, top + 120))

class _MBlock(Block):
    def __init__(self, FLOW, top, bottom, left, right, paint):
        Block.__init__(self, FLOW, top, bottom, left, right)
        self._print = paint
    
    def I(self, x, y):
        return self['j']
    
    def deposit(self, repository):
        for A in self._FLOW:
            A.deposit(repository)
        repository['_paint'].append(self._print)
