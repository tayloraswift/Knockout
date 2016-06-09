from bisect import bisect
from math import pi

from fonts.interfacefonts import ISTYLES

from state.constants import accent

from interface.base import Kookie, text, show_text

class Null(object):
    def is_over_hover(a, b):
        return False
    
    def is_over(a, b):
        return False

class Button(Kookie):
    def __init__(self, x, y, width, height, callback=None, name=''):
        Kookie.__init__(self, x, y, width, height)
        self._callback = callback
        
        self.is_over_hover = self.is_over
        
        self._label = text(x + width/2, self.y_bottom - self._height/2 + 5, name, ISTYLES[('strong',)], align=0)
    
    def focus(self, x, y):
        self._active = 1
    
    def release(self, action=True):
        self._active = None
        if action:
            self._callback()

    def hover(self, x, y):
        return 1

    def draw(self, cr, hover=(None, None)):
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
        show_text(cr, self._label)

class Tabs(Kookie):
    def __init__(self, x, y, cellwidth, height, default=0, callback=None, signals=() ):
        Kookie.__init__(self, x, y, cellwidth * len(signals), height)
        self._signals = signals
        self._callback = callback
        
        self.is_over_hover = self.is_over
        
        self._active = default
        
        self._buttons = self._construct(ISTYLES[('strong',)], signals)
        self._xx = [k[0] for k in self._buttons]

    def is_over(self, x, y):
        return self._y <= y <= self.y_bottom and abs(x - self._x) * 2 <= self._width
    
    def _construct(self, font, signals):
        self._button_width = self._width/len(signals)
        x0 = self._x - self._width // 2
        buttons = []
        for signal in signals:
            buttons.append((int(round(x0)), text(x0 + self._button_width/2, self.y_bottom - self._height/2 + 5, signal[1], font, align=0)))
            x0 += self._button_width
        return buttons

    def focus(self, x, y):
        self._active = self.hover(x, y)
        self._callback(self._signals[self._active][0])

    def hover(self, x, y):
        return bisect(self._xx, x) - 1

    def draw(self, cr, hover=(None, None)):
        for i, (x, label) in enumerate(self._buttons):
            if i == self._active:
                cr.set_source_rgb( * accent)

                radius = 5
                y1, y2, x1, x2 = self._y, self.y_bottom, x, x + int(round(self._button_width))
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
            show_text(cr, label)

class Tabs_round(Tabs):
    def __init__(self, x, y, cellwidth, height, default, callback=None, signals=(), longstrings=None):
        Tabs.__init__(self, x, y, cellwidth, height, default, callback, signals)
        
        font = ISTYLES[('strong',)]
        self._state_labels = [text(x, self.y_bottom + 20, label, font, align=0) for label in longstrings]
        
    def draw(self, cr, hover=(None, None)):
        for i, (x, label) in enumerate(self._buttons):

            if i == hover[1] or i == self._active:
                ink = accent
            else:
                ink = (0, 0, 0)
            
            cr.set_source_rgba( * ink )

            radius = self._height/2
            cx, cy = x + int(round(self._button_width/2)), (self._y + self.y_bottom)//2
            cr.arc(cx, cy, radius, 0, 2*pi)
            cr.close_path()
            cr.fill()
            
            cr.set_source_rgb(1, 1, 1)
            if i != self._active:
                cr.arc(cx, cy, radius - 1.5, 0, 2*pi)
                cr.close_path()
                cr.fill()
                
                cr.set_source_rgba( * ink )
            
            show_text(cr, label)

        cr.set_source_rgb(1, 1, 1)
        radius = 10
        state_label = self._state_labels[self._active]
        width = state_label[2][-1][1] - state_label[2][0][1] + 20
        y1, y2, x1, x2 = self.y_bottom + 5, self.y_bottom + 25, self._x - width//2, self._x + width//2
        cr.arc(x1 + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
        cr.arc(x2 - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
        cr.arc(x2 - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
        cr.arc(x1 + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
        cr.close_path()
        cr.fill()
                
        cr.set_source_rgb(0, 0, 0)
        show_text(cr, state_label)

class Heading(Kookie):
    def __init__(self, x, y, width, height, get_text, font=('title',), fontsize=None, upper=False):
        Kookie.__init__(self, x, y, width, height)
        
        font = ISTYLES[font]
        self._typeset_text = lambda: text(x, y + fontsize, get_text(), font, fontsize=fontsize, upper=upper)
        self.read()
        
    def read(self):
        self._heading = self._typeset_text()
    
    def is_over(self, x, y):
        return False
        
    def draw(self, cr, hover=(None, None)):
        cr.set_source_rgb(0,0,0)
        cr.rectangle(self._x, self.y_bottom - 2, self._width, 2)
        cr.fill()
        show_text(cr, self._heading)
