class Page(object):
    def __init__(self, width, height, gap):
        self.WIDTH = width
        self.HEIGHT = height
        self._GAP = gap
        
        self._dual = False
    
    def inside_x(self, x):
        if self._GAP/2 <= x <= self.WIDTH + self._GAP/2:
            return True
        else:
            return False

    def inside_y(self, y):
        if self._GAP/2 <= y <= self.HEIGHT + self._GAP/2:
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
    
    def Y_to_page(self, y):
        return int((y + self._GAP/2) // (self.HEIGHT + self._GAP/2))
    
    def normalize_Y(self, y, pp):
        return y - pp * (self.HEIGHT + self._GAP/2)

page = Page(765, 990, 200)
