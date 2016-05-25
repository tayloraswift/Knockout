from state import noticeboard, constants
from interface import base

class Menu(object):
    def __init__(self):
        self._menu = None
        self._hovered = None
    
    def create(self, x, y, width, options, callback, inform=(), extend_life=False, source=0):

        self._dy = 0
        
        self._menu = base.Menu(int(round(x)) + constants.UI[source], int(round(y)), int(round(width)), 30, options)
        self._callback = callback
        self._inform = inform
        
        self._extend = extend_life
        
        self.test_change()
        
    def destroy(self):
        self._menu = None
        self._hovered = None
    
    def menu(self):
        if self._menu is not None:
            return True
        else:
            return False
    
    def in_bounds(self, x, y):
        if self._menu.is_over(x, y - self._dy):
            return True
        else:
            self._clear_hover()
            return False
    
    # do we need x?
    def press(self, y):
        O, label = self._menu.press(y - self._dy)
        if self._extend:
            self._callback(O, label)
            self._extend = False
        else:
            self._callback(O, label)
            self.destroy()
        for F in self._inform:
            F()
    
    def hover(self, y):
        self._hovered = self._menu.hover(y - self._dy)
    
    def scroll(self, direction):
        if direction:
            self._dy -= 22
        else:
            self._dy += 22
        noticeboard.redraw_overlay.push_change()
    
    def test_change(self, hist=[None]):
        if self._hovered != hist[0]:
            noticeboard.redraw_overlay.push_change()
            hist[0] = self._hovered
    
    def _clear_hover(self):
        self._hovered = None
        self.test_change()
    
    def render(self, cr):
        if self._menu is not None:
            cr.save()
            cr.translate(0, self._dy)
            self._menu.draw(cr, self._hovered)
            cr.restore()

menu = Menu()
