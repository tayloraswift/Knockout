from bisect import bisect

from itertools import chain

def accumulate_path(path):
    advance = 0
    for subpath in path:
        top = advance - subpath[0][1]
        advance += subpath[-1][1] - subpath[0][1]
        yield tuple((x, y + top) for x, y, a in subpath)

class Frame(list):
    def __init__(self, sides):
        list.__init__(self, sides[:-1])
        self.page = sides[-1]

    def __repr__(self):
        return ' ; '.join(chain((' '.join(str(x) + ',' + str(y) for x, y, a in side) for side in self), (str(self.page),)))

class Frames(list):
    def __init__(self, frames):
        list.__init__(self, (Frame(F) for F in frames))
        self.straighten()
    
    def straighten(self):
        left, right = zip( * self )
        
        self.run = tuple(accumulate_path(left)), tuple(accumulate_path(right))
        
        print(self.run)
    
    def __repr__(self):
        return ' |\n    '.join(repr(F) for F in self)
