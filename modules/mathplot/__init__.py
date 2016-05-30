from math import floor, sqrt, atan2, sin, cos, pi
from bisect import bisect
from itertools import chain

from meredith.paragraph import Plane, Blockelement
from olivia.frames import Subcell
from layout.line import cast_mono_line

from state.exceptions import LineOverflow

class Cartesian(list):
    def __init__(self, axes):
        list.__init__(self, (axis for axis in axes if axis is not None))

    def to(self, * coord ):
        return tuple(axis.bubble(i) for axis, i in zip(self, coord))
    
class Data(Plane):
    name = 'mod:plot:data'

class Slope(Data):
    name = 'mod:plot:slope'
    DNA = [('m', 'fx', 'x + y'), ('dx', 'float', 1), ('dy', 'float', 1), ('pill_width', 'float', 1), ('pill_length', 'float', 5), ('color', 'rgba', '#ff0085')]
    
    def compact(self, system, height):
        P = []
        Fxy = self['m']
        to = system.to
        # fill in x
        for y in system[1].step(self['dy']):
            for x in system[0].step(self['dx']):
                try:
                    gx, gy = to(x, y)
                    P.append((gx, gy * height, Fxy(x, y)))
                except (ZeroDivisionError, ValueError):
                    pass
        self._compacted = P
    
    def inflate(self, width):
        pl = self['pill_length']
        inflated = []
        for x, y, m in ((x*width, y, m) for x, y, m in self._compacted):
            factor = pl/sqrt(1 + m**2)
            dx = factor
            dy = -m*factor # because screen coordinates are opposite the virtual space (“downward sloping” is positive)
            inflated.append(((x - dx, y - dy), (x + dx, y + dy)))
        self._inflated = inflated
    
    def paint(self, cr):
        cr.set_source_rgba( * self['color'] )
        cr.set_line_width(self['pill_width'])
        for p1, p2 in self._inflated:
            cr.move_to( * p1 )
            cr.line_to( * p2 )
        cr.stroke()
    
class Axis(Plane):
    name = 'mod:plot:axis'
    DNA = [('class', 'blocktc', '_center'), ('start', 'float', 0), ('stop', 'float', 12), ('line_width', 'float', 1.5), ('arrowhead', 'bool', True), ('color', 'rgba', '#000')]
    
    def bubble(self, x):
        return (x - self['start']) / (self['stop'] - self['start'])

    def step(self, step, start=None, stop=None):
        if start is None:
            start = self['start']
        if stop is None:
            stop = self['stop']
        return (start + i * step for i in range(floor(abs(stop - start)/step) + 1))
    
    def compact(self, system, height):
        A = next(i for i, a in enumerate(system) if a is self)
        begin = [0, 0, 0]
        begin[A] = self['start']
        end = [0, 0, 0]
        end[A] = self['stop']
        x1, y1 = system.to( * begin )
        x2, y2 = system.to( * end )
        self._compacted = x1, y1*height, x2, y2*height

    def inflate(self, width):
        self.inflated = (self._compacted[0]*width, self._compacted[1]), (self._compacted[2]*width, self._compacted[3])
        # arrowheads
        if self['arrowhead']:
            (x1, y1), (x2, y2) = self.inflated
            length = 6*self['line_width']
            angle = atan2((y2 - y1), (x2 - x1)) + pi
            
            dx = x2 - x1
            if dx:
                m = (y2 - y1)/dx
                factor = length/sqrt(1 + m**2)*0.5
                x2 += factor
                y2 += -m*factor
            else:
                y2 += -length*0.5
            
            ax = x2 + length * cos(angle - 0.3)
            ay = y2 + length * sin(angle - 0.3)
            bx = x2 + length * cos(angle + 0.3)
            by = y2 + length * sin(angle + 0.3)
            self._arrow = (x2, y2), (ax, ay), (bx, by)
    
    def generate_numbers(self, slug, B, T, ox, oy, align=1):
        numerals = (self['start'], * self.inflated[0]), (self['stop'], * self.inflated[-1])
        for numeral, x, y in numerals:
            label = cast_mono_line(slug, list(str(numeral).replace('-', '−')), 0, B, T)
            if align:
                if align > 0:
                    label['x'] = x + ox
                else:
                    label['x'] = x + ox - label['advance']
            else:
                label['x'] = x + ox - label['advance']*0.5
            label['y'] = y + oy
            yield label
    
    def paint(self, cr):
        cr.set_source_rgba( * self['color'] )
        cr.set_line_width(self['line_width'])
        cr.move_to( * self.inflated[0] )
        cr.line_to( * self.inflated[1] )
        cr.close_path()
        cr.stroke()
        if self['arrowhead']:
            cr.move_to( * self._arrow[0] )
            cr.line_to( * self._arrow[1] )
            cr.line_to( * self._arrow[2] )
            cr.close_path()
            cr.fill()
    
class Plot(Blockelement):
    name = 'mod:plot'
    DNA = [('class', 'blocktc', 'body'), ('cl_variable', 'texttc', 'emphasis'), ('cl_constant', 'texttc', ''), ('height', 'int', 189), ('azm', 'float', 0), ('alt', 'float', 'pi*0.5'), ('rot', 'float', 0), ('tickwidth', 'float', 0.5)]
    
    def _load(self):
        system = Cartesian(self.find_nodes(Axis, Axis, Axis))
        self._FLOW = list(chain(system, self.filter_nodes(Data)))
        for DS in self._FLOW:
            DS.compact(system, -self['height'])
        self._CS = system
        
    def regions(self, x, y):
        if y > 0:
            return 0
        elif y < -self['height'] and x < self._yaxis_div:
            return 1
        else:
            return len(self._CS) + self._KEY.target(y)
    
    def _layout_block(self, frames, BSTYLE, cascade, overlay):
        u = frames.read_u()
        
        planes = []
        X, Y, * DATA = self._FLOW
        if Y.content:
            if overlay is not None:
                Y_ol = overlay + Y['class']
            else:
                Y_ol = Y['class']
            Y.layout(frames, u=u, overlay=Y_ol)
            planes.append(Y)
        frames.space(40)

        u, x1, x2, y, c, pn = frames.fit(self['height'])
        ytop = y - self['height']
        width = x2 - x1
        
        paint_functions = []
        for E in self._FLOW:
            E.inflate(width)
            paint_functions.append((pn, (E.paint, x1, y)))

        # axis labels
        slug = {'l': 0, 'c': c, 'page': pn}
        y_label = cast_mono_line(slug, ['y'], 0, self, self['cl_variable'])
        y_label['x'] = x1 + Y.inflated[-1][0] - y_label['advance']*0.5
        y_label['y'] = y + Y.inflated[-1][1] - y_label['fstyle']['fontsize']*0.8

        x_label = cast_mono_line(slug, ['x'], 0, self, self['cl_variable'])
        x_label['x'] = x1 + X.inflated[-1][0] + x_label['fstyle']['fontsize']*0.8
        x_label['y'] = y + X.inflated[-1][1] + x_label['fstyle']['fontsize']*0.3
        
        ox = x1 - x_label['fstyle']['fontsize']*0.45
        oy = y + x_label['fstyle']['fontsize']*1.1
        O_label = cast_mono_line(slug, ['O'], 0, self, self['cl_variable'])
        O_label['x'] = Y.inflated[0][0] - O_label['advance'] + ox
        O_label['y'] = X.inflated[0][1] + oy
        
        labels = [x_label, y_label, O_label]
        labels.extend(X.generate_numbers(slug, self, self['cl_constant'], x1, oy, 0))
        labels.extend(Y.generate_numbers(slug, self, self['cl_constant'], ox, y + x_label['fstyle']['fontsize']*0.3, -1))
        
        return u, labels, [], planes, paint_functions
        

members = [Plot, Axis, Slope]
#members.extend(chain.from_iterable(D.members for D in (scatterplot, f, histogram)))
