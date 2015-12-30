import bisect

from state import noticeboard

from model import meredith, penclick

accent = (1, 0.22, 0.55)

class Sprinkles(object):
    def __init__(self):
        self._grid = meredith.mipsy.page_grid
        self.grid_selected = (None, None)
    
    def clear_selection(self):
        self.grid_selected = (None, None)

    def press(self, x, y):
        print(y)
        if penclick.page.gutter_horizontal(x, y):
            if not self._target_grid('x', x):
                self._add_grid('x', x)
            return True
            
        elif penclick.page.gutter_vertical(x, y):
            if not self._target_grid('y', y):
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
        if self.grid_selected[0] is not None:
            if self.grid_selected[0] == 0:
                if 0 < x < penclick.page.WIDTH:
                    value = x
                else:
                    return False
            else:
                if 0 < y < penclick.page.HEIGHT:
                    value = y
                else:
                    return False

            value = 10*int(round(value/10))
            
            if value not in self._grid[self.grid_selected[0]]:
                self._grid[self.grid_selected[0]][self.grid_selected[1]] = value
                noticeboard.redraw_becky.push_change()
    
    def release(self):
        if self.grid_selected[0] is not None:
            GL = self._grid[self.grid_selected[0]].pop(self.grid_selected[1])
            self.grid_selected = (self.grid_selected[0], bisect.bisect(self._grid[self.grid_selected[0]], GL))
            self._grid[self.grid_selected[0]].insert(self.grid_selected[1], GL)
        
    def del_grid(self):
        try:
            del self._grid[self.grid_selected[0]][self.grid_selected[1]]
            self.grid_selected = (None, None)
        except IndexError:
            print ('Error deleting grid')

    def render(self, cr, px, py, p_h, p_k, A):
        for n, notch in enumerate(self._grid[0]):
            if n == self.grid_selected[1] and self.grid_selected[0] == 0:
                cr.set_source_rgba( * accent, 0.7)
                cr.move_to(px + int(round(notch*A)), py - int(round(10*A)))
                cr.rel_line_to(1, 0)
                cr.rel_line_to(1, -int(round(8*A)))
                cr.rel_line_to(-3, 0)
                cr.close_path()
                
                cr.move_to(px + int(round(notch*A)), py + int(round((p_k + 10)*A)))
                cr.rel_line_to(1, 0)
                cr.rel_line_to(1, int(round(8*A)))
                cr.rel_line_to(-3, 0)
                cr.close_path()
            else:
                cr.set_source_rgba(0, 0, 0, 0.2)
                cr.rectangle(px + int(round(notch*A)), py - int(round(18*A)), 1, int(round(8*A)))
                cr.rectangle(px + int(round(notch*A)), py + int(round((p_k + 10)*A)), 1, int(round(8*A)))
        
            cr.fill()
            
            cr.set_line_width(1)
#            cr.set_dash([2, 8], 0)
            cr.move_to(px + int(round(notch*A)) + 0.5, py)
            cr.rel_line_to(0, p_k*A)
            
            cr.stroke()

        for n, notch in enumerate(self._grid[1]):
            if n == self.grid_selected[1] and self.grid_selected[0] == 1:
                cr.set_source_rgba( * accent, 0.7)
                cr.move_to(px - int(round(10*A)), py + int(round(notch*A)))
                cr.rel_line_to(0, 1)
                cr.rel_line_to(-int(round(8*A)), 1)
                cr.rel_line_to(0, -3)
                cr.close_path()
                
                cr.move_to(px + int(round((p_h + 10)*A)), py + int(round(notch*A)))
                cr.rel_line_to(0, 1)
                cr.rel_line_to(int(round(8*A)), 1)
                cr.rel_line_to(0, -3)
                cr.close_path()
            else:
                cr.set_source_rgba(0, 0, 0, 0.2)
                cr.rectangle(px - int(round(18*A)), py + int(round(notch*A)), int(round(8*A)), 1)
                cr.rectangle(px + int(round((p_h + 10)*A)), py + int(round(notch*A)), int(round(8*A)), 1)
        
            cr.fill()

            cr.set_line_width(1)
#            cr.set_dash([2, 8], 0)
            cr.move_to(px, py + int(round(notch*A)) + 0.5)
            cr.rel_line_to(p_h*A, 0)
            
            cr.stroke()
