from fonts.interfacefonts import ISTYLES

from state import noticeboard, constants

from interface.base import Kookie, text, set_fonts, accent

class _Menu_widget(Kookie):
    def __init__(self, x, y, width, item_height, signals=None):

        # 'centers' menu
        height = item_height*len(signals)
        k = constants.window.get_k()
        if y > k/2:
            signals = tuple(reversed(signals))
            y -= height
            
        if y < 0:
            y = 0
        elif y + height > k:
            y = k - height

        Kookie.__init__(self, x, y, width, height)

        self._item_height = item_height
        self._signals = signals
        
        self._SF, self._labels = self._construct(ISTYLES[()])
        
    def _construct(self, font):
        # build menu
        x = self._x + 10
        y = self._y + font['fontsize'] + 5
        iht = self._item_height
        return (font['font'], font['fontsize']), [text(x, y + iht*i, signal[1], font) for i, signal in enumerate(self._signals)]
            
    def press(self, y):
        return self._signals[self.hover(y)]

    def hover(self, y):
        return int((y - self._y)//self._item_height)

    def draw(self, cr, hover=None):
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.rectangle(self._x, self._y, self._width, self._height)
        cr.fill()
        cr.set_source_rgba(1, 1, 1, 1)
        cr.rectangle(self._x + 1, self._y + 1, self._width - 2, self._height - 2)
        cr.fill()
        
        set_fonts(cr, * self._SF )
        for i, label in enumerate(self._labels):
            if i == hover:
                cr.set_source_rgb( * accent )
                cr.rectangle(self._x, self._y + i*self._item_height, self._width, self._item_height)
                cr.fill()
                cr.set_source_rgb(1, 1, 1)
            else:
                cr.set_source_rgb(0.1,0.1,0.1)
            cr.show_glyphs(label[2])

class Menu(object):
    def __init__(self):
        self._menu = None
        self._hovered = None
    
    def create(self, x, y, width, options, callback, inform=(), extend_life=False, source=0):

        self._dy = 0
        
        self._menu = _Menu_widget(int(round(x)) + constants.UI[source], int(round(y)), int(round(width)), 30, options)
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
