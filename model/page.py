class Page(object):
    def __init__(self, prop):
        self.WIDTH = prop['dimensions'][0]
        self.HEIGHT = prop['dimensions'][1]
        
        self._GAP = 100
        
        self._recalc()
        
        self.dual = prop['dual']
    
    def toggle_dual(self, dual):
        self.dual = dual
    
    def set_width(self, width):
        self.WIDTH = width
        self._recalc()
    
    def set_height(self, height):
        self.HEIGHT = height
        self._recalc()
    
    def _recalc(self):
        self._HALFGAP = int(self._GAP//2)
        self._WIDTH_HALFGAP = self.WIDTH + self._HALFGAP
        self._HEIGHT_HALFGAP = self.HEIGHT + self._HALFGAP
        
    def inside(self, x, y):
        if -self._HALFGAP <= y <= self._HEIGHT_HALFGAP and -self._HALFGAP <= x <= self._WIDTH_HALFGAP:
            return True
        else:
            return False
    
    def gutter_horizontal(self, x, y):
        if (-5 < x < self.WIDTH + 5) and (-20 <= y <= -10 or self.HEIGHT + 10 <= y <= self.HEIGHT + 20):
            return True
        else:
            return False

    def gutter_vertical(self, x, y):
        if (-5 < y < self.HEIGHT + 5) and (-20 <= x <= -10 or self.WIDTH + 10 <= x <= self.WIDTH + 20):
            return True
        else:
            return False
    
    def XY_to_page(self, x, y):
        if self.dual:
            E = int((y + self._HALFGAP) // self._HEIGHT_HALFGAP) * 2
            if x > self._WIDTH_HALFGAP:
                return E
            else:
                return E - 1
        else:
            return int((y + self._HALFGAP) // self._HEIGHT_HALFGAP)
    
    def normalize_XY(self, x, y, pp):
        if self.dual:
            y -= (pp + 1)//2 * self._HEIGHT_HALFGAP
            if pp % 2 == 0:
                x -= self._WIDTH_HALFGAP
            return x, y
        else:
            return x, y - pp * self._HEIGHT_HALFGAP
    
    def map_X(self, x, pp):
        if self.dual:
            return x + self._WIDTH_HALFGAP * ( not (pp % 2))
        else:
            return x

    def map_Y(self, y, pp):
        if self.dual:
            return y + (pp + 1)//2 * self._HEIGHT_HALFGAP
        else:
            return y + pp * self._HEIGHT_HALFGAP
