from math import floor, sqrt, atan2, sin, cos, pi, log, e, ceil, isclose

from itertools import chain

from layout.otline import cast_mono_line

from meredith.paragraph import Plane

def _vector_rotate(x, y, t):
    return x*cos(t) - y*sin(t), (y*cos(t) + x*sin(t))

def _spherical_to_cartesian(azm, alt):
    xf  = cos(azm)
    yf  = sin(azm)
    fac = cos(alt)
    return xf*fac, yf*fac, sin(alt)

class Cartesian(list):
    def __init__(self, axes, azimuth=0, altitude=0, rotate=0):
        self.a = azimuth
        self.b = altitude
        self.c = rotate

        # form axal unit vectors
        xhat =  cos(azimuth), sin(azimuth) * cos(altitude)
        yhat = -sin(azimuth), cos(azimuth) * cos(altitude)
        zhat =  0           , sin(altitude)
        self._unitaxes = (_vector_rotate( * xhat , rotate), _vector_rotate( * yhat , rotate), _vector_rotate( * zhat , rotate))
        
        self.camera = _spherical_to_cartesian(-pi*0.5 - azimuth, pi*0.5 - altitude)
        
        list.__init__(self, (axis for axis in axes if axis is not None))

        for axis in self:
            axis.make_bubble_f()
        
        self.center()
        self.z_center = self.Z( * ((axis['range'][0] + axis['range'][1])*0.5 for axis in self) )
    
    def center(self):
        self._centering = (0, 0)
        extreme1 = self.to( * (axis['range'][0] for axis in self) )
        extreme2 = self.to( * (axis['range'][1] for axis in self) )
        cx = (extreme1[0] + extreme2[0] - 1)*0.5
        cy = (extreme1[1] + extreme2[1] - 1)*0.5
        self._centering = (-cx, -cy)
    
    def to(self, * coord ):
        x, y = map(sum, zip( * ((U*avx, U*avy) for (avx, avy), U in zip(self._unitaxes, (axis.bubble(u) for axis, u in zip(self, chain(coord, (0, 0))))) ), self._centering ))
        return x, y
    
    def Z(self, * coord ):
        return sum(a*b for a, b in zip(self.camera, coord))
    
    def in_range(self, * coord ):
        return all(axis['range'][0] <= u <= axis['range'][1] for axis, u in zip(self, coord))

class Axis(Plane):
    name = 'mod:plot:axis'
    DNA = [('class', 'blocktc', '_center'), ('cl_variable', 'texttc', 'emphasis'), ('variable', 'str', ''), 
            ('range', 'range', '0:12'), ('minor', 'float', 1), ('major', 'float', 2), ('number', 'float', 4), 
            ('floor', 'bool', False), 
            ('line_width', 'float', 1), ('arrowhead', 'bool', False), ('axis', 'bool', False), ('ticks', 'bool', False), ('pixel_align', 'bool', True), ('color', 'rgba', '#000')]
    
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

    def make_bubble_f(self):
        i0 = self['range'][0]
        R = 1/(self['range'][1] - self['range'][0])
        def bubble(x):
            return (x - i0)*R
        self.bubble = bubble
    
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
        
        self._z_center = system.Z( * ((a + b)*0.5 for a, b in zip(begin, end)) )
        
    def _round_2sided(self, x):
        halfwidth = self['line_width']*0.5
        xminus = x - halfwidth
        xplus = x + halfwidth
        xminus_int = int(round(xminus))
        xplus_int = int(round(xplus))
        if abs(xplus_int - xplus) <= abs(xminus_int - xminus): # bias right
            return xplus_int - halfwidth
        else:
            return xminus_int + halfwidth
    
    def _hint_line(self, line, sign=1):
        if self['pixel_align']:
            # vhint
            if isclose(line[0][0], line[1][0], abs_tol=0.000001):
                x_int = -sign*self._round_2sided(-sign*line[0][0])
                return (x_int, line[0][1]), (x_int, line[1][1])
            
            # hhint
            elif isclose(line[0][1], line[1][1], abs_tol=0.000001):
                y_int = sign*self._round_2sided(sign*line[0][1])
                return (line[0][0], y_int), (line[1][0], y_int)
        return line
    
    def _calculate_vectors(self):
        totalvector = self._line[1][0] - self._line[0][0], self._line[1][1] - self._line[0][1]
        try:
            inv_hyp = 1/sqrt(totalvector[0]**2 + totalvector[1]**2)
        except ZeroDivisionError:
            inv_hyp = 0
        vector = totalvector[0]*inv_hyp, totalvector[1]*inv_hyp
        perpendicular = vector[1], -vector[0]
        
        # bias perpendicular towards the bottom left
        if perpendicular[0] - perpendicular[1] > 0:
            perpendicular = -perpendicular[0], -perpendicular[1]
        
        self._perpendicular = perpendicular
        return totalvector, vector, perpendicular
        
    def inflate(self, width, ox, oy, PARENTLINE, BSTYLE):
        x1, y1, x2, y2 = self._compact_line[0]*width, self._compact_line[1], self._compact_line[2]*width, self._compact_line[3]
        self._line = (x1, y1), (x2, y2)
        return self._construct(x2, y2, ox, oy, PARENTLINE, BSTYLE)
        
    def _construct(self, x2, y2, ox, oy, PARENTLINE, BSTYLE):
        totalvector, vector, perpendicular = self._calculate_vectors()
        
        # print variable
        variable = cast_mono_line(PARENTLINE, list(self['variable']), BSTYLE['__runinfo__'], self['cl_variable'])
        k = variable['fstyle']['fontsize']*0.3
        # arrowheads
        if self['arrowhead']:
            hp1, (hx2, hy2) = self._hint_line(self._line)
            
            a_length = 8*self['line_width']
            angle = atan2(totalvector[1], totalvector[0]) + pi
            aa = 0.275
            a_distance = cos(aa)*a_length
            
            x3 = hx2 + 0.5*a_distance*vector[0]
            y3 = hy2 + 0.5*a_distance*vector[1]
            
            cx = x3 + a_distance*vector[0]
            cy = y3 + a_distance*vector[1]
            
            ax = cx + a_length * cos(angle - aa)
            ay = cy + a_length * sin(angle - aa)
            bx = cx + a_length * cos(angle + aa)
            by = cy + a_length * sin(angle + aa)
            self._arrow = (cx, cy), (ax, ay), (bx, by)
            
            variable_space = 2.5*k + 1.5*a_distance
            self._extended_line = hp1, (x3, y3)
        else:
            variable_space = 4*k
            self._extended_line = self._hint_line(self._line)
        
        variable.nail_to(ox + x2 + variable_space*vector[0], oy + y2 + variable_space*vector[1], k, round(vector[0]))
        
        # ticks
        if self['ticks']:
            spacing = (2 - 0.5*self.floating) *k
            ticks = chain(self._generate_ticks(self._positions_to_xy(self._major, * self._line[0], * totalvector ), -spacing*self.floating, spacing), 
                          self._generate_ticks(self._positions_to_xy(self._minor, * self._line[0], * totalvector ), -0.5*spacing*self.floating, 0.5*spacing))
            self._ticks = list(map(self._hint_line, ticks))
        else:
            spacing = 0
        # numbers
        letterspacing = spacing + 2.5*k
        self.lettervector = letterspacing*perpendicular[0], letterspacing*perpendicular[1]
        mono = chain((variable,), self._generate_numbers(self._positions_to_xy(self._numbers, ox + self._line[0][0] + self.lettervector[0], 
                                                                                            oy + self._line[0][1] + self.lettervector[1], * totalvector), PARENTLINE, BSTYLE['__runinfo__'], k))
        return mono, ((self._z_center, self.paint),), ()
    
    def _positions_to_xy(self, positions, ox, oy, dx, dy):
        if self.floating:
            return ((ox + dx*factor, oy + dy*factor, u) for factor, u in positions if u)
        else:
            return ((ox + dx*factor, oy + dy*factor, u) for factor, u in positions)
    
    def _generate_numbers(self, numerals, PARENTLINE, runinfo, k):
        sign = round(self._perpendicular[0])
        for x, y, u in numerals:
            label = cast_mono_line(PARENTLINE, str(u).replace('-', '−'), runinfo)
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
            cr.move_to( * self._extended_line[0] )
            cr.line_to( * self._extended_line[1] )

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

def logrange(start, stop, step):
    if start > 0:
        la = ceil(round(log(start, step), 13))
    else:
        la = 0
    if stop > 0:
        lb = floor(round(log(stop, step), 13))
    else:
        lb = 0
    return 1, la, lb

def safelog(x, fl=1):
    if x > 0:
        return log(x)
    else:
        return fl

def _soft_int(n, decimals):
    if type(n) is float:
        if decimals < 13:
            n = round(n, 13)
        if n.is_integer():
            n = int(n)
        else:
            n = round(n, decimals)
    return n

class LogAxis(Axis):
    name = 'mod:plot:logaxis'
    DNA = Axis.DNA + [('base', 'float', 0), ('round', 'int', 13)]

    def _format_reg(self, u):
        exp = _soft_int(log(u, self._expressed_base), self['round'])
        if -4 < exp < 4:
            return (str(_soft_int(u, self['round']))).replace('-', '−')
        else:
            return (str(_soft_int(self._expressed_base, self['round'])) + ' E ' + str(exp)).replace('-', '−')

    def _format_e(self, u):
        exp = _soft_int(log(u), self['round'])
        return ('e E ' + str(exp)).replace('-', '−')
    
    def _attempt_set_format(self, b):
        if b < 0 or b == 1:
            self._format = self._format_e
            return False
        else:
            self._expressed_base = b
            self._format = self._format_reg
            return True

    def make_bubble_f(self):
        if self['base']:
            self._attempt_set_format(self['base'])
        else:
            self._attempt_set_format(self['number'])
        
        i0 = safelog(self['range'][0])
        R = 1/(safelog(self['range'][1]) - safelog(self['range'][0]))
        def bubble(x):
            return (safelog(x, i0) - i0)*R
        self.bubble = bubble

    def _enum(self, k):
        eformat = self._format
        if k > 0:
            if k == 1:
                k = e
            _, a, b = logrange( * self['range'] , k)
            if (b - a) / k < 1989:
                bubble = self.bubble
                return ((bubble(n), eformat(n)) for n in (k**m for m in self.step(1, a, b)))
        return (0, eformat(self['range'][0])), (1, eformat(self['range'][1]))

