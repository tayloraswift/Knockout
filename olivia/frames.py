from math import inf as infinity

from bisect import bisect

from itertools import chain

from meredith import datablocks

from state.exceptions import LineSplit

from olivia.basictypes import interpret_int

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
    
    def assign(self, A, S):
        if A == 'page':
            self.page = interpret_int(S)
            datablocks.DOCUMENT.layout_all()
        
    def inside(self, x, y, radius):
        return y >= self[0][0][1] - radius and y <= self[1][-1][1] + radius and x >= piecewise(self[0], y) - radius and x <= piecewise(self[1], y) + radius

    ## used by Frames object ##
    def inside_vertical(self, y):
        return self[0][0][1] <= y <= self[1][-1][1]

    ## used by editor ##
    def which_portal(self, x, y, radius):
        portal = (None, 0, 0)
        if -radius - 5 <= y - self[0][0][1] <= radius:
            if self[0][0][0] < x < self[1][0][0]:
                portal = ('entrance', x - self[0][0][0], y - self[0][0][1])

        elif -radius <= y - self[1][-1][1] <= radius + 5:
            if self[0][-1][0] < x < self[1][-1][0]:
                portal = ('portal', x - self[1][-1][0], y - self[1][-1][1])
        return portal

    def insert_point(self, r, y):
        y = 10*round(y*0.1)
        # make sure to only insert points between the portals
        if self.inside_vertical(y):
            x = 10*round(piecewise(self[r], y)*0.1)
            i = bisect([point[1] for point in self[r]], y)
            self[r].insert(i, [x, y, False])
            return i
        else:
            return None
    
    def can_fall(self, x, y):
        return not (x, y) in set((p[0], p[1]) for p in chain(self[0], self[1]))

    def fix_r(self, r):
        # removes points that are outside the portals
        self[r][:] = [point for point in self[r] if self.inside_vertical(point[1])]
        # sort list
        self[r].sort(key = lambda k: k[1])
    
    def __repr__(self):
        return ' ; '.join(chain((' '.join(str(x) + ',' + str(y) for x, y, a in side) for side in self), (str(self.page),)))

class Frames(list):
    def __init__(self, frames):
        list.__init__(self, (Frame(F) for F in frames))
        self._savestack = []
        self._straighten()
    
    def make_page_copy(self, offset):
        return self.__class__(((F[0], F[1], F.page + offset) for F in self))
    
    def _straighten(self):
        left, right = zip( * self )
        
        acc_left = tuple(accumulate_path(left))
        acc_right = tuple(accumulate_path(right))
                                                                                                    # lateral bounds cannot be infinity
        self._run = acc_left + ((acc_left[-1][-1], (acc_left[-1][-1][0], infinity)),) , acc_right + (((1989000, acc_right[-1][-1][1]), (1989000, infinity)),)
        self._segments = 0, * (F[-1][1] for F in self._run[0]) , infinity
        self._yy = * (F[0][0][1] for F in self), self[-1][0][-1][1]
    
    def y2u(self, y, c):
        return min(max(0, y - self._yy[c]) + self._segments[c], self._segments[c + 1] - 0.000001)
    
    def start(self, u, split=None):
        self.overflow = False
        if split is not None:
            self._break_on_split = split
        self._u = u
        self._c = bisect(self._segments, u) - 1
        self._top, self._limit = self._segments[self._c : self._c + 2]
        self._y0 = self._yy[self._c]
        try:
            self._pn = self[self._c].page
        except IndexError:
            self.overflow = True
            self._pn = None
    
    def save_u(self):
        self._savestack.append((self._u, self._c, self._top, self._limit, self._y0, self._break_on_split))
    
    def restore_u(self):
        self._u, self._c, self._top, self._limit, self._y0, self._break_on_split = self._savestack.pop()
    
    def read_u(self):
        return self._u
    
    def _next_frame(self):
        self._c += 1
        self._top, self._limit = self._segments[self._c : self._c + 2]
        self._u = self._top
        self._y0 = self._yy[self._c]
        try:
            self._pn = self[self._c].page
        except IndexError:
            self.overflow = True
            self._pn = None
            
        if self._break_on_split:
            raise LineSplit
        
    def space(self, du):
        u = self._u + du
        if u > self._limit:
            self._u = self._limit
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
            return u, x1, x2, y, self._c, self._pn
    
    def at(self, u):
        c = bisect(self._segments, u) - 1
        y = self._yy[c] + u - self._segments[c]
        return piecewise(self._run[0][c], u), piecewise(self._run[1][c], u), y, self._pn
        
    def which(self, x0, y0, radius):
        norm = datablocks.DOCUMENT.normalize_XY
        for c, frame in enumerate(self):
            x, y = norm(x0, y0, frame.page)
            if frame.inside(x, y, radius):
                return c, frame.page
        return None, None
    
    def fix(self, c=None):
        if c is not None:
            self[c].fix_r(0)
            self[c].fix_r(1)
        self._straighten()
    
    def freeze(self):
        self._break_on_split += 1
    
    def unfreeze(self):
        self._break_on_split -= 1
        if self._break_on_split < 0:
            raise RuntimeError
    
    ## used by editor ##
    
    def which_point(self, x0, y0, radius):
        P, C, R = None, None, None
        norm = datablocks.DOCUMENT.normalize_XY
        for c, frame in enumerate(self):
            x, y = norm(x0, y0, frame.page)
            inside = frame.inside_vertical(y)
            for r, railing in enumerate(frame):
                for i, point in enumerate(railing):
                    if abs(x - point[0]) + abs(y - point[1]) < radius:
                        return frame.page, c, r, i
                # if that fails, take a railing, if possible
                if inside and abs(x - piecewise(frame[r], y)) <= radius:
                    P = frame.page
                    C = c
                    R = r
            if frame.inside(x, y, radius):
                P = frame.page
                C = c
        return P, C, R, None
    
    def is_selected(self, c, r, i):
        try:
            return self[c][r][i][2]
        except TypeError:
            return False
    
    def make_selected(self, c, r, i, mod):
        if mod == 'ctrl':
            self[c][r][i][2] = not self[c][r][i][2]
        else:
            self[c][r][i][2] = True
        
    def clear_selection(self):
        cfi = chain.from_iterable
        for point in cfi(cfi(frame) for frame in self):
            point[2] = False

    def expand_selection(self, c):
        if c is None:
            self._select_all()
        else:
            touched = False
            for point in chain.from_iterable(self[c]):
                if not point[2]:
                    point[2] = True
                    touched = True
            if not touched:
                self._select_all()
    
    def _select_all(self):
        cfi = chain.from_iterable
        for point in cfi(cfi(frame) for frame in self):
            point[2] = True

    def delete_selection(self):
        changed = False
        for r, railing in chain.from_iterable(enumerate(frame) for frame in self):
            remain = [point for i, point in enumerate(railing) if not point[2] or i == 0 or i == len(railing) - 1]
            if len(remain) != len(railing):
                railing[:] = remain
                changed = True
        return changed

    def translate_selection(self, x, y, x0, y0):
        x, y = 10*round(x/10), 10*round(y/10)
        
        # survey conditions
        for frame in self:
            for point in chain(frame[0], frame[1]):
                if point[2]:
                    # do any of the points fall on another point?
                    if not frame.can_fall(point[0] + x - x0, point[1] + y - y0):
                        return

        for frame in self:
            for point in chain(frame[0], frame[1]):
                if point[2]:
                    point[:2] = [point[0] + x - x0, point[1] + y - y0]

            # check y alignment
            if frame[0][0][1] != frame[1][0][1]:
                # determine which should move
                if frame[0][0][2]:
                    flip = 1
                else:
                    flip = 0
                frame[flip][0][1] = frame[not flip][0][1]

            if frame[0][-1][1] != frame[1][-1][1]:
                # determine which should move
                if frame[0][-1][2]:
                    flip = 1
                else:
                    flip = 0
                frame[flip][-1][1] = frame[not flip][-1][1]
    
    def add_frame(self):
        x1, y1, x2 = self[-1][0][-1][0], self[-1][0][-1][1] + 40, self[-1][1][-1][0]
        F = Frame( ([[x1, y1, False], [x1, y1 + 40, False]], [[x2, y1, False], [x2, y1 + 40, False]], self[-1].page) )
        self.append(F)
        self._straighten()
        
    def __repr__(self):
        return ' |\n    '.join(repr(F) for F in self)

class Frames_wrapper(object):
    def __init__(self, outer, a, b):
        self._outer = outer
        self._a = a
        self._b = b
        
        self.space = outer.space
        self.start = outer.start
        self.save_u = outer.save_u
        self.restore_u = outer.restore_u
        self.read_u = outer.read_u
        self.at = outer.at
        self.freeze = outer.freeze
        self.unfreeze = outer.unfreeze

class Margined(Frames_wrapper):
    def fit(self, du):
        u, x1, x2, y, c, pn = self._outer.fit(du)
        return u, x1 + self._a, x2 - self._b, y, c, pn

class Subcell(Frames_wrapper):
    def fit(self, du):
        u, x1, x2, y, c, pn = self._outer.fit(du)
        width = x2 - x1
        return u, x1 + width*self._a, x1 + width*self._b, y, c, pn
