import bisect

from state import noticeboard

from model import meredith

class Sprinkles(object):
    def __init__(self):
        self._grid = meredith.mipsy.page_grid
        self.grid_selected = (None, None)
    
    def clear_selection(self):
        self.grid_selected = (None, None)

    def press(self, x, y):
        if -20 <= y <= -10 or 990 - 10 >= y >= 990 + 10:
            if self._target_grid('x', x):
                return True
            elif -5 < x < 765 + 5:
                self._add_grid('x', x)
                return True
            
        elif -20 <= x <= -10 or 765 - 10 >= x >= 765 + 10:
            if self._target_grid('y', y):
                return True
            elif -5 < y < 990 + 5:
                self._add_grid('y', y)
                return True
        return False

    def _add_grid(self, axis, value):
        if axis == 'x':
            a = 0
        elif axis == 'y':
            a = 1
        
        value = 10*int(round(value/10))
        
        i = bisect.bisect(self._grid[a], value)
        self._grid[a].insert(i, value)
        self.grid_selected = (a, i)
    
    def _target_grid(self, axis, value):
        if axis == 'x':
            a = 0
        elif axis == 'y':
            a = 1
            
        g_closest = bisect.bisect(self._grid[a], 10*int(round(value/10)) - 5)
        try:
            g = self._grid[a][g_closest]
        except IndexError:
            self.grid_selected = (None, None)
            return False
        
        if abs(value - g) < 5:
            self.grid_selected = (a, g_closest)
            return True
        else:
            self.grid_selected = (None, None)
            return False
    
    def move_grid(self, x, y):
        if self.grid_selected[0] == 0:
            if 0 < x < 765:
                value = x
            else:
                return False
        else:
            if 0 < y < 990:
                value = y
            else:
                return False

        value = 10*int(round(value/10))
        
        if value not in self._grid[self.grid_selected[0]]:
            self._grid[self.grid_selected[0]][self.grid_selected[1]] = value
            noticeboard.refresh.push_change()
    
    def release(self):
        if self.grid_selected[0] is not None:
            self._grid[self.grid_selected[0]].sort()
        
    def del_grid(self):
        try:
            del self._grid[self.grid_selected[0]][self.grid_selected[1]]
        except IndexError:
            print ('Error deleting grid')

    def render(self, cr, px, py, p_h, p_k, A):
        for n, notch in enumerate(self._grid[0]):
            if n == self.grid_selected[1] and self.grid_selected[0] == 0:
                cr.set_source_rgba(1, 0.2, 0.6, 0.7)
                width = 2
            else:
                cr.set_source_rgba(0, 0, 0, 0.2)
                width = 1
            cr.rectangle(px + int(round(notch*A)), py - int(round(18*A)), width, int(round(8*A)))
            cr.rectangle(px + int(round(notch*A)), py + int(round((p_k + 10)*A)), width, int(round(8*A)))
        
            cr.fill()

        for n, notch in enumerate(self._grid[1]):
            if n == self.grid_selected[1] and self.grid_selected[0] == 1:
                cr.set_source_rgba(1, 0.2, 0.6, 0.7)
                width = 2
            else:
                cr.set_source_rgba(0, 0, 0, 0.2)
                width = 1
            cr.rectangle(px - int(round(18*A)), py + int(round(notch*A)), int(round(8*A)), width)
            cr.rectangle(px + int(round((p_h + 10)*A)), py + int(round(notch*A)), int(round(8*A)), width)
        
            cr.fill()

sprinkles = Sprinkles()
