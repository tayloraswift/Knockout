import textbox
import constants
import text_t as comp

import bisect


class Properties_Panel(object):
    def __init__(self):
        self._h = constants.windowwidth
        
        self._items = []
        
        i = 0
        for key, item in comp.fontclasses_a.items():
            fontpath = item.path
            self._items.append(textbox.Blank_Space(list(fontpath), constants.windowwidth - constants.propertieswidth + 10, 100 + i*30, comp.the_box_submitted))
            i += 1
        
        self._active_box_i = None
    
    def resize(self, h, k):
        dx = h - self._h
        self._h = h
        for entry in self._items:
            entry.translate(dx)
    
    def render(self, cr):
        for entry in self._items:
            entry.draw(cr)
    
    def key_input(self, name, char):
        if name == 'Return':
            self._items[self._active_box_i].defocus()
            self._active_box_i = None
        else:
            return self._items[self._active_box_i].type_box(name, char)
    
    def press(self, x, y):
        b = None
        bb = bisect.bisect([item.y for item in self._items], y)
        try:
            if self._items[bb].y - y < 15:
                self._items[bb].focus(x)
                b = bb

        except IndexError:
            pass
        # defocus the other box, if applicable
        if b is None or b != self._active_box_i:
            if self._active_box_i is not None:
                self._items[self._active_box_i].defocus()
            self._active_box_i = b
    
    def press_motion(self, x):
        if self._active_box_i is not None:
            self._items[self._active_box_i].focus_drag(x)
    

panel = Properties_Panel()
