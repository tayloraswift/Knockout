import bisect
from math import pi
from itertools import chain

from fonts.interfacefonts import ISTYLES

from interface.base import Base_kookie, accent, plus_sign, minus_sign, downchevron, upchevron, cross
from interface import menu

class Null(object):
    def is_over_hover(a, b):
        return False
    
    def is_over(a, b):
        return False

class Button(Base_kookie):
    def __init__(self, x, y, width, height, callback=None, string='', params=() ):
        Base_kookie.__init__(self, x, y, width, height, font=('strong',))
        
        self._callback = callback
        self._params = params
#        self._string = string
        
        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._add_static_text(x + width/2, self.y_bottom - self._height/2 + 5, string, align=0)
    
    def focus(self, x, y):
        self._active = 1
    
    def release(self, action=True):
        self._active = None
        if action:
            self._callback( * self._params)

    def hover(self, x, y):
        return 1

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        if self._active:
            cr.set_source_rgb( * accent)

            radius = 5
            y1, y2, x1, x2 = self._y, self.y_bottom, self._x, self._x_right
            cr.arc(x1 + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
            cr.arc(x2 - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
            cr.arc(x2 - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
            cr.arc(x1 + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
            cr.close_path()

            cr.fill()

            cr.set_source_rgb(1,1,1)
            
        elif hover[1]:
            cr.set_source_rgb( * accent)

        else:
            cr.set_source_rgb(0,0,0)
        cr.show_glyphs(self._texts[0])

class Tabs(Base_kookie):
    def __init__(self, x, y, cellwidth, height, default=0, callback=None, signals=() ):
        Base_kookie.__init__(self, x, y, cellwidth * len(signals), height, font=('strong',))
        self._signals, self._strings = zip( * signals )
        
        self._callback = callback
        
        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._active = default
        
        self._construct()

    def is_over(self, x, y):
        return self._y <= y <= self.y_bottom and abs(x - self._x) * 2 <= self._width
    
    def _construct(self):
        self._button_width = self._width/len(self._strings)
        self._x_left = []
        xo = self._x - self._width // 2
        for string in self._strings:
            self._add_static_text(xo + self._button_width/2, self.y_bottom - self._height/2 + 5, string, align=0)
            self._x_left.append(int(round(xo)))
            xo += self._button_width

    def _target(self, x):
        return bisect.bisect(self._x_left, x) - 1

    def focus(self, x, y):
        self._active = self._target(x)
        self._callback(self._signals[self._active])

    def hover(self, x, y):
        return self._target(x)

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        for i, button in enumerate(self._x_left):
            if i == self._active:
                cr.set_source_rgb( * accent)

                radius = 5
                y1, y2, x1, x2 = self._y, self.y_bottom, button, button + int(round(self._button_width))
                cr.arc(x1 + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
                cr.arc(x2 - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
                cr.arc(x2 - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
                cr.arc(x1 + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
                cr.close_path()

                cr.fill()

                cr.set_source_rgb(1,1,1)
                
            elif i == hover[1]:
                cr.set_source_rgb( * accent)

            else:
                cr.set_source_rgb(0,0,0)
            cr.show_glyphs(self._texts[i])

class Heading(Base_kookie):
    def __init__(self, x, y, width, height, get_text, font=('title',), fontsize=None, upper=False):
        Base_kookie.__init__(self, x, y, width, height, font=font)
        
        if fontsize is None:
            fontsize = self.font['fontsize']
        
        self._get_text = get_text
        self._fontsize = fontsize
        self._upper = upper
        self.read()
        
    def read(self):
        del self._texts[:]
        self._add_static_text(self._x, self._y + self._fontsize, self._get_text(), fontsize=self._fontsize, upper=self._upper)
    
    def is_over(self, x, y):
        return False
        
    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        cr.set_source_rgb(0,0,0)
        cr.rectangle(self._x, self.y_bottom - 2, self._width, 2)
        cr.fill()
        cr.show_glyphs(self._texts[0])

#############
class Selection_menu(Base_kookie):
    def __init__(self, x, y, width, height, menu_callback, options_acquire, value_acquire, params = (), before=lambda: None, after=lambda: None, source=0):
        Base_kookie.__init__(self, x, y, width, height, font=('strong',))
        
        self._get_value = value_acquire
        self._get_options = options_acquire
        self._params = params
        self._BEFORE = before
        self._AFTER = after

        self._menu_callback = menu_callback

        self._dropdown_active = False
        
        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._source = source
        
        self._SYNCHRONIZE()

    def _ACQUIRE_OPTIONS(self):
        self._menu_options = self._get_options()
        self._lookup_label = dict(self._menu_options)

    def _ACQUIRE_REPRESENT(self):
        label = self._lookup_label[self._get_value( * self._params)]
        self._texts = []
        self._add_static_text(self._x_right, self.y_bottom - self._height/2 + 5, label, align=-1)

    def _SYNCHRONIZE(self):
        self._ACQUIRE_OPTIONS()
        self._ACQUIRE_REPRESENT()
    
    def _MENU_PUSH(self, * args):
        self._menu_callback( * args)
        self._SYNCHRONIZE()
    
    def focus(self, x, y):
        menu.menu.create(self._x, self.y_bottom - 5, 200, self._menu_options, self._MENU_PUSH, self._params, before=self._BEFORE, after=self._AFTER, source=self._source )
        self._active = True
        self._dropdown_active = True
        print('DROPDOWN')

    def defocus(self):
        self._active = None
        self._dropdown_active = False

        return False

    def hover(self, x, y):
        return 1
    
    def draw(self, cr, hover=(None, None)):
        
        self._render_fonts(cr)
        
        if hover[1] == 1:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
            
        cr.show_glyphs(self._texts[0])
