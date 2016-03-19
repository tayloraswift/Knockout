from math import log, e, cos, sin, pi, floor, ceil

from elements.elements import Node
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

class _Axis(Node):
    def freeze(self, h):
        self.scaleminor   = [int(round(x*h)) for x in self.minor]
        self.scalemajor   = [int(round(x*h)) for x in self.major]
        self.scalenumbers = [(int(round(x*h)), S) for x, S in self.numbers]

    def step(self, step, start=None, stop=None):
        if start is None:
            start = self['start']
        if stop is None:
            stop = self['stop']
        return (start + i * step for i in range(floor(abs(stop - start)/step) + 1))

class _LinearAxis(_Axis):
    ADNA = [('start', 0, 'float'), ('stop', 89, 'float'), ('minor', 1, 'float'), ('major', 2, 'float'), ('number', 4, 'float'), ('round', 13, 'int')]
    
    def _format(self, u):
        return (str(_soft_int(u, self['round']))).replace('-', '−')
    
    def enum(self):
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

class _LogAxis(_Axis):
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

    def enum(self):
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
    
class _Horizontal(object):
    def print_numbers(self, LINE, PP, F):
        for x, S in self.scalenumbers:
            XT = cast_mono_line(LINE, S, 13, PP, F)
            XT['x'] = x - XT['advance']/2
            XT['y'] = 20
            yield XT
    
    def draw(self, cr, tw):
        for x in self.scalemajor:
            cr.rectangle(x, 0, tw, 8)
        for x in self.scaleminor:
            cr.rectangle(x, 0, tw, 4)

class _Vertical(object):
    def print_numbers(self, LINE, PP, F):
        for y, S in self.scalenumbers:
            YT = cast_mono_line(LINE, S, 13, PP, F)
            YT['x'] = -YT['advance'] - 10
            YT['y'] = -y + 4
            yield YT
    
    def draw(self, cr, tw):
        for y in self.scalemajor:
            cr.rectangle(0, -y, -8, -tw)
        for y in self.scaleminor:
            cr.rectangle(0, -y, -4, -tw)

class X(object):
    pass
class Y(object):
    pass

class Linear_X(_LinearAxis, _Horizontal, X):
    name = namespace + ':x'

class Linear_Y(_LinearAxis, _Vertical, Y):
    name = namespace + ':y'

class Log_X(_LogAxis, _Horizontal, X):
    name = namespace + ':logx'

class Log_Y(_LogAxis, _Vertical, Y):
    name = namespace + ':logy'

"""
class Cartesian3(object):
    def __init__(self, xaxis, yaxis, zaxis, azimuth=0, altitude=pi*0.5, rotate=0):
        self.a = azimuth  #  0
        self.b = altitude # 90°
        self.c = rotate   #  0
        self.X = xaxis
        self.Y = yaxis
        self.Z = zaxis

    def project(self, x, y, z=0):
        u = self.X.U(x)
        v = self.Y.U(x)
        h0 = u*cos(self.a) - v*sin(self.a)
        k0 = (v*cos(self.a) + u*sin(self.a)) * sin(self.b)
        h = h0*cos(self.c) - k0*sin(self.c)
        k = k0*cos(self.c) + h0*sin(self.c)
        return h, k
"""
class Cartesian2(object):
    def __init__(self, xaxis, yaxis):
        self.X = xaxis
        self.Y = yaxis

    def project(self, x, y):
        return self.X.U(x) / self.X.R, self.Y.U(y) / self.Y.R

axismembers = [Linear_X, Linear_Y, Log_X, Log_Y]
