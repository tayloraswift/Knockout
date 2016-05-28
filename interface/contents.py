from bisect import bisect
from math import pi, ceil
from itertools import chain

from fonts.interfacefonts import ISTYLES

from interface.base import Kookie, accent, text, set_fonts, show_text, plus_sign, minus_sign, downchevron, upchevron, cross

def _null_copy(node, active):
    raise NotImplementedError

class Ordered(Kookie):
    def __init__(self, x, y, width, node, context, slot, display=lambda: None, copy=_null_copy, lcap=0):
        self._display = display
        
        self._itemheight = 26
        self._node = node
        self._content = node.content
        self._context = context
        self._slot = slot
        self._copy_element = copy
        
        self._LMAX = len(node.content) + lcap
        self._font = ISTYLES[('strong',)]
        Kookie.__init__(self, x, y, width, self._itemheight * (self._LMAX + 1))

        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self.read()
        
        x2 = x + width
        self._subdivisions = [x2 - 74, x2 - 50, x2 - 26]

    def _get_list(self):
        return self._content

    def read(self):
        self._fullcontent = self._get_list()
        self._labels = [text(self._x + 10, self._y + self._itemheight*i + 17, self._display(node), self._font) for i, node in enumerate(self._get_list())]
        
        active = getattr(self._context, self._slot)
        
        if self._fullcontent:
            if active in self._fullcontent:
                self._active = active
            else:
                self._active = self._fullcontent[0]
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
        O = self._copy_element(self._node, self._active)
        if self._active is not None:
            try:
                i = self._node.content.index(self._active) + 1
            except ValueError:
                i = 0
        else:
            i = 0
        self._node.content.insert(i, O)
        self._active = O

    def hover(self, x, y):
        y -= self._y
        i = int(y // self._itemheight)
        if i > self._LMAX:
            i = self._LMAX

        j = bisect(self._subdivisions, x) + 1
        return i, j
     
    def focus(self, x, y):
        F, C = self.hover(x, y)
        items = self._fullcontent
        
        if F == len(items):
            self._node.before()
            self._add()
            self._send(forceread=True)
            self._node.after('__addition__')
        else:
            if C == 1:
                self._active = items[F]
                self._send()
                return
            elif F < len(self._content):
                if C == 2:
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
                self._node.after(self._node)

    def _colored(self, value):
        return True
    
    def draw(self, cr, hover=(None, None)):
        if self._labels:
            set_fonts(cr, * self._labels[0][:2] )
        
        cr.set_source_rgba(0, 0, 0, 0.7)
        cr.set_line_width(2)
        
        y1 = self._y
        for i, (value, textline) in enumerate(zip(self._fullcontent, self._labels)):

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
                
            cr.show_glyphs(textline[2])
            y1 += self._itemheight

        if hover[1] is not None and hover[1][0] == self._LMAX:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        plus_sign(cr, self._x, y1)
        cr.fill()

class Para_control_panel(Ordered):
    def __init__(self, x, y, width, node, context, slot, display=lambda: None, copy=_null_copy):
        self._paragraph = context.bk
        Ordered.__init__(self, x, y, width, node, context, slot, display, copy, lcap=1)
        
    def read(self):
        if self._paragraph.implicit_ is None:
            self._present_tags = self._paragraph['class']
        else:
            self._present_tags = self._paragraph['class'] + self._paragraph.implicit_
        
        super().read()
        
    def _get_list(self):
        return self._content + [self._paragraph]

    def _colored(self, value):
        return value['class'] <= self._present_tags
