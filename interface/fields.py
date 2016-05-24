from bisect import bisect
from math import pi, ceil, inf
from itertools import chain

from fonts.interfacefonts import ISTYLES

from edit.text import expand_cursors_word

from olivia import literal

from interface.base import accent, xhover, plus_sign, minus_sign, downchevron, upchevron, cross

z_colors = ((0.6, 0.6, 0.6), (0.7, 0.7, 0.7), accent, accent, (0.55, 0.55, 0.55))
z_hover_colors = ((0.4, 0.4, 0.4), (0.5, 0.5, 0.5), tuple(v + 0.2 for v in accent), tuple(v + 0.2 for v in accent), (0.35, 0.35, 0.35))

def _draw_Z(cr, x, y, h, k, hover, state):
        cr.rectangle(x, y, h, k)
        if hover:
            cr.set_source_rgb( * z_hover_colors[state] )
        else:
            cr.set_source_rgb( * z_colors[state] )
        
        if state <= 0:
            cr.rectangle(x + h - 2, y + 2, 4 - h, k - 4)
        
        if state == 2 or state == -1:
            cr.save()
            cr.clip()
            cr.move_to(x, y + 2.5)

            for i in range(5):
                
                cr.rel_line_to(h, -10)
                cr.rel_line_to(0, 3)
                cr.rel_line_to(-h, 10)
                cr.rel_move_to(0, 3)
            
            cr.fill()
            cr.restore()
            return
            
        cr.fill()

def _binary_Z(N, A):
    return A in N.attrs, ''

class Kookie(object):
    def __init__(self, x, y, width, height):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        
        self._active = None
        
        self._x_right = x + width
        self.y_bottom = y + height

    def _make_sd(self, subdivisions, cap):
        self._subdivisions, self._sdkeys = zip( * subdivisions)
        self._sdkeys += (cap,)
    
    def is_over(self, x, y):
        return self._y <= y <= self.y_bottom and self._x <= x <= self._x_right
    
    def is_over_hover(self, x, y):
        return False
    
    def focus(self, x, y):
        pass
    
    def dpress(self):
        pass
    
    def focus_drag(self, x, y):
        pass
    
    def release(self, action):
        pass
    
    def defocus(self):
        pass
    
    def hover(self, x, y):
        pass
    
    def type_box(self, name, char):
        pass
    
    def bounding_box(self):
        return self._x, self._x_right, self._y, self.y_bottom

class _Attribute(Kookie): # abstract base class
    def __init__(self, WI, x, y, width, node, A, Z, name, refresh, no_z):        
        self.is_over_hover = self.is_over
        
        self._node = node
        self._A = A
        self._read_Z = Z
        self._refresh = refresh
        
        self._name = name
        
        if no_z:
            self._z_div = -inf
            self._widget_x = x
            wwidth = width
        else:
            self._z_div = x + 15
            self._widget_x = x + 25
            wwidth = width - 25
        self._z = not no_z
        
        self._WIDGET = self.__class__.widgetclass(wwidth, * WI[0], ** WI[1])
        Kookie.__init__(self, x, y, width, self._WIDGET.k)
        self._exit = self.__class__.widgetclass.exit
        self._WActive = False
        
        self.read()
    
    def read(self):
        A = self._A
        self._status, bvalue = self._read_Z(self._node, A)
        if self._status > 0:
            value = self._node.attrs[A]
        else:
            TYPE, default = next((TYPE, default) for a, TYPE, * default in type(self._node).DNA if a == A)
            if TYPE in literal and self._read_Z is _binary_Z:
                value = self._node[A]
            elif default:
                value = default
            else:
                value = bvalue
        
        self._WIDGET.store(value)

    def _write(self, force=False):
        V, change = self._WIDGET.value()
        if change or force:
            self._node.assign(self._A, V)
            self._refresh()
            self.read()
    
    def _toggle_Z(self):
        if self._status > 0:
            self._node.deassign(self._A)
            self._refresh()
            self.read()
        else:
            self._write(force=True)

    def hover(self, x, y):
        if x < self._z_div:
            return 1, None
        else:
            return 0, self._WIDGET.hover(x - self._widget_x, y - self._y)

    def focus(self, x, y):
        if x < self._z_div:
            self._WActive = False
            self._toggle_Z()
            
        else:
            self._WActive = True
            self._WIDGET.focus(x - self._widget_x, y - self._y)
            if self._exit == 'f':
                self._write()
    
    def dpress(self):
        if self._WActive:
            self._WIDGET.dpress()
    
    def focus_drag(self, x, y):
        if self._WActive:
            return self._WIDGET.focus_drag(x - self._widget_x, y - self._y)
    
    def release(self, action):
        if self._WActive:
            self._WIDGET.release(action)
    
    def defocus(self):
        if self._WActive:
            self._WActive = False
            self._WIDGET.defocus()
            if self._exit == 'd':
                self._write()
    
    def type_box(self, name, char):
        if self._WActive:
            self._WIDGET.type_box(name, char)
    
    def draw(self, cr, hover=(None, None)):
        if hover[0] is not None:
            ZH, HH = hover[1]
        else:
            ZH = False
            HH = None
        
        if self._z:
            _draw_Z(cr, self._x, self._y + 10, 10, 22, ZH, self._status)
        
        cr.save()
        cr.translate(self._widget_x, self._y)
        self._WIDGET.draw(cr, HH)
        cr.restore()

class _Widget(object): # abstract
    def focus(self, x, y):
        pass
    
    def dpress(self):
        pass
    
    def focus_drag(self, x, y):
        pass
    
    def release(self, action):
        pass
    
    def defocus(self):
        pass
    
    def hover(self, x, y):
        pass
    
    def type_box(self, name, char):
        pass

def text(x, y, text, font, fontsize=None, align=1, sub_minus=False, upper=False):
    if upper:
        text = text.upper()
    if fontsize is None:
        fontsize = font['fontsize']
    xo = x
    line = []
    for character in text:
        if sub_minus and character == '-':
            character = '–'
        try:
            line.append((font['fontmetrics'].character_index(character), x, y))
            x += (font['fontmetrics'].advance_pixel_width(character)*fontsize + font['tracking'])
        except TypeError:
            line.append((-1, x, y))

    if align == 0:
        dx = (xo - x)/2
        line = [(g[0], g[1] + dx, g[2]) for g in line]
    elif align == -1:
        dx = xo - x
        line = [(g[0], g[1] + dx, g[2]) for g in line]
    
    return font['font'], font['fontsize'], line

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def set_fonts(cr, font, fontsize):
    cr.set_font_face(font)
    cr.set_font_size(fontsize)

def show_text(cr, textline):
    * F, T = textline
    set_fonts(cr, * F)
    cr.show_glyphs(T)

class CE(_Widget):
    exit = 'f'
    
    def __init__(self, width, cellsize, superset):
        min_cellwidth, self._cellheight = cellsize
        self._cellwidth = int(width / (width // min_cellwidth))
        self._per_row = int(width // self._cellwidth)
        
        self._superset = superset
        self.k = ceil(len(superset) / self._per_row) * self._cellheight

    def store(self, value):
        self._COUNT = value.copy()
        self._table = [(self._COUNT[V], str(self._COUNT[V]) + ' ' + V['name'], V) for V in self._superset]
        self._construct_table(margin = 2)
    
    def value(self):
        return self._COUNT, True
    
    def _construct_table(self, margin=0):
        cells = []
        x = 0
        y = 0
        ch = self._cellwidth
        ck = self._cellheight
        mp = ch/2
        font = ISTYLES[('strong',)]
        for row in chunks(self._table, self._per_row):
            cells.extend(((x + ch*i + margin, y + margin, ch - 2*margin, ck - 2*margin), 
                            text(x + ch*i + mp, y + 18, cell[1], font, align=0)) for i, cell in enumerate(row))
            y += ck
        self._cells = cells
    
    def hover(self, x, y):
        r = y // self._cellheight
        c = min(x // self._cellwidth, self._per_row - 1)
        i = int(r * self._per_row + c)
        
        if i >= len(self._table):
            i = None
            j = None
        else:
            a = x - c*self._cellwidth
            j = a * 2 > self._cellwidth
        
        return i, j
    
    def focus(self, x, y):
        i, j = self.hover(x, y)
        
        if i is not None:
            key = self._table[i][2]
            self._COUNT[key] += j*2 - 1
            if not self._COUNT[key]:
                del self._COUNT[key]
    
    def draw(self, cr, hover=None):
        if hover is not None:
            hover, Hside = hover
        
        set_fonts(cr, * self._cells[0][1][:2] )
        for i, ((cx, cy, ch, ck), textline) in enumerate(self._cells):
            count = self._table[i][0]
            if count: # nonzero count
                if count > 0:
                    R = range(count)
                    bg = accent
                else:
                    R = reversed(range(0, count, -1))
                    bg = (1, 0.3, 0.35)
                for c in R:
                    cr.set_source_rgba(1, 1, 1, 0.5)
                    cr.rectangle(cx + 2*c - 1, cy - 2*c + 1, ch, ck)
                    cr.fill()
                    cr.set_source_rgb( * bg )
                    cr.rectangle(cx + 2*c, cy - 2*c, ch, ck)
                    cr.fill()
                
                offset = max(0, (count - 1) * 2)
                
                cr.set_source_rgb(1, 1, 1)
                cr.show_glyphs((g[0], g[1] + offset, g[2] - offset) for g in textline[2])
                minus_sign(cr, cx - 2 + offset, cy - 1 - offset)
                plus_sign(cr, cx + ch - 24 + offset, cy - 1 - offset)
                
                cr.fill()
                continue
            
            elif hover == i:
                minus_sign(cr, cx - 2, cy)
                if Hside:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                else:
                    cr.set_source_rgb( * accent )
                cr.fill()

                plus_sign(cr, cx + ch - 24, cy)
                if Hside:
                    cr.set_source_rgb( * accent )
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                cr.fill()

                cr.set_source_rgb( * accent )
                cr.show_glyphs(textline[2])
            
            else:
                cr.set_source_rgba(0, 0, 0, 0.7)
                cr.show_glyphs(textline[2])

class Counter_editor(_Attribute):
    
    widgetclass = CE
    
    def __init__(self, x, y, width, cellsize, superset, node, A, Z=_binary_Z, name='', refresh=lambda: None, no_z=True):
        _Attribute.__init__(self, ((cellsize, superset), {}), x, y, width, node, A, Z, name, refresh, no_z)

class CB(_Widget):
    exit = 'f'
    
    def __init__(self, width, name):
        self.k = 36
        self._label = text(24, self.k - 10, name, ISTYLES[('label',)])

    def store(self, value):
        self._value = bool(value)
        self._state = self._value
    
    def value(self):
        return self._state, self._state != self._value
    
    def hover(self, x, y):        
        return True
    
    def focus(self, x, y):
        self._state = not self._state
    
    def draw(self, cr, hover=None):
        if hover is None:
            cr.set_source_rgba(0, 0, 0, 0.6)
        else:
            cr.set_source_rgb(0, 0, 0)
        
        show_text(cr, self._label)
        
        if self._state:
            cr.arc(10, self.k - 14, 6, 0, 2*pi)
            cr.fill()
        else:
            cr.set_line_width(1.5)
            cr.arc(10, self.k - 14, 5.25, 0, 2*pi)
            cr.stroke()

class Checkbox(_Attribute):
    
    widgetclass = CB
    
    def __init__(self, x, y, width, node, A, Z=_binary_Z, name='', refresh=lambda: None, no_z=False):        
        _Attribute.__init__(self, ((name,), {}), x, y, width, node, A, Z, name, refresh, no_z)

class BS(_Widget):
    exit = 'd'
    def __init__(self, width, name):
        self.k = 32
        
        self._set_text_bounds(width)
        self._label = text(self._text_left, 40, name, ISTYLES[('label',)], upper=True)
        
        # cursors
        self._active = False
        self._i = 0
        self._j = self._i
        
        self._resting_bar_color = (0, 0, 0, 0.4)
        self._active_bar_color = (0, 0, 0, 0.8)
        self._resting_text_color = (0, 0, 0, 0.6)
        self._active_text_color = (0, 0, 0, 1)
        
        self._scroll = 0

    def _set_text_bounds(self, width):
        self._text_left = 0
        self._text_right = width
        self._text_width = self._text_right - self._text_left
    
    ## Widget functions ##
    
    def _stamp_glyphs(self, glyphs):
        font = ISTYLES[()]
        self._contents = text(self._text_left, font['fontsize'] + 5, glyphs, font)
        self._template = self._contents[2]
    
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

    # target glyph index
    def _target(self, x):
        x -= self._scroll
        
        i = bisect([g[1] for g in self._template[:-1]], x)
        if i > 0 and x - self._template[i - 1][1] < self._template[i][1] - x:
            i -= 1
        return i
    
    def store(self, value):
        self._value = str(value)
        self._LIST = list(self._value) + [None]
        self._stamp_glyphs(self._LIST)
    
    def value(self):
        value = ''.join(self._LIST[:-1])
        return value, value != self._value
    
    def hover(self, x, y):        
        return True

    def dpress(self):
        if self._active:
            self._i, self._j = expand_cursors_word(self._LIST, self._i)
            self._j = min(self._j, len(self._LIST) - 1)

    def focus(self, x, y):
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
        self._active = False
        self._dropdown_active = False
        self._scroll = 0
    
    def draw(self, cr, hover=None):        
        if hover is None:
            resting_bar_color = self._resting_bar_color
        else:
            resting_bar_color = self._active_bar_color
        active_bar_color = self._active_bar_color
        resting_text_color = self._resting_text_color
        active_text_color = self._active_text_color

        
        fontsize = round(self._contents[1])
        
        if self._active:
            cr.set_source_rgba( * active_text_color )
        else:
            cr.set_source_rgba( * resting_text_color )
        
        cr.save()
        
        cr.rectangle(self._text_left - 1, 0, self._text_width + 2, self.k)
        cr.clip()
        cr.translate(round(self._scroll), 0)
        
        show_text(cr, ( * self._contents[:2], self._contents[2][:-1])) # don't print the cap glyph
        
        if self._active:
            # print cursors
            cr.set_source_rgb( * accent )
            cr.rectangle(round(self._template[self._i][1] - 1), 
                        5, 
                        2, 
                        fontsize)
            cr.rectangle(round(self._template[self._j][1] - 1), 
                        5, 
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
                        5,
                        abs(self._template[self._i][1] - self._template[self._j][1]),
                        fontsize)
                cr.fill()
        
        cr.restore()
        
        show_text(cr, self._label)
        
        if self._active:
            cr.set_source_rgba( * active_bar_color )
        else:
            cr.set_source_rgba( * resting_bar_color )
        cr.rectangle(self._text_left, fontsize + 10, self._text_width, 1)
        cr.fill()

class Blank_space(_Attribute):
    
    widgetclass = BS
    
    def __init__(self, x, y, width, node, A, Z=_binary_Z, name='', refresh=lambda: None, no_z=False):        
        _Attribute.__init__(self, ((name,), {}), x, y, width, node, A, Z, name, refresh, no_z)

"""
class New_object_menu(Base_kookie):
    hover = xhover
    def __init__(self, x, y, width, value_push, library, TYPE, before=lambda: None, after=lambda: None, name='', source=0):
        Base_kookie.__init__(self, x, y, width, 28, font=('strong',))
        self._BEFORE = before
        self._AFTER = after
        self._library = library
        self._value_push = value_push
        self._TYPE = TYPE

        self._dropdown_active = False
        self.is_over_hover = self.is_over
        
        self._source = source
        
        self._add_static_text(self._x + 40, self._y + self.font['fontsize'] + 5, 'NEW')
        
        self._SYNCHRONIZE()
        self._make_sd([(x + 30, 2)], 3)

    def _SYNCHRONIZE(self):
        # scan objects
        self._menu_options = tuple( (v, str(k)) for k, v in sorted(self._library.items()) )

    def focus(self, x, y):
        J = self.hover(x, y)

        if J == 3:
            FS = self._TYPE()
            self._library[FS.name] = FS
            self._value_push(self._library[FS.name])
        elif J == 2:
            menu.menu.create(self._x, self.y_bottom - 5, 200, self._menu_options, lambda *args: (self._BEFORE(), self._value_push(*args), self._AFTER()), (), source=self._source )
            self._active = True
            self._dropdown_active = True
            print('DROPDOWN')
        
        self._AFTER()
        
    def draw(self, cr, hover=(None, None)):
        cr.set_line_width(2)
        if self._dropdown_active:
            cr.set_source_rgb( * accent)
        elif hover[1] == 2:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        
        # v
        downchevron(cr, self._x + 3, self._y + 1)
        cr.stroke()

        # +
        if hover[1] == 3:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        plus_sign(cr, self._x_right - 26, self._y + 1)
        cr.fill()
        
        self._render_fonts(cr)
        cr.show_glyphs(self._texts[0])
        
class Object_menu(Blank_space):
    hover = xhover
    def __init__(self, x, y, width, read, value_push, library, before=lambda: None, after=lambda: None, name='', source=0):
        self._library = library
        self._value_push = value_push

        Blank_space.__init__(self, x, y, width, read=read, assign=lambda N: self._O.rename(N), before=before, after=after, name=name)

        self._dropdown_active = False
        self._source = source
        
        self._make_sd([(x + 30, 2), (x + width - 50, 1), (x + width - 26, 3)], 4)

    def _set_text_bounds(self):
        self._text_left = self._x + 30
        self._text_right = self._x_right - 50

    def _ACQUIRE_REPRESENT(self):
        # scan objects
        self._menu_options = tuple( (v, k) for k, v in sorted(self._library.items()) )
        
        self._O = self._read()

        self._VALUE = self._O.name
        self._LIST = list(self._VALUE) + [None]
        self._stamp_glyphs(self._LIST)

    def focus(self, x, y):
        J = self.hover(x, y)
        if J == 1:
            self._active = True
            self._dropdown_active = False
            self._i = self._target(x)
            self._j = self._i
            
            self._center_j()
        else:
            self.defocus()
            if J == 3:
                self._value_push(self._O.clone())
            elif J == 2:
                menu.menu.create(self._x, self.y_bottom - 5, 200, self._menu_options, lambda *args: (self._BEFORE(), self._value_push(*args), self._AFTER()), (),  source=self._source )
                self._active = True
                self._dropdown_active = True
                print('DROPDOWN')
                return
            elif J == 4:
                # unlink
                self._value_push(None)
            
            self._AFTER()
        
    def defocus(self):
        self._active = None
        self._dropdown_active = False
        self._scroll = 0
        # dump entry
        self._VALUE = self._entry()
        if self._VALUE != self._PREV_VALUE:
            self._BEFORE()
            self._assign(self._VALUE)
            self._AFTER()

        else:
            return False
        return True
        
    def _sup_draw(self, cr, hover=(None, None)):
        cr.set_line_width(2)
        if self._dropdown_active:
            cr.set_source_rgb( * accent)
        elif hover[1] == 2:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        
        # v
        downchevron(cr, self._x + 3, self._y + 1)
        cr.stroke()

        # +
        if hover[1] == 3:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        plus_sign(cr, self._subdivisions[1], self._y + 1)
        cr.fill()

        # x
        if hover[1] == 4:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        cross(cr, self._subdivisions[2], self._y + 1)
        cr.stroke()
"""
