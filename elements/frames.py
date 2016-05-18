from bisect import bisect

from itertools import chain

from elements import datablocks

from state.exceptions import LineOverflow

def accumulate_path(path):
    advance = 0
    for subpath in path:
        top = advance - subpath[0][1]
        advance += subpath[-1][1] - subpath[0][1]
        yield tuple((x, y + top) for x, y, a in subpath)

def piecewise(points, y):
    i = bisect([point[1] for point in points], y)
    
    try:
        x2, y2, *_ = points[i]
    except IndexError:
        if y >= points[-1][1]:
            return points[-1][0]
        else:
            return points[0][0]
        
    x1, y1, *_ = points[i - 1]
    return (x2 - x1)*(y - y1)/(y2 - y1) + x1

class Frame(list):
    def __init__(self, sides):
        list.__init__(self, sides[:-1])
        self.page = sides[-1]

    def inside(self, x, y, radius):
        return y >= self[0][0][1] - radius and y <= self[1][-1][1] + radius and x >= piecewise(self[0], y) - radius and x <= piecewise(self[1], y) + radius

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
    
    def y2u(self, y, c):
        return min(max(0, y - self[c][0][0][1]) + self._segments[c], self._segments[c + 1] - 0.000001)
    
    def start(self, u):
        self.overflow = False
        self._u = u
        self._c = bisect(self._segments, u) - 1
        self._top, self._limit = self._segments[self._c : self._c + 2]
        self._y0 = self[self._c][0][0][1]
    
    def _next_frame(self):
        self._c += 1
        try:
            self._top, self._limit = self._segments[self._c : self._c + 2]
            self._u = self._top
            self._y0 = self[self._c][0][0][1]
        except ValueError:
            self.overflow = True
            raise LineOverflow
    
    def space(self, du):
        u = self._u + du
        if u > self._limit:
            self._next_frame()
        else:
            self._u = u
        
    def fit(self, du):
        u = self._u + du
        if u > self._limit:
            self._next_frame()
            return self.fit(du)
        else:
            x1 = piecewise(self._run[0][self._c], u)
            x2 = piecewise(self._run[1][self._c], u)
            y = self._y0 + u - self._top
            self._u = u
            return u, x1, x2, y, self._c, self[self._c].page
    
    def which(self, x0, y0, radius):
        norm = datablocks.DOCUMENT.medium.normalize_XY
        for c, frame in enumerate(self):
            x, y = norm(x0, y0, frame.page)
            if frame.inside(x, y, radius):
                return c, frame.page
        return None, None
    
    def __repr__(self):
        return ' |\n    '.join(repr(F) for F in self)
