from bisect import bisect
from math import pi, ceil
from itertools import chain

from fonts.interfacefonts import ISTYLES

from interface.base import Base_kookie, accent, xhover, plus_sign, minus_sign, downchevron, upchevron, cross

class Ordered(Base_kookie):
    def __init__(self, x, y, width, node, context, slot, display=lambda: None, lcap=0):
        self._display = display
        
        self._itemheight = 26
        self._node = node
        self._content = node.content
        self._context = context
        self._slot = slot
        
        self._LMAX = len(node.content) + lcap
        Base_kookie.__init__(self, x, y, width, self._itemheight * (self._LMAX + 1), font=('strong',))

        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self.read()
        
        x2 = x + width
        self._make_sd([(x2 - 74, 1), (x2 - 50, 2), (x2 - 26, 3)], 4)

    def read(self):
        self._texts = []
        for i, node in enumerate(self._content):
            self._add_static_text(self._x + 10, self._y + self._itemheight*i + 17, self._display(node), align=1)
        active = getattr(self._context, self._slot)
        
        if self._content:
            if active in self._content:
                self._active = active
            else:
                self._active = self._content[0]
        else:
            self._active = None
        
        self._send()
    
    def _send(self, forceread=False):
        if self._active is not getattr(self._context, self._slot):
            self._context.push_active(self._slot, self._active)
            self.read()
            return
        if forceread:
            self.read()
    
    def _move(self, i, j):
        if 0 <= j < len(self._content):
            self._content.insert(j, self._content.pop(i))
            self._active = self._content[j]
    
    def _add(self):
        if self._LIBRARY.active is not None:
            O = self._LIBRARY.active.copy()
        else:
            O = self._LIBRARY.template.copy()
        try:
            i = self._LIBRARY.index(self._LIBRARY.active) + 1
        except ValueError:
            i = 0
        self._LIBRARY.insert(i, O)
        self._LIBRARY.active = O

    def hover(self, x, y):
        y -= self._y
        i = int(y // self._itemheight)
        if i > self._LMAX:
            i = self._LMAX

        j = self._sdkeys[bisect(self._subdivisions, x)]
        return i, j
     
    def focus(self, x, y):
        F, C = self.hover(x, y)

        if F == len(self._content):
            self._BEFORE()
            self._add()
            self._SYNCHRONIZE()
            self._AFTER()
        else:
            if C == 1:
                self._active = self._content[F]
                self._send()
                return

            elif C == 2:
                self._node.before()
                self._move(F, F - 1)
                self._send(forceread=True)

            elif C == 3:
                self._node.before()
                self._move(F, F + 1)
                self._send(forceread=True)

            elif C == 4:
                self._node.before()
                O = self._content[F]
                del self._content[F]
                if O is self._active:
                    self._active = None
                self._send(forceread=True)
            self._node.after()

    def _colored(self, value):
        return True
    
    def _list(self):
        return enumerate(self._content)
    
    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        cr.set_source_rgba(0, 0, 0, 0.7)
        cr.set_line_width(2)
        
        y1 = self._y
        for i, value in self._list():

            if value is self._active:
                radius = 5

                y2 = y1 + self._itemheight
                cr.move_to(self._x, y1 + radius)
                cr.arc(self._x + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
                cr.arc(self._x_right - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
                cr.arc(self._x_right - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
                cr.arc(self._x + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
                cr.close_path()
                
                if self._colored(value):
                    cr.set_source_rgb( * accent)
                    cr.fill()
                else:
                    cr.set_source_rgb(0.7, 0.7, 0.7)
                    cr.fill()

                cr.set_source_rgb(1, 1, 1)
                
                upchevron(cr, self._subdivisions[0], y1)
                cr.stroke()
                
                downchevron(cr, self._subdivisions[1], y1)
                cr.stroke()

                cross(cr, self._subdivisions[2], y1)
                cr.stroke()

                cr.set_source_rgb(1, 1, 1)

            elif hover[1] is not None and hover[1][0] == i:
                if hover[1][1] == 2:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                upchevron(cr, self._subdivisions[0], y1)
                cr.stroke()

                if hover[1][1] == 3:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                downchevron(cr, self._subdivisions[1], y1)
                cr.stroke()

                if hover[1][1] == 4:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                cross(cr, self._subdivisions[2], y1)
                cr.stroke()
                
                if self._colored(value):
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.4)

            elif self._colored(value):
                cr.set_source_rgba(0, 0, 0, 0.7)

            else:
                cr.set_source_rgba(0, 0, 0, 0.4)
                
            cr.show_glyphs(self._texts[i])
            y1 += self._itemheight

        if hover[1] is not None and hover[1][0] == self._LMAX:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        plus_sign(cr, self._x, y1)
        cr.fill()

class Para_control_panel(Ordered):
    def __init__(self, x, y, width, paragraph, library, display=lambda: None, before=lambda: None, after=lambda: None, refresh=lambda: None):
        self._paragraph = paragraph
        Ordered.__init__(self, x, y, width, library=library, display=display, before=before, after=after, refresh=refresh, lcap=1)
        
    def _ACQUIRE_REPRESENT(self):
        self._texts = []
        if self._paragraph.I_ is not None:
            self._present_tags = self._paragraph.P + self._paragraph.I_
        else:
            self._present_tags = self._paragraph.P
        for i, l in enumerate(chain((self._display(L) for L in self._LIBRARY), ['ELEMENT'])):
            self._add_static_text(self._x + 15, self._y + self._itemheight*i + 17, l, align=1)

    def _colored(self, value):
        return value.tags <= self._present_tags

    def _list(self):
        return enumerate(chain(self._LIBRARY, [self._paragraph.EP]))
    
    def focus(self, x, y):
        F, C = self.hover(x, y)
        items = self._LIBRARY + [self._paragraph.EP]

        if F == len(items):
            self._BEFORE()
            self._add()
            self._SYNCHRONIZE()
            self._AFTER()
        else:
            if C == 1:
                self._LIBRARY.active = items[F]
                self._REFRESH()
                return C

            elif F < len(items) - 1:
                if C == 2:
                    self._BEFORE()
                    self._move(F, F - 1)

                elif C == 3:
                    self._BEFORE()
                    self._move(F, F + 1)

                elif C == 4:
                    self._BEFORE()
                    del self._LIBRARY[F]
            
            self._SYNCHRONIZE()
            self._AFTER()
            return C

