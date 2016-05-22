from bisect import bisect

from fonts.interfacefonts import ISTYLES

from edit.text import expand_cursors_word

from interface.base import Base_kookie, accent, xhover

z_colors = ((0.6, 0.6, 0.6), (0.7, 0.7, 0.7), accent, accent)
z_hover_colors = ((0.4, 0.4, 0.4), (0.5, 0.5, 0.5), tuple(v + 0.2 for v in accent), tuple(v + 0.2 for v in accent))

def _draw_Z(cr, x, y, h, k, hover, state):
        cr.rectangle(x, y, h, k)
        if hover:
            cr.set_source_rgb( * z_hover_colors[state] )
        else:
            cr.set_source_rgb( * z_colors[state] )
        
        if state:
            if state == 2:
                cr.save()
                cr.clip()
                cr.move_to(x, y)

                for i in range(6):
                    
                    cr.rel_line_to(h, -12)
                    cr.rel_line_to(0, 3.8)
                    cr.rel_line_to(-h, 12)
                    cr.rel_move_to(0, 2.8)
                
                cr.fill()
                cr.restore()
                return
        else:
            cr.rectangle(x + h - 2, y + 2, 4 - h, k - 4)
        cr.fill()

class Blank_space(Base_kookie):
    def __init__(self, x, y, width, node, A, Z=lambda N, A: (A in N.attrs, ''), name=''):        
        Base_kookie.__init__(self, x, y, width, 32)
        self.is_over_hover = self.is_over
        
        self._node = node
        self._A = A
        self._read_Z = Z
        
        self._name = name
        
        self._set_text_bounds()
        self._text_width = self._text_right - self._text_left
        
        self._read()
        
        # cursors
        self._i = len(self._LIST) - 1
        self._j = self._i
        
        # build static texts
        self._add_static_text(self._text_left, self._y + 40, self._name, font=ISTYLES[('label',)] , upper=True)
        
        self._resting_bar_color = (0, 0, 0, 0.4)
        self._active_bar_color = (0, 0, 0, 0.8)
        self._resting_text_color = (0, 0, 0, 0.6)
        self._active_text_color = (0, 0, 0, 1)
        
        self._scroll = 0
    
    def _set_text_bounds(self):
        self._text_left = self._x + 24
        self._text_right = self._x_right

    def _read(self):
        A = self._A
        self._status, bvalue = self._read_Z(self._node, A)
        if self._status:
            value = self._node.attrs[A]
        else:
            try:
                value = next(default[0] for a, TYPE, * default in type(self._node).DNA if a == A and default)
            except StopIteration:
                value = bvalue
        
        self._value = str(value)
        self._LIST = list(self._value) + [None]
        self._stamp_glyphs(self._LIST)
    
    def _write(self, force=False):
        value = ''.join(self._LIST[:-1])
        if value != self._value or force:
            self._node.assign(self._A, value)
            self._read()
    
    def _toggle_Z(self):
        if self._status:
            self._node.deassign(self._A)
            self._read()
        else:
            self._write(force=True)
    
    ## WIDGET FUNCTIONS ##
    
    def _stamp_glyphs(self, glyphs):
        self._template = self._build_line(self._text_left, self._y + self.font['fontsize'] + 5, glyphs, self.font)
        
    def is_over(self, x, y):
        return self._y <= y <= self.y_bottom and self._x - 10 <= x <= self._x_right + 10
    
    # scrolling function
    def _center_j(self):
        position = self._template[self._j][1] - self._text_left
        if position + self._scroll > self._text_width:
            self._scroll = -(position - self._text_width)
        elif position + self._scroll < 0:
            self._scroll = -(position)

    # typing
    def type_box(self, name, char):
        changed = False
        output = None
        
        if name in ['BackSpace', 'Delete']:
            # delete selection
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                del self._LIST[self._i : self._j]
                changed = True
                self._j = self._i
                
            elif name == 'BackSpace':
                if self._i > 0:
                    del self._LIST[self._i - 1]
                    changed = True
                    self._i -= 1
                    self._j -= 1
            else:
                if self._i < len(self._LIST) - 2:
                    del self._LIST[self._i]
                    changed = True

        elif name == 'Left':
            if self._i > 0:
                self._i -= 1
                self._j = self._i
        elif name == 'Right':
            if self._i < len(self._LIST) - 1:
                self._i += 1
                self._j = self._i
        elif name == 'Home':
            self._i = 0
            self._j = 0
        elif name == 'End':
            self._i = len(self._LIST) - 1
            self._j = len(self._LIST) - 1

        elif name == 'All':
            self._i = 0
            self._j = len(self._LIST) - 1
        
        elif name == 'Paste':
            # delete selection
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                del self._LIST[self._i : self._j]
                self._j = self._i
            # take note that char is a LIST now
            self._LIST[self._i:self._i] = char
            changed = True
            self._i += len(char)
            self._j = self._i
        
        elif name == 'Copy':
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                
                output = ''.join(self._LIST[self._i : self._j])
        
        elif name == 'Cut':
            # delete selection
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                output = ''.join(self._LIST[self._i : self._j])
                del self._LIST[self._i : self._j]
                changed = True
                self._j = self._i

        elif char is not None:
            # delete selection
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                del self._LIST[self._i : self._j]
                self._j = self._i
            self._LIST[self._i:self._i] = [char]
            changed = True
            self._i += 1
            self._j += 1
        
        if changed:
            self._stamp_glyphs(self._LIST)
        
        self._center_j()
        return output

    def dpress(self):
        if self._active:
            self._i, self._j = expand_cursors_word(self._LIST, self._i)
            self._j = min(self._j, len(self._LIST) - 1)
    
    # target glyph index
    def _target(self, x):
        x -= self._scroll
        
        i = bisect([g[1] for g in self._template[:-1]], x)
        if i > 0 and x - self._template[i - 1][1] < self._template[i][1] - x:
            i -= 1
        return i

    def focus(self, x, y):
        J = self.hover(x, y)
        if J == 1:
            self._active = True
            
            # clip to edges of visible text
            if x < self._text_left:
                self._i = self._target(self._text_left)
                # inch left or right
                if self._template[self._i][1] > self._text_left:
                    self._i -= 1
            elif x > self._text_right:
                self._i = self._target(self._text_right)
                if self._template[self._i][1] < self._text_right and self._i < len(self._template) - 1:
                    self._i += 1
            else:
                self._i = self._target(x)
            self._j = self._i
            
            self._center_j()
            
        elif J == 2:
            self._toggle_Z()

    def focus_drag(self, x, y):
        j = self._target(x)
        # force redraw if cursor moves
        if self._j != j:
            self._j = j
            self._center_j()
            return True
        else:
            return False

    def defocus(self):
        self._active = None
        self._dropdown_active = False
        self._scroll = 0
        
        self._write()

    def hover(self, x, y):
        return 1 + (x < self._text_left - 10)
    
    # drawing
    def _sup_draw(self, cr, hover):
        pass
    
    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        self._sup_draw(cr, hover=hover)
        
        if hover[0] is not None:
            zh = hover[1] - 1
            resting_bar_color = self._active_bar_color
        else:
            zh = False
            resting_bar_color = self._resting_bar_color
        active_bar_color = self._active_bar_color
        resting_text_color = self._resting_text_color
        active_text_color = self._active_text_color
        
        _draw_Z(cr, self._x, self._y + 6, 10, 22, zh, self._status)
        
        fontsize = round(self.font['fontsize'])
        
        if self._active:
            cr.set_source_rgba( * active_text_color )
        else:
            cr.set_source_rgba( * resting_text_color )
        
        cr.save()
        
        cr.rectangle(self._text_left - 1, self._y, self._text_width + 2, self._height)
        cr.clip()
        cr.translate(round(self._scroll), 0)
        
        # don't print the cap glyph
        cr.show_glyphs(self._template[:-1])
        
        if self._active:
            # print cursors
            cr.set_source_rgb( * accent )
            cr.rectangle(round(self._template[self._i][1] - 1), 
                        self._y + 5, 
                        2, 
                        fontsize)
            cr.rectangle(round(self._template[self._j][1] - 1), 
                        self._y + 5, 
                        2, 
                        fontsize)
            cr.fill()
            
            # print highlight
            if self._i != self._j:
                cr.set_source_rgba(0, 0, 0, 0.1)
                # find leftmost
                if self._i <= self._j:
                    root = self._template[self._i][1]
                else:
                    root = self._template[self._j][1]
                cr.rectangle(root, 
                        self._y + 5,
                        abs(self._template[self._i][1] - self._template[self._j][1]),
                        fontsize)
                cr.fill()
        
        cr.restore()
                
        if self._name is not None:
            cr.set_font_size(11)
            # print label
            for label in self._texts:
                cr.show_glyphs(label)
        
        if self._active:
            cr.set_source_rgba( * active_bar_color )
        else:
            cr.set_source_rgba( * resting_bar_color )
        cr.rectangle(self._text_left, self._y + fontsize + 10, self._text_width, 1)
        cr.fill()
