import textbox
import constants
import text_t as comp

import bisect


class Properties_Panel(object):
    def __init__(self):
        self._h = constants.windowwidth
        body_fontpath = comp.fontclasses_a[()].path
        h1_fontpath = comp.fontclasses_b[()].path
        item1 = textbox.Blank_Space(list(h1_fontpath), constants.windowwidth - constants.propertieswidth + 30, 100)
        item2 = textbox.Blank_Space(list(body_fontpath), constants.windowwidth - constants.propertieswidth + 30, 200)
        
        self._items = [item1, item2]
    
    def resize(self, h, k):
        dx = h - self._h
        self._h = h
        for entry in self._items:
            entry.translate(dx)
    
    def render(self, cr):
        for entry in self._items:
            entry.draw(cr, active=True)
    
    def target(self, x, y):
        b = bisect.bisect([item.y for item in self._items], y)
        try:
            if self._items[b].y - y < 15:
                self._items[b].press(x)
        except IndexError:
            pass

panel = Properties_Panel()
