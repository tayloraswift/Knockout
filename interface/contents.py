from bisect import bisect
from math import pi, ceil
from itertools import chain

from fonts.interfacefonts import ISTYLES

from state.constants import accent

from interface.base import Kookie, text, set_fonts, show_text, plus_sign, minus_sign, downchevron, upchevron, cross

class Ordered(Kookie):
    def __init__(self, x, y, width, node, context, slot, display=lambda: None, lcap=0):
        self._display = display
        
        self._itemheight = 26
        self._node = node
        self._content = node.content
        self._context = context
        self._slot = slot
        
        self._LMAX = len(node.content) + lcap
        self._fonts = ISTYLES[('strong',)], ISTYLES[('emphasis',)]
        Kookie.__init__(self, x, y, width, self._itemheight * (self._LMAX + 1))

        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        x2 = x + width
        self._subdivisions = [x2 - 74, x2 - 50, x2 - 26]
        
        self.read()

    def _get_list(self):
        return self._content

    def _multi_label(self, x1, x2, y, subtexts):
        if type(subtexts) is str:
            return text(x1, y, subtexts, self._fonts[0]),
        elif len(subtexts) < 2 or not subtexts[1]:
            return text(x1, y, subtexts[0], self._fonts[0]),
        else:
            T1 = text(x1, y, subtexts[0], self._fonts[0])
            T2 = text(x2, y, subtexts[1], self._fonts[1], align=-1, left=x1 + T1[3] + 10)
            return T1, T2
    
    def read(self):
        self._fullcontent = self._get_list()
        self._labels = [self._multi_label(self._x + 10, self._subdivisions[0] - 10, self._y + self._itemheight*i + 17, 
                                          self._display(node)) for i, node in enumerate(self._get_list())]
        
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
        if self._active is not None:
            try:
                i = self._node.content.index(self._active) + 1
            except ValueError:
                i = 0
        else:
            i = 0
        self._active = self._node.content_new(self._active, i)

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
        cr.set_line_width(2)
        
        y1 = self._y
        for i, (value, textlines) in enumerate(zip(self._fullcontent, self._labels)):
            if value is self._active:
                radius = 5
                halfpi = pi*0.5
                y2 = y1 + self._itemheight
                cr.move_to(self._x           , y1 + radius)
                cr.arc(self._x       + radius, y1 + radius, radius, pi      , 3*halfpi)
                cr.arc(self._x_right - radius, y1 + radius, radius, 3*halfpi, 2*pi    )
                cr.arc(self._x_right - radius, y2 - radius, radius, 0       , halfpi  )
                cr.arc(self._x       + radius, y2 - radius, radius, halfpi  , pi      )
                cr.close_path()
                
                if self._colored(value):
                    cr.set_source_rgb( * accent )
                else:
                    cr.set_source_rgb(0.7, 0.7, 0.7)
                cr.fill()

                cr.set_source_rgb(1, 1, 1)
                upchevron(cr, self._subdivisions[0], y1)
                downchevron(cr, self._subdivisions[1], y1)
                cross(cr, self._subdivisions[2], y1)
                cr.stroke()

            elif hover[1] is not None and hover[1][0] == i:
                colors = [(0.3, 0.3, 0.3)] * 3
                if hover[1][1] > 1:
                    colors[hover[1][1] - 2] = accent
                
                cr.set_source_rgba( * colors[0] )
                upchevron(cr, self._subdivisions[0], y1)
                cr.stroke()

                cr.set_source_rgba( * colors[1] )
                downchevron(cr, self._subdivisions[1], y1)
                cr.stroke()

                cr.set_source_rgba( * colors[2] )
                cross(cr, self._subdivisions[2], y1)
                cr.stroke()
                
                if self._colored(value):
                    cr.set_source_rgba( * accent )
                else:
                    cr.set_source_rgb(0.6, 0.6, 0.6)

            elif self._colored(value):
                cr.set_source_rgb(0.3, 0.3, 0.3)

            else:
                cr.set_source_rgb(0.6, 0.6, 0.6)
            
            for textline in textlines:
                show_text(cr, textline)
            y1 += self._itemheight

        if hover[1] is not None and hover[1][0] == self._LMAX:
            cr.set_source_rgb( * accent )
        else:
            cr.set_source_rgb(0.3, 0.3, 0.3)
        plus_sign(cr, self._x, y1)
        cr.fill()

class Para_control_panel(Ordered):
    def __init__(self, x, y, width, node, context, slot, display=lambda: None):
        self._paragraph = context.bk
        Ordered.__init__(self, x, y, width, node, context, slot, display, lcap=1)
        
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
