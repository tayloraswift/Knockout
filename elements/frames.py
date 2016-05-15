from bisect import bisect

from itertools import chain

def accumulate_path(path):
    advance = 0
    for subpath in path:
        top = advance - subpath[0][1]
        advance += subpath[-1][1] - subpath[0][1]
        yield tuple((x, y + top) for x, y, a in subpath)

def piecewise(points, y):
    i = bisect([point[1] for point in points], y)
    
    try:
        x2, y2 = points[i]
    except IndexError:
        if y == points[-1][1]:
            return points[-1][0]
        else:
            raise ValueError('math domain error')
        
    x1, y1 = points[i - 1]
    return (x2 - x1)*(y - y1)/(y2 - y1) + x1

class Frame(list):
    def __init__(self, sides):
        list.__init__(self, sides[:-1])
        self.page = sides[-1]

    def __repr__(self):
        return ' ; '.join(chain((' '.join(str(x) + ',' + str(y) for x, y, a in side) for side in self), (str(self.page),)))

class Frames(list):
    def __init__(self, frames):
        list.__init__(self, (Frame(F) for F in frames))
        self._straighten()
    
    def _straighten(self):
        left, right = zip( * self )
        
        self._run = tuple(accumulate_path(left)), tuple(accumulate_path(right))
        self._segments = (0,) + tuple(F[-1][1] for F in self._run[0])
        
    def start(self, u):
        self._u = u
        self._c = bisect(self._segments, u) - 1
        self._top, self._limit = self._segments[self._c : self._c + 2]
        self._y0 = self[self._c][0][0][1]
    
    def fit(self, gap, du):
        u = self._u + gap + du
        if u > self._limit:
            self._c += 1
            self._u = self._limit
            self._top, self._limit = self._segments[self._c : self._c + 2]
            self._y0 = self[self._c][0][0][1]
            return self.fit(gap, du)
        else:
            x1 = piecewise(self._run[0][self._c], u)
            x2 = piecewise(self._run[1][self._c], u)
            y = self._y0 + u - self._top
            self._u = u
            return u, x1, x2, y, self._c
    
    def __repr__(self):
        return ' |\n    '.join(repr(F) for F in self)
