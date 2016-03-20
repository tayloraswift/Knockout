from math import log, e, cos, sin, pi, floor, ceil
from itertools import chain

from elements.node import Node
from model.cat import cast_mono_line

namespace = 'mod:plot'

def _soft_int(n, decimals):
    if type(n) is float:
        if decimals < 13:
            n = round(n, 13)
        if n.is_integer():
            n = int(n)
        else:
            n = round(n, decimals)
    return n

class Axis(Node):
    def __init__(self, * args, ** kwargs):
        Node.__init__(self, * args, ** kwargs)
        self._enum()
    
    def step(self, step, start=None, stop=None):
        if start is None:
            start = self['start']
        if stop is None:
            stop = self['stop']
        return (start + i * step for i in range(floor(abs(stop - start)/step) + 1))

class LinearAxis(Axis):
    name = namespace + ':axis'
    ADNA = [('start', 0, 'float'), ('stop', 89, 'float'), ('minor', 1, 'float'), ('major', 2, 'float'), ('number', 4, 'float'), ('round', 13, 'int')]
    
    def _format(self, u):
        return (str(_soft_int(u, self['round']))).replace('-', '−')
    
    def _enum(self):
        major = self['major']
        minor = self['minor']
        number = self['number']
        start = self['start']
        self.U = lambda x: x - start
        R = self.U(self['stop'])
        self.R = R

        self.minor   = [x/R for x in (i*minor for i in range(floor((self['stop'] - start) / minor) + 1)) if x % major]
        self.major   = [x/R for x in (i*major for i in range(floor((self['stop'] - start) / major) + 1))]
        self.numbers = [(x/R, self._format(x + start)) for x in (i*number for i in range(floor((self['stop'] - start) / number) + 1))]
        

def floorlog(x, fl=1):
    try:
        return log(x)
    except ValueError:
        return fl

def logrange(start, stop, step):
    if start > 0:
        la = ceil(round(log(start, step), 13))
    else:
        la = 0
    if stop > 0:
        lb = floor(round(log(stop, step), 13))
    else:
        lb = 0
    return range(la, lb + 1)

def logbasevalid(b, number):
    if b:
        if b <= 0 or b == 1:
            return e
        else:
            return b
    else:
        return number

class LogAxis(Axis):
    name = namespace + ':logaxis'
    ADNA = [('start', 0, 'float'), ('stop', 10000, 'float'), ('minor',  10, 'float'), ('major', 10, 'float'), ('number', 100, 'float'), ('base', 0, 'float'), ('round', 13, 'int')]

    def _format_reg(self, u):
        exp = _soft_int(log(u, self._expressed_base), self['round'])
        if -4 < exp < 4:
            return (str(_soft_int(u, self['round']))).replace('-', '−')
        else:
            return (str(_soft_int(self._expressed_base, self['round'])) + ' E ' + str(exp)).replace('-', '−')

    def _format_e(self, u):
        exp = _soft_int(log(u), self['round'])
        return ('e E ' + str(exp)).replace('-', '−')

    def _set_base(self, expressed_base, number):
        if expressed_base:
            if expressed_base < 0 or expressed_base == 1:
                self._format = self._format_e
                return
            else:
                self._expressed_base = expressed_base
        else:
            self._expressed_base = number
        self._format = self._format_reg

    def _enum(self):
        self._set_base(self['base'], self['number'])
        if self['start'] > 0:
            i0 = log(self['start'])
            self.U = lambda x: floorlog(x, i0) - i0
        else:
            self.U = floorlog
        
        number = logbasevalid(self['number'], e)
        minor  = logbasevalid(self['minor'], number)
        major  = logbasevalid(self['major'], number)
                        
        R = self.U(self['stop'])
        majorticks = set(major**i for i in logrange(self['start'], self['stop'], major))
        self.major   = [self.U(x)/R for x in majorticks]
        self.minor   = [self.U(x)/R for x in (minor**i for i in logrange(self['start'], self['stop'], minor)) if x not in majorticks]
        self.numbers = [(self.U(x)/R, self._format(x)) for x in (number**i for i in logrange(self['start'], self['stop'], number))]
        self.R = R

class Cartesian(list):
    def __init__(self, axes):
        self.unitaxis = ((1, 0), (0, 1))
        list.__init__(self, axes)

    def fit(self, * coord ):
        return tuple(axis.U(i) / axis.R for axis, i in zip(self, coord))
    
    def freeze(self, h, k):
        self.project = lambda x, y: (x*h, y*k)
        self.h = h
        self.k = k
        # freeze axes
        self.ticks = tuple(tuple(chain(( (int(round(x*scale)), 4) for x in axis.minor), ( (int(round(x*scale)), 8) for x in axis.major))) 
                for axis, scale in zip(self, (h, k)))
        self.scalenumbers = tuple(tuple((int(round(x*scale)), S) for x, S in axis.numbers) for axis, scale in zip(self, (h, k)))

    def _numbers_x(self, LINE, PP, F):
        for x, S in self.scalenumbers[0]:
            XT = cast_mono_line(LINE, S, 13, PP, F)
            XT['x'] = x - XT['advance']/2
            XT['y'] = 20
            yield XT
    
    def _numbers_y(self, LINE, PP, F):
        for y, S in self.scalenumbers[1]:
            YT = cast_mono_line(LINE, S, 13, PP, F)
            YT['x'] = -YT['advance'] - 10
            YT['y'] = y + 4
            yield YT
    
    def yield_numbers(self, LINE, PP, F):
        return chain(self._numbers_x(LINE, PP, F), self._numbers_y(LINE, PP, F))
        
    def draw(self, cr, tw):
        for x, l in self.ticks[0]:
            cr.rectangle(x, 0, tw, l)
        for y, l in self.ticks[1]:
            cr.rectangle(0, y, -l, -tw)

def _vector_rotate(x, y, t):
    return x*cos(t) - y*sin(t), (y*cos(t) + x*sin(t))

def _magnitude(vector, h, k):
    boxslope = k/h
    vectorslope = vector[1] / vector[0]
    if vectorslope > boxslope:
        return k*(vector[0] / vector[1]), k
    else:
        return h, h*vectorslope

class Cartesian3(Cartesian):
    def __init__(self, axes, azimuth=0, altitude=0, rotate=0):
        self.a = azimuth
        self.b = altitude
        self.c = rotate

        # form axal unit vectors
        xhat = cos(self.a), sin(self.a) * cos(self.b)
        yhat = cos(self.a + pi*0.5), sin(self.a + pi*0.5) * cos(self.b)
        zhat = 0, sin(self.b)
        self.unitaxis = (_vector_rotate( * xhat, self.c), _vector_rotate( * yhat, self.c), _vector_rotate( * zhat, self.c))
        list.__init__(self, axes)
    
    def freeze(self, h, k):
        xv, yv, zv = (_magnitude(vector, h, k) for vector in self.unitaxis)
        self.project = lambda x, y, z=0: (x*xv[0] + y*yv[0] + z*zv[0], x*xv[1] + y*yv[1] + z*zv[1])
        self.h = h
        self.k = k

axismembers = [LinearAxis, LogAxis]
