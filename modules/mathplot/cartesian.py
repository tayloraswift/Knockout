from math import floor, sqrt, atan2, sin, cos, pi

from itertools import chain

from layout.line import cast_mono_line

from meredith.paragraph import Plane

def _vector_rotate(x, y, t):
    return x*cos(t) - y*sin(t), (y*cos(t) + x*sin(t))

class Cartesian(list):
    def __init__(self, axes, azimuth=0, altitude=0, rotate=0):
        self.a = azimuth
        self.b = altitude
        self.c = rotate

        # form axal unit vectors
        xhat = cos(self.a), sin(self.a) * cos(self.b)
        yhat = cos(self.a + pi*0.5), sin(self.a + pi*0.5) * cos(self.b)
        zhat = 0, sin(self.b)
        self._unitaxes = (_vector_rotate( * xhat , self.c), _vector_rotate( * yhat , self.c), _vector_rotate( * zhat , self.c))
        list.__init__(self, (axis for axis in axes if axis is not None))
    
    def to(self, * coord ):
        x, y = map(sum, zip( * ((U*avx, U*avy) for (avx, avy), U in zip(self._unitaxes, (axis.bubble(u) for axis, u in zip(self, chain(coord, (0, 0))))) ) ))
        return x, y
    
    def in_range(self, * coord ):
        return all(axis['range'][0] <= u <= axis['range'][1] for axis, u in zip(self, coord))

class Axis(Plane):
    name = 'mod:plot:axis'
    DNA = [('class', 'blocktc', '_center'), ('cl_variable', 'texttc', 'emphasis'), ('variable', 'str', 'u'), 
            ('range', 'range', '0:12'), ('minor', 'float', 1), ('major', 'float', 2), ('number', 'float', 4), 
            ('floor', 'bool', False), 
            ('line_width', 'float', 1), ('arrowhead', 'bool', True), ('axis', 'bool', True), ('ticks', 'bool', False), ('pixel_align', 'bool', False), ('color', 'rgba', '#000')]
    
    def bubble(self, x):
        return (x - self['range'][0]) / (self['range'][1] - self['range'][0])

    def step(self, step, start=None, stop=None):
        if start is None:
            start = self['range'][0]
        if stop is None:
            stop = self['range'][1]
        if start > stop:
            stop, start = start, stop
        return (start + i * step for i in range(floor((stop - start)/step) + 1))

    def _enum(self, k):        
        if k > 0 and (self['range'][1] - self['range'][0]) / k < 1989:
            bubble = self.bubble
            return ((bubble(n), n) for n in self.step(k))
        else:
            return (0, self['range'][0]), (1, self['range'][1])
    
    def compact(self, system, height):
        A = next(i for i, a in enumerate(system) if a is self)
        if self['floor'] or not system.in_range(0, 0, 0):
            begin = [axis['range'][0] for axis in system]
            end = [axis['range'][0] for axis in system]
            self.floating = False
        else:
            begin = [0, 0, 0]
            end = [0, 0, 0]
            self.floating = True
        
        begin[A], end[A] = self['range']
        
        x1, y1 = system.to( * begin )
        x2, y2 = system.to( * end )
        
        self._compact_line = x1, y1*height, x2, y2*height
        self._numbers = list(self._enum(self['number']))
        if self['ticks']:
            self._major = list(self._enum(self['major']))
            majorticks = set(u for U, u in self._major)
            self._minor = [tick for tick in self._enum(self['minor']) if tick[1] not in majorticks]
    
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
    
    def _calculate_vectors(self):
        totalvector = self._line[1][0] - self._line[0][0], self._line[1][1] - self._line[0][1]
        inv_hyp = 1/sqrt(totalvector[0]**2 + totalvector[1]**2)
        vector = totalvector[0]*inv_hyp, totalvector[1]*inv_hyp
        perpendicular = vector[1], -vector[0]
        
        # bias perpendicular towards the bottom left
        if perpendicular[0] - perpendicular[1] > 0:
            perpendicular = -perpendicular[0], -perpendicular[1]
        
        self._perpendicular = perpendicular
        return totalvector, vector, perpendicular
        
    def inflate(self, width, ox, oy, slug, B):
        x1, y1, x2, y2 = self._compact_line[0]*width, self._compact_line[1], self._compact_line[2]*width, self._compact_line[3]
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
        
        self._line = (x1, y1), (x2, y2)        
        return self._construct(x2, y2, ox, oy, slug, B)
        
    def _construct(self, x2, y2, ox, oy, slug, B):
        totalvector, vector, perpendicular = self._calculate_vectors()
        
        # print variable
        variable = cast_mono_line(slug, list(self['variable']), 0, B, self['cl_variable'])
        k = variable['fstyle']['fontsize']*0.3
        variable.nail_to(ox + x2 + 5*k*vector[0], oy + y2 + 5*k*vector[1], k, round(vector[0]))
        
        # ticks
        if self['ticks']:
            spacing = (2 - 0.5*self.floating) *k
            self._ticks = list(chain(self._generate_ticks(self._positions_to_xy(self._major, * self._line[0], * totalvector ), -spacing*self.floating, spacing), 
                                    self._generate_ticks(self._positions_to_xy(self._minor, * self._line[0], * totalvector ), -0.5*spacing*self.floating, 0.5*spacing)))
        else:
            spacing = 0
        # numbers
        letterspacing = spacing + 2.5*k
        self.lettervector = letterspacing*perpendicular[0], letterspacing*perpendicular[1]
        mono = chain((variable,), self._generate_numbers(self._positions_to_xy(self._numbers, ox + self._line[0][0] + self.lettervector[0], 
                                                                                            oy + self._line[0][1] + self.lettervector[1], * totalvector), slug, B, k))

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
        
        return mono, (self.paint,), ()
    
    def _positions_to_xy(self, positions, ox, oy, dx, dy):
        if self.floating:
            return ((ox + dx*factor, oy + dy*factor, u) for factor, u in positions if u)
        else:
            return ((ox + dx*factor, oy + dy*factor, u) for factor, u in positions)
    
    def _generate_numbers(self, numerals, slug, B, k):
        sign = round(self._perpendicular[0])
        for x, y, u in numerals:
            label = cast_mono_line(slug, list(str(u).replace('-', '−')), 0, B)
            label.nail_to(x, y, k, sign)
            yield label
    
    def _generate_ticks(self, positions, a, b):
        dx1 = self._perpendicular[0]*a
        dx2 = self._perpendicular[0]*b
        dy1 = self._perpendicular[1]*a
        dy2 = self._perpendicular[1]*b
        for x, y, u in positions:
            yield (x + dx1, y + dy1), (x + dx2, y + dy2)
    
    def paint(self, cr):
        cr.set_source_rgba( * self['color'] )
        cr.set_line_width(self['line_width'])
        if self['axis']:
            cr.move_to( * self._line[0] )
            cr.line_to( * self._line[1] )
            cr.close_path()
        if self['ticks']:
            for p1, p2 in self._ticks:
                cr.move_to( * p1 )
                cr.line_to( * p2 )
        cr.stroke()
        if self['arrowhead']:
            cr.move_to( * self._arrow[0] )
            cr.line_to( * self._arrow[1] )
            cr.line_to( * self._arrow[2] )
            cr.close_path()
            cr.fill()
