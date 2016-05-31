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
    
    def inflate(self, width, ox, oy, slug, B):
        pl = self['pill_length']
        inflated = []
        for x, y, m in ((x*width, y, m) for x, y, m in self._compacted):
            factor = pl/sqrt(1 + m**2)
            dx = factor
            dy = -m*factor # because screen coordinates are opposite the virtual space (“downward sloping” is positive)
            inflated.append(((x - dx, y - dy), (x + dx, y + dy)))
        self._inflated = inflated
        return (), (self.paint,), ()
    
    def paint(self, cr):
        cr.set_source_rgba( * self['color'] )
        cr.set_line_width(self['pill_width'])
        for p1, p2 in self._inflated:
            cr.move_to( * p1 )
            cr.line_to( * p2 )
        cr.stroke()

class Axis(Plane):
    name = 'mod:plot:axis'
    DNA = [('class', 'blocktc', '_center'), ('cl_variable', 'texttc', 'emphasis'), ('variable', 'str', 'u'), 
            ('start', 'float', 0), ('stop', 'float', 12), ('number', 'float', 4), 
            ('line_width', 'float', 1), ('arrowhead', 'bool', True), ('pixel_align', 'bool', False), ('color', 'rgba', '#000')]
    
    def bubble(self, x):
        return (x - self['start']) / (self['stop'] - self['start'])

    def step(self, step, start=None, stop=None):
        if start is None:
            start = self['start']
        if stop is None:
            stop = self['stop']
        return (start + i * step for i in range(floor(abs(stop - start)/step) + 1))

    def _enum(self):
        if self['number'] > 0 and (self['stop'] - self['start']) / self['number'] < 1989:
            bubble = self.bubble
            return ((n, bubble(n)) for n in self.step(self['number']))
        else:
            return (self['start'], 0), (self['stop'], 1)
    
    def compact(self, system, height):
        A = next(i for i, a in enumerate(system) if a is self)
        begin = [0, 0, 0]
        begin[A] = self['start']
        end = [0, 0, 0]
        end[A] = self['stop']
        x1, y1 = system.to( * begin )
        x2, y2 = system.to( * end )
        self._compacted = x1, y1*height, x2, y2*height
        self._numbers = list(self._enum())
    
    def _pix_epsilon(self, u):
        e1 = (u + self['line_width']*0.5) % 1
        if 1 - e1 < e1:
            e1 -= 1
        e2 = - ((u - self['line_width']*0.5) % 1)
        if -1 - e2 > e2:
            e2 += 1
        if abs(e2) > abs(e1):
            return e1
        else:
            return e2
    
    def inflate(self, width, ox, oy, slug, B):
        x1, y1, x2, y2 = self._compacted[0]*width, self._compacted[1], self._compacted[2]*width, self._compacted[3]
        # align to pixels
        if self['pixel_align']:
            if x1 == x2:
                e = self._pix_epsilon(x2)
                x1 -= e
                x2 -= e
            elif y1 == y2:
                e = self._pix_epsilon(y2)
                y1 -= e
                y2 -= e
        self.inflated = (x1, y1), (x2, y2)
        
        variable = cast_mono_line(slug, list(self['variable']), 0, B, self['cl_variable'])
        k = variable['fstyle']['fontsize']*0.3
        v_distance = variable['fstyle']['fontsize']*1.5
        
        # calculate vectors
        totalvector = x2 - x1, y2 - y1
        inv_hyp = 1/sqrt(totalvector[0]**2 + totalvector[1]**2)
        vector = totalvector[0]*inv_hyp, totalvector[1]*inv_hyp
        perpendicular = vector[1], -vector[0]
        
        # bias perpendicular towards the bottom left
        if perpendicular[0] - perpendicular[1] > 0:
            perpendicular = -perpendicular[0], -perpendicular[1]
        self.perpendicular = perpendicular
        
        variable.nail_to(ox + x2 + v_distance*vector[0], oy + y2 + v_distance*vector[1], k, round((x2 - x1)*inv_hyp))
        
        mono = chain((variable,), self._generate_numbers(slug, ox, oy, B, k, totalvector))

        # arrowheads
        if self['arrowhead']:
            a_length = 8*self['line_width']
            angle = atan2(totalvector[1], totalvector[0]) + pi
            aa = 0.275
            a_distance = cos(aa)*a_length
            
            cx = x2 + a_distance*vector[0]
            cy = y2 + a_distance*vector[1]
            
            ax = cx + a_length * cos(angle - aa)
            ay = cy + a_length * sin(angle - aa)
            bx = cx + a_length * cos(angle + aa)
            by = cy + a_length * sin(angle + aa)
            self._arrow = (cx, cy), (ax, ay), (bx, by)
        if self.math:
            return mono, (self.paint,), ()
        else:
            return mono, (self.paint,), ()
    
    def _generate_numbers(self, slug, ox, oy, B, k, totalvector):
        dx, dy = totalvector
        space = 2.5*k
        ox += self.inflated[0][0] + space*self.perpendicular[0]
        oy += self.inflated[0][1] + space*self.perpendicular[1]
        
        sign = round(self.perpendicular[0])
        
        numerals = ((u, ox + dx*factor, oy + dy*factor) for u, factor in self._numbers if u)
        for u, x, y in numerals:
            label = cast_mono_line(slug, list(str(u).replace('-', '−')), 0, B)
            label.nail_to(x, y, k, sign)
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
    DNA = Blockelement.DNA + [('height', 'int', 189), ('azm', 'float', 0), ('alt', 'float', 'pi*0.5'), ('rot', 'float', 0), ('tickwidth', 'float', 0.5)]
    
    def _load(self):
        system = Cartesian(self.find_nodes(Axis, Axis, Axis))
        self._FLOW = list(chain(system, self.filter_nodes(Data)))
        for DS in self._FLOW:
            DS.compact(system, -self['height'])
        self._origin = system.to(0, 0, 0)
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
        if Y.content and X.content:
            if overlay is not None:
                Y_ol = overlay + Y['class']
                X_ol = overlay + X['class']
            else:
                Y_ol = Y['class']
                X_ol = X['class']
            Y.layout(Subcell(frames, -0.15, 0.15), u=u, overlay=Y_ol)

            frames.space(20)
            u, x1, x2, y, c, pn = frames.fit(self['height'])
            frames.space(20)
            X.layout(frames, u=u, overlay=X_ol)
            u = frames.read_u()
            Y.math = False
            X.math = False
            planes += [Y, X]
        else:
            u, x1, x2, y, c, pn = frames.fit(self['height'])
            Y.math = True
            X.math = True

        ytop = y - self['height']
        width = x2 - x1
        
        slug = {'l': 0, 'c': c, 'page': pn}
        
        monos = []
        paint_functions = []
        paint_annot_functions = []
        for E in self._FLOW:
            mono, paint, paint_annot = E.inflate(width, x1, y, slug, self)
            monos.extend(mono)
            paint_functions.extend((pn, (F, x1, y)) for F in paint)
            #paint_annot_functions.extend((pn, (F, x1, y)) for F in paint_annot)
        
        perp_x, perp_y = zip( * (A.perpendicular for A in self._CS) )
        O_label = cast_mono_line(slug, ['O'], 0, self, self._CS[0]['cl_variable'])
        k = O_label['fstyle']['fontsize']*0.3
        origin_k = 2.5*k
        O_label.nail_to(x1 + self._origin[0]*width + 1.1*origin_k*sum(perp_x), 
                        y + self._origin[1]*-self['height'] + origin_k*sum(perp_y), k, 0)
        monos.append(O_label)
        
        return u, monos, [], planes, paint_functions

members = [Plot, Axis, Slope]
#members.extend(chain.from_iterable(D.members for D in (scatterplot, f, histogram)))
