from state import noticeboard

from interface import base

class Menu(object):
    def __init__(self):
        self._menu = None
        self._hovered = None
    
    def create(self, x, y, width, options, callback, callback_parameters):
        self._menu = base.Menu(int(round(x)), int(round(y)), int(round(width)), 30, options)
        self._callback = callback
        self._callback_parameters = callback_parameters
        
    def destroy(self):
        self._menu = None
        self._hovered = None
    
    def menu(self):
        if self._menu is not None:
            return True
        else:
            return False
    
    def in_bounds(self, x, y):

        if self._menu.is_over(x, y):
            return True
        else:
            self._clear_hover()
            return False
    
    # do we need x?
    def press(self, y):
        name = self._menu.press(y)
        self._callback(name, * self._callback_parameters)
        self.destroy()
    
    def hover(self, y):
        self._hovered = self._menu.hover(y)
    
    def test_change(self, hist=[None]):
        if self._hovered != hist[0]:
            noticeboard.refresh.push_change()
            hist[0] = self._hovered
    
    def _clear_hover(self):
        self._hovered = None
    
    def render(self, cr):
        if self._menu is not None:
            self._menu.draw(cr, self._hovered)

menu = Menu()
