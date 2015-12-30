import bisect
from copy import deepcopy
from math import pi

from fonts import styles
from fonts import paperairplanes as plane

from interface.base import Base_kookie, accent
from interface import menu



class Button(Base_kookie):
    def __init__(self, x, y, width, height, callback=None, string='', params=() ):
        Base_kookie.__init__(self, x, y, width, height, font=styles.FONTSTYLES['_interface:STRONG'])
        
        self._callback = callback
        self._params = params
#        self._string = string
        
        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._add_static_text(x + width/2, self._y_bottom - self._height/2 + 5, string, align=0)
    
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
            y1, y2, x1, x2 = self._y, self._y_bottom, self._x, self._x_right
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

class Checkbox(Base_kookie):
    def __init__(self, x, y, width, callback, params = (), value_acquire=None, before=lambda: None, after=lambda: None, name=''):
        Base_kookie.__init__(self, x, y, width, 20, font=styles.FONTSTYLES['_interface:LABEL'])

        self._BEFORE = before
        self._AFTER = after
        self._callback = callback
        self._params = params
        self._value_acquire = value_acquire
        self._ACQUIRE_REPRESENT()
        self._SYNCHRONIZE = self._ACQUIRE_REPRESENT

        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._add_static_text(self._x + 20, self._y_bottom - 5, name, align=1)

    def _ACQUIRE_REPRESENT(self):
        self._STATE = self._value_acquire( * self._params)

    def focus(self, x, y):
        self._BEFORE()
        self._callback(not self._STATE, * self._params)
        self._ACQUIRE_REPRESENT()
        self._AFTER()

    def hover(self, x, y):
        return 1

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
            
        if hover[1]:
            cr.set_source_rgb(0,0,0)
            cr.show_glyphs(self._texts[0])

        else:
            cr.set_source_rgba(0,0,0, 0.6)
            cr.show_glyphs(self._texts[0])

        cr.arc(self._x + 6, self._y_bottom - 9, 6, 0, 2*pi)
        cr.fill()
        if not self._STATE:
            cr.set_source_rgb(1, 1, 1)
            cr.arc(self._x + 6, self._y_bottom - 9, 4.5, 0, 2*pi)
            cr.fill()


class Tabs(Base_kookie):
    def __init__(self, x, y, width, height, default=0, callback=None, signals=() ):
        Base_kookie.__init__(self, x, y, width, height, font=styles.FONTSTYLES['_interface:STRONG'])
        self._signals, self._strings = zip( * signals )
        
        self._callback = callback
        
        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._active = default
        
        self._construct()
    
    def _construct(self):
        self._button_width = self._width/len(self._strings)
        self._x_left = []
        xo = self._x
        for string in self._strings:
            self._add_static_text(xo + self._button_width/2, self._y_bottom - self._height/2 + 5, string, align=0)
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
                y1, y2, x1, x2 = self._y, self._y_bottom, button, button + int(round(self._button_width))
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
    def __init__(self, x, y, width, height, text, font=styles.FONTSTYLES['_interface:TITLE'], fontsize=None, upper=False):
        Base_kookie.__init__(self, x, y, width, height)
        
        self.font = font
        if fontsize is None:
            fontsize = self.font.u_fontsize
        
        self._add_static_text(self._x, self._y + fontsize, text, fontsize=fontsize, upper=upper)
    
    def is_over(self, x, y):
        return False
        
    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        cr.set_source_rgb(0,0,0)
        cr.rectangle(self._x, self._y_bottom - 2, self._width, 2)
        cr.fill()
        cr.show_glyphs(self._texts[0])


class Blank_space(Base_kookie):
    def __init__(self, x, y, width, callback, value_acquire, params = (), before=lambda: None, after=lambda: None, name=''):
        self.broken = False
        self._params = params
        self._BEFORE = before
        self._AFTER = after
        
        Base_kookie.__init__(self, x, y, width, 28)

        self._callback = callback
        self._value_acquire = value_acquire
        
        self._set_text_bounds()
        self._text_width = self._text_right - self._text_left
        
        self._SYNCHRONIZE()

        self._domain = lambda k: k
        self._name = name
        
        self.is_over_hover = self.is_over
        
        # cursors
        self._i = len(self._LIST) - 1
        self._j = self._i
        
        # build static texts
        self._add_static_text(self._x, self._y + 40, self._name, font=styles.FONTSTYLES['_interface:LABEL'] , upper=True)
        
        self._resting_bar_color = (0, 0, 0, 0.4)
        self._active_bar_color = (0, 0, 0, 0.8)
        self._resting_text_color = (0, 0, 0, 0.6)
        self._active_text_color = (0, 0, 0, 1)
        
        self._broken_resting_bar_color = (1, 0.15, 0.2, 0.8)
        self._broken_active_bar_color = (1, 0.15, 0.2, 1)
        self._broken_resting_text_color = (1, 0.15, 0.2, 0.8)
        self._broken_active_text_color = (1, 0.15, 0.2, 1)
        
        self._scroll = 0
    
    def _set_text_bounds(self):
        self._text_left = self._x
        self._text_right = self._x_right

    def _ACQUIRE_REPRESENT(self):
        self._VALUE = self._value_acquire( * self._params)
        self._LIST = list(self._VALUE) + [None]
        self._stamp_glyphs(self._LIST)

    def _SYNCHRONIZE(self):
        self._ACQUIRE_REPRESENT()
        self._PREV_VALUE = self._VALUE

    def _stamp_glyphs(self, glyphs):
        self._template = self._build_line(self._text_left, self._y + self.font.u_fontsize + 5, glyphs, self.font)
        
    def is_over(self, x, y):
        return self._y <= y <= self._y_bottom and self._x - 10 <= x <= self._x_right + 10

    def _entry(self):
        return ''.join(self._LIST[:-1])
    
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
        
        elif name == 'Paste':
            # check to make sure string contains no dangerous entities
            if all(isinstance(e, str) for e in char):
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
            else:
                print('selection contains characters that cannot be pasted into text box')
        
        elif name == 'Copy':
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                
                output = self._LIST[self._i : self._j]
        
        elif name == 'Cut':
            # delete selection
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                output = self._LIST[self._i : self._j]
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
        
        i = bisect.bisect([g[1] for g in self._template[:-1]], x)
        if i > 0 and x - self._template[i - 1][1] < self._template[i][1] - x:
            i -= 1
        return i

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

    def focus_drag(self, x):
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
        # dump entry
        self._VALUE = self._entry()
        if self._VALUE != self._PREV_VALUE:
            self._BEFORE()
            self._callback(self._domain(self._VALUE), * self._params)
            self._SYNCHRONIZE()
            self._AFTER()
        else:
            return False
        return True

    def hover(self, x, y):
        return 1
    # drawing
    def _sup_draw(self, cr, hover):
        pass
    
    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        self._sup_draw(cr, hover=hover)
        
        if self.broken:
            if hover[0] is not None:
                resting_bar_color = self._broken_active_bar_color
            else:
                resting_bar_color = self._broken_resting_bar_color
            active_bar_color = self._broken_active_bar_color
            resting_text_color = self._broken_resting_text_color
            active_text_color = self._broken_active_text_color
        else:
            if hover[0] is not None:
                resting_bar_color = self._active_bar_color
            else:
                resting_bar_color = self._resting_bar_color
            active_bar_color = self._active_bar_color
            resting_text_color = self._resting_text_color
            active_text_color = self._active_text_color
            
        fontsize = round(self.font.u_fontsize)
        
        cr.rectangle(self._text_left - 1, self._y, self._text_width + 2, self._height)
        cr.clip()
        
        if self._active:
            cr.set_source_rgba( * active_text_color)
        else:
            cr.set_source_rgba( * resting_text_color)
        
        cr.save()
        cr.translate(round(self._scroll), 0)
        
        # don't print the cap glyph
        cr.show_glyphs(self._template[:-1])
        
        if self._active:
            # print cursors
            cr.set_source_rgb( * accent)
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
        cr.reset_clip()
                
        if self._name is not None:
            cr.move_to(self._x, self._y + self.font.u_fontsize + 5)
            cr.set_font_size(11)
            # print label
            for label in self._texts:
                cr.show_glyphs(label)
        
        if self._active:
            cr.set_source_rgba( * active_bar_color)
        else:
            cr.set_source_rgba( * resting_bar_color)
        cr.rectangle(self._text_left, self._y + fontsize + 10, self._text_width, 1)
        cr.fill()


class Numeric_field(Blank_space):
    def __init__(self, x, y, width, callback, value_acquire, params=(), before=lambda: None, after=lambda: None, name=None):
    
        Blank_space.__init__(self, x, y, width, callback, value_acquire, params, before, after, name)
        
        self._digits = lambda k: ''.join([c for c in k if c in '1234567890.-'])
        self._domain = lambda k: float(self._digits(k)) if '.' in k else int(self._digits(k))

    def _stamp_glyphs(self, text):
        self._template = self._build_line(self._text_left, self._y + self.font.u_fontsize + 5, text, self.font, sub_minus=True)

    def _ACQUIRE_REPRESENT(self):
        self._VALUE = str(self._value_acquire( * self._params))
        self._LIST = list(self._VALUE) + [None]
        self._stamp_glyphs(self._LIST)

class Integer_field(Numeric_field):
    def __init__(self, x, y, width, callback, value_acquire, params=(), before=lambda: None, after=lambda: None, name=None):
        Numeric_field.__init__(self, x, y, width, callback, value_acquire, params, before, after, name)
        self._domain = lambda k: int(float(self._digits(k)))

class Enumerate_field(Numeric_field):
    def __init__(self, x, y, width, callback, value_acquire, params=(), before=lambda: None, after=lambda: None, name=None):
        Blank_space.__init__(self, x, y, width, callback, value_acquire, params, before, after, name)
        self._domain = lambda k: set( int(v) for v in [''.join([c for c in val if c in '1234567890']) for val in k.split(',')] if v )

    def _ACQUIRE_REPRESENT(self):
        self._VALUE = str(self._value_acquire( * self._params))[1:-1]
        self._LIST = list(self._VALUE) + [None]
        self._stamp_glyphs(self._LIST)

class Binomial_field(Numeric_field):
    def __init__(self, x, y, width, callback, value_acquire, params, before=lambda: None, after=lambda: None, name=None, letter='X'):
        Blank_space.__init__(self, x, y, width, callback, value_acquire, params, before, after, name)
        letters = set('1234567890.-+' + letter)
        self._domain = lambda k: plane.pack_binomial(''.join([c for c in k if c in letters]))

    def _ACQUIRE_REPRESENT(self):
        self._VALUE = plane.read_binomial( * self._value_acquire( * self._params))
        self._LIST = list(self._VALUE) + [None]
        self._stamp_glyphs(self._LIST)

#########
class Selection_menu(Base_kookie):
    def __init__(self, x, y, width, height, menu_callback, options_acquire, value_acquire, params = (), before=lambda: None, after=lambda: None, source=0):
        Base_kookie.__init__(self, x, y, width, height, font=styles.FONTSTYLES['_interface:STRONG'])
        
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
        print(self._lookup_label)

    def _ACQUIRE_REPRESENT(self):
        label = self._lookup_label[self._get_value( * self._params)]
        self._texts = []
        self._add_static_text(self._x_right, self._y_bottom - self._height/2 + 5, label, align=-1)

    def _SYNCHRONIZE(self):
        self._ACQUIRE_OPTIONS()
        self._ACQUIRE_REPRESENT()
    
    def _MENU_PUSH(self, * args):
        self._menu_callback( * args)
        self._SYNCHRONIZE()
    
    def focus(self, x, y):
        menu.menu.create(self._x, self._y_bottom - 5, 200, self._menu_options, self._MENU_PUSH, self._params, before=self._BEFORE, after=self._AFTER, source=self._source )
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

class Datablock_selection_menu(Selection_menu):
    def _ACQUIRE_OPTIONS(self):
        self._menu_options = self._get_options()
    def _ACQUIRE_REPRESENT(self):
        current = self._get_value( * self._params)
        self._texts = []
        self._add_static_text(self._x_right, self._y_bottom - self._height/2 + 5, current, align=-1)
    def focus(self, x, y):
        menu.menu.create(self._x_right - 200, self._y_bottom - 5, 200, self._menu_options, self._MENU_PUSH, self._params, before=self._BEFORE, after=self._AFTER, source=self._source )
#########
class Double_selection_menu(Selection_menu):
    def __init__(self, x, y, width, height, menu_callback, options_acquire, options_acquire_l2, value_acquire, source):
        
        self._options_acquire_l2 = options_acquire_l2
        Selection_menu.__init__(self, x, y, width, height, menu_callback, options_acquire, value_acquire, source)

    def _ACQUIRE_OPTIONS(self):
        self._menu_options = self._get_options()
        self._lookup_label = dict(self._menu_options)
        for key in self._lookup_label:
            self._lookup_label[key] = dict(self._options_acquire_l2(key))
            
    def _ACQUIRE_REPRESENT(self):
        V = self._get_value()
        label = self._display(V, self._lookup_label[V[0]][V[1]])
        self._texts = []
        self._add_static_text(self._x_right, self._y_bottom - self._height/2 + 5, label, align=-1)
        
    def _MENU_PUSH(self, branch):
        menu.menu.create(self._x, self._y_bottom - 5, 200, self._options_acquire_l2(branch), self._DOUBLE_MENU_PUSH, (), extend_life=True, source=self._source )
    
    def _DOUBLE_MENU_PUSH(self, * args):
        self._menu_callback( * args)
        self._SYNCHRONIZE()

class New_object_menu(Base_kookie):
    def __init__(self, x, y, width, value_push, library, params = (), before=lambda: None, after=lambda: None, name='', source=0):
        Base_kookie.__init__(self, x, y, width, 28, font=styles.FONTSTYLES['_interface:STRONG'])
        self._BEFORE = before
        self._AFTER = after
        self._params = params
        self._library = library
        self._value_push = value_push

        self.broken = False
        self._dropdown_active = False
        self.is_over_hover = self.is_over
        
        self._source = source
        
        self._add_static_text(self._x + 40, self._y + self.font.u_fontsize + 5, 'NEW')
        
        self._SYNCHRONIZE()

    def _SYNCHRONIZE(self):
        # scan objects
        self._menu_options = tuple( (v, str(k)) for k, v in sorted(self._library.items()) )

    def focus(self, x, y):
        J = self.hover(x, y)

        if J == 3:
            F = next(iter(self._library.values()))
            KEY = F.next_name('New fontclass')
            self._library[KEY] = F.copy(KEY)
            self._value_push(self._library[KEY], * self._params)
        elif J == 2:
            menu.menu.create(self._x, self._y_bottom - 5, 200, self._menu_options, lambda *args: (self._BEFORE(), self._value_push(*args), self._AFTER()), self._params, source=self._source )
            self._active = True
            self._dropdown_active = True
            print('DROPDOWN')
        
        self._AFTER()
    
    def hover(self, x, y):
        if x < self._x + 30:
            j = 2
        else:
            j = 3
        return j
        
    def draw(self, cr, hover=(None, None)):
        cr.set_line_width(2)
        if self._dropdown_active:
            cr.set_source_rgb( * accent)
        elif hover[1] == 2:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        
        # DROPDOWN
        cr.move_to(self._x + 8, self._y + 10)
        cr.rel_line_to(5, 5)
        cr.rel_line_to(5, -5)
        cr.stroke()

        # +
        if hover[1] == 3:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        cr.rectangle(self._x_right - 40, self._y + 7, 2, 10)
        cr.rectangle(self._x_right - 44, self._y + 11, 10, 2)
        cr.fill()
        self._render_fonts(cr)
        cr.show_glyphs(self._texts[0])
        
class Object_menu(Blank_space):
    def __init__(self, x, y, width, value_acquire, value_push, library, params = (), before=lambda: None, after=lambda: None, name='', source=0):

        self._library = library
        self._value_push = value_push

        Blank_space.__init__(self, x, y, width, lambda O, N, *args: O.rename(N, *args), value_acquire, params, before, after, name)

        self.broken = False
        self._dropdown_active = False
        
        self._source = source

    def _set_text_bounds(self):
        self._text_left = self._x + 30
        self._text_right = self._x_right

    def _ACQUIRE_REPRESENT(self):
        # scan objects
        self._menu_options = tuple( (v, str(k)) for k, v in sorted(self._library.items()) )
        
        self._O = self._value_acquire( * self._params)

        self._VALUE = self._O.name
        self._LIST = list(self._VALUE) + [None]
        self._stamp_glyphs(self._LIST)
        
    def _new(self):
        KEY = self._O.next_name()
        self._library[KEY] = self._O.copy(KEY)
        return self._library[KEY]

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
                O = self._new()
                self._value_push(O, * self._params)
            elif J == 2:
                menu.menu.create(self._x, self._y_bottom - 5, 200, self._menu_options, lambda *args: (self._BEFORE(), self._value_push(*args), self._AFTER()), self._params, source=self._source )
                self._active = True
                self._dropdown_active = True
                print('DROPDOWN')
            elif J == 4:
                # unlink
                self._value_push(None, * self._params)
            
            self._AFTER()
        
    def defocus(self):
        self._active = None
        self._dropdown_active = False
        self._scroll = 0
        # dump entry
        self._VALUE = self._entry()
        if self._VALUE != self._PREV_VALUE:
            self._BEFORE()
            self._callback(self._O, self._VALUE, * self._params)
            self._AFTER()

        else:
            return False
        return True
    
    def hover(self, x, y):
        if x < self._x + 30:
            j = 2
        elif x < self._x_right - 52:
            j = 1
        elif x < self._x_right - 26:
            j = 3
        else:
            j = 4
        return j
        
    def _sup_draw(self, cr, hover=(None, None)):
        cr.set_line_width(2)
        if self._dropdown_active:
            cr.set_source_rgb( * accent)
        elif hover[1] == 2:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        
        # DROPDOWN
        cr.move_to(self._x + 8, self._y + 10)
        cr.rel_line_to(5, 5)
        cr.rel_line_to(5, -5)
        cr.stroke()

        # +
        if hover[1] == 3:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        cr.rectangle(self._x_right - 40, self._y + 7, 2, 10)
        cr.rectangle(self._x_right - 44, self._y + 11, 10, 2)
        cr.fill()

        # x
        if hover[1] == 4:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        cr.move_to(self._x_right - 9, self._y + 8)
        cr.rel_line_to(-8, 8)
        cr.rel_move_to(0, -8)
        cr.rel_line_to(8, 8)
        cr.stroke()

class Orderable(Base_kookie):
    def __init__(self, x, y, width, height, datablock, display=lambda: None, before=lambda: None, after=lambda: None ):
        self._itemheight = 26
        self._display = display
        self._BEFORE = before
        self._AFTER = after

        Base_kookie.__init__(self, x, y, width, height, font=styles.FONTSTYLES['_interface:STRONG'])
        
        self._DB = datablock
        self._DB_ordered = self._DB.ordered

        # set hover function equal to press function
        self.is_over_hover = self.is_over

        self._SYNCHRONIZE = self._ACQUIRE_REPRESENT
        self._SYNCHRONIZE()

    def _ACQUIRE_REPRESENT(self):
        self._texts = []
        for i, l in enumerate(self._DB_ordered):
            self._add_static_text(self._x + 10, self._y + self._itemheight*i + 17, self._display(l), align=1)
    
    def _move(self, i, j):
        if 0 <= j < len(self._DB_ordered):
            self._DB_ordered.insert(j, self._DB_ordered.pop(i))
            self._DB.active = j
    
    def _add(self):
        if self._DB_ordered:
            O = self._DB_ordered[self._DB.active]
        else:
            O = styles.T_UNDEFINED
        self._DB_ordered.append(O.copy(O.next_name()))
        self._DB.active  = len(self._DB_ordered) - 1
        self._DB.update_map()
    
    def hover(self, x, y):
        y -= self._y
        i = int(y // self._itemheight)
        if i > len(self._DB_ordered):
            i = len(self._DB_ordered)
        
        if x > self._x_right - 25:
            j = 4
        elif x > self._x_right - 47:
            j = 3
        elif x > self._x_right - 69:
            j = 2
        else:
            j = 1
        return i, j
    
    def focus(self, x, y):
        F, C = self.hover(x, y)

        if F == len(self._DB_ordered):
            self._BEFORE()
            self._add()
            self._SYNCHRONIZE()
            self._AFTER()
        else:
            if C == 1:
                self._DB.active = F

            elif C == 2:
                self._BEFORE()
                self._move(F, F - 1)
                self._SYNCHRONIZE()

            elif C == 3:
                self._BEFORE()
                self._move(F, F + 1)
                self._SYNCHRONIZE()

            elif C == 4:
                self._BEFORE()
                del self._DB_ordered[F]
                
                if self._DB.active >= len(self._DB_ordered):
                    self._DB.active = len(self._DB_ordered) - 1
                self._DB.update_map()
                self._SYNCHRONIZE()
            
            self._AFTER()

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        cr.set_source_rgba(0, 0, 0, 0.7)
        cr.set_line_width(2)
        
        y1 = self._y
        for i, l in enumerate(self._texts):
            if i == self._DB.active:
                cr.set_source_rgb( * accent)

                radius = 5

                y2 = y1 + self._itemheight
                cr.arc(self._x + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
                cr.arc(self._x_right - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
                cr.arc(self._x_right - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
                cr.arc(self._x + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
                cr.close_path()

                cr.fill()
                
                cr.set_source_rgb(1, 1, 1)
                cr.show_glyphs(l)
                
                cr.move_to(self._x_right - 9, y1 + 9)
                cr.rel_line_to(-8, 8)
                cr.rel_move_to(0, -8)
                cr.rel_line_to(8, 8)
                cr.stroke()

                cr.move_to(self._x_right - 30 - 10, y1 + 10)
                cr.rel_line_to(5, 5)
                cr.rel_line_to(5, -5)
                cr.stroke()

                cr.move_to(self._x_right - 54 - 10, y1 + 15)
                cr.rel_line_to(5, -5)
                cr.rel_line_to(5, 5)
                cr.stroke()

                cr.set_source_rgba(0, 0, 0, 0.7)
            elif hover[1] is not None and hover[1][0] == i:
                if hover[1][1] == 1:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                cr.show_glyphs(l)

                if hover[1][1] == 3:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                cr.move_to(self._x_right - 30 - 10, y1 + 10)
                cr.rel_line_to(5, 5)
                cr.rel_line_to(5, -5)
                cr.stroke()

                if hover[1][1] == 2:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                cr.move_to(self._x_right - 54 - 10, y1 + 15)
                cr.rel_line_to(5, -5)
                cr.rel_line_to(5, 5)
                cr.stroke()

                if hover[1][1] == 4:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                cr.move_to(self._x_right - 9, y1 + 9)
                cr.rel_line_to(-8, 8)
                cr.rel_move_to(0, -8)
                cr.rel_line_to(8, 8)
                cr.stroke()
                
                cr.set_source_rgba(0, 0, 0, 0.7)
            else:
                cr.show_glyphs(l)

            y1 += self._itemheight
        
        if hover[1] is not None and hover[1][0] == len(self._DB_ordered):
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        cr.rectangle(self._x + 16, y1 + 7, 2, 10)
        cr.rectangle(self._x + 12, y1 + 11, 10, 2)
        
        cr.fill()

class Unorderable(Base_kookie):
    def __init__(self, x, y, width, height, datablock, protect=set(), display=lambda: None, before=lambda: None, after=lambda: None ):
        self._itemheight = 26
        self._protect = protect
        self._display = display
        self._BEFORE = before
        self._AFTER = after

        Base_kookie.__init__(self, x, y, width, height, font=styles.FONTSTYLES['_interface:STRONG'])
        
        self._DB = datablock

        # set hover function equal to press function
        self.is_over_hover = self.is_over

        self._SYNCHRONIZE = self._ACQUIRE_REPRESENT
        self._SYNCHRONIZE()

    def _ACQUIRE_REPRESENT(self):
        self._map = list(self._DB.elements.keys())
        
        self._texts = []
        if self._map:
            self._map.sort()
            for i, l in enumerate(self._map):
                self._add_static_text(self._x + 10, self._y + self._itemheight*i + 17, self._display(l), align=1)
    
    def hover(self, x, y):
        y -= self._y
        i = int(y // self._itemheight)
        if i > len(self._DB.elements):
            i = len(self._DB.elements) - 1
        
        if x > self._x_right - 25:
            j = 4
        else:
            j = 1
        return i, j
    
    def focus(self, x, y):
        F, C = self.hover(x, y)

        if F == len(self._DB.elements):
            self._BEFORE()
            self._DB.add_slot()
            self._SYNCHRONIZE()
            self._AFTER()
        else:
            key = self._map[F]
            if C == 1 or key in self._protect:
                self._DB.active = key
                self._AFTER()

            elif C == 4:
                self._BEFORE()
                self._DB.delete_slot(key)
                self._SYNCHRONIZE()
                self._AFTER()

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        cr.set_line_width(2)
        y1 = self._y
        
        for i, l in enumerate(self._texts):
            key = self._map[i]
            if key == self._DB.active:
                cr.set_source_rgb( * accent)

                radius = 5

                y2 = y1 + self._itemheight
                cr.arc(self._x + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
                cr.arc(self._x_right - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
                cr.arc(self._x_right - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
                cr.arc(self._x + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
                cr.close_path()

                cr.fill()
                
                cr.set_source_rgb(1, 1, 1)
                
                if key not in self._protect:
                    cr.move_to(self._x_right - 9, y1 + 9)
                    cr.rel_line_to(-8, 8)
                    cr.rel_move_to(0, -8)
                    cr.rel_line_to(8, 8)
                    cr.stroke()

            elif hover[1] is not None and hover[1][0] == i:
                if key not in self._protect:
                    if hover[1][1] == 4:
                        cr.set_source_rgb( * accent)
                    else:
                        cr.set_source_rgba(0, 0, 0, 0.7)
                    cr.move_to(self._x_right - 9, y1 + 9)
                    cr.rel_line_to(-8, 8)
                    cr.rel_move_to(0, -8)
                    cr.rel_line_to(8, 8)
                    cr.stroke()

                if hover[1][1] == 1:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)

            else:
                cr.set_source_rgba(0, 0, 0, 0.7)
            cr.show_glyphs(l)
            y1 += self._itemheight

        if hover[1] is not None and hover[1][0] == len(self._DB.elements):
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        cr.rectangle(self._x + 16, y1 + 7, 2, 10)
        cr.rectangle(self._x + 12, y1 + 11, 10, 2)
        
        cr.fill()

class Subset_table(Base_kookie):
    def __init__(self, x, y, width, height, datablock, superset, params = (), before=lambda: None, after=lambda: None):
        self._itemheight = 26
        self._BEFORE = before
        self._AFTER = after
        self._params = params

        Base_kookie.__init__(self, x, y, width, height, font=styles.FONTSTYLES['_interface:STRONG'])

        self._DB = datablock
        self._SS = superset

        # set hover function equal to press function
        self.is_over_hover = self.is_over

        self._SYNCHRONIZE = self._ACQUIRE_REPRESENT
        self._SYNCHRONIZE()

    def _ACQUIRE_REPRESENT(self):
        self._map = list(self._SS.keys())
        
        self._texts = []
        self._map.sort()
        for i, l in enumerate(self._map):
            self._add_static_text(self._x + 10, self._y + self._itemheight*i + 17, l, align=1)

    def hover(self, x, y):
        y -= self._y
        i = int(y // self._itemheight)
        if i >= len(self._SS):
            i = len(self._SS) - 1
        
        if x > self._x_right - 25:
            j = 4
        else:
            j = 1
        return i, j

    def focus(self, x, y):
        F, C = self.hover(x, y)

        key = self._map[F]
        if C == 1 and key in self._DB.elements:
            self._DB.active = key
            self._AFTER()

        elif C == 4:
            self._BEFORE()
            if key in self._DB.elements:
                self._DB.delete_slot(key)
            else:
                self._DB.add_slot(key)
            self._SYNCHRONIZE()
            self._AFTER()
    
    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        cr.set_line_width(1.5)
        y1 = self._y
        
        for i, l in enumerate(self._texts):
            key = self._map[i]
            if key == self._DB.active:
                cr.set_source_rgb( * accent)

                radius = 5

                y2 = y1 + self._itemheight
                cr.arc(self._x + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
                cr.arc(self._x_right - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
                cr.arc(self._x_right - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
                cr.arc(self._x + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
                cr.close_path()

                cr.fill()

                if hover[1] == (i, 4):
                    cr.set_source_rgba(1, 1, 1, 0.9)
                else:
                    cr.set_source_rgb(1, 1, 1)
                cr.arc(self._x_right - 15, y1 + 13, 6, 0, 2*pi)
                cr.fill()

                cr.set_source_rgb(1, 1, 1)

            elif hover[1] is not None and hover[1][0] == i:
                
                if hover[1][1] == 4:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                
                if key in self._DB.elements:
                    cr.arc(self._x_right - 15, y1 + 13, 6, 0, 2*pi)
                    cr.fill()
                    cr.set_source_rgb( * accent)
                else:
                    cr.arc(self._x_right - 15, y1 + 13, 5.5, 0, 2*pi)
                    cr.stroke()
                    cr.set_source_rgba(0, 0, 0, 0.4)

            elif key in self._DB.elements:
                cr.set_source_rgba(0, 0, 0, 0.7)
                cr.arc(self._x_right - 15, y1 + 13, 6, 0, 2*pi)
                cr.fill()
            else:
                cr.set_source_rgba(0, 0, 0, 0.7)
                cr.arc(self._x_right - 15, y1 + 13, 5.5, 0, 2*pi)
                cr.stroke()
                cr.set_source_rgba(0, 0, 0, 0.4)
                
            cr.show_glyphs(l)
            y1 += self._itemheight


class Binary_table(Base_kookie):
    def __init__(self, x, y, width, height, cellsize, callback, states_acquire, params = (), before=lambda: None, after=lambda: None):
        self._BEFORE = before
        self._AFTER = after
        self._callback = callback
        self._params = params
        self._cellwidth, self._cellheight = cellsize

        Base_kookie.__init__(self, x, y, width, height, font=styles.FONTSTYLES['_interface:STRONG'])
        
        self._per_row = ( self._width // self._cellwidth )
        self._states_acquire = states_acquire

        # set hover function equal to press function
        self.is_over_hover = self.is_over

        self._SYNCHRONIZE = self._ACQUIRE_REPRESENT
        self._SYNCHRONIZE()

    def _ACQUIRE_REPRESENT(self):
        self._STATES, self._NAMES = zip( * self._states_acquire( * self._params))
        self._STATES = list(self._STATES)
        self._construct_table()

    def _construct_table(self):
        self._texts = []
        self._cells = []
        x = self._x
        y = self._y
        mp = self._cellwidth/2
        for name in self._NAMES:
            if x + self._cellwidth > self._x_right:
                x = self._x
                y += self._cellheight
            
            self._add_static_text(x + mp, y + 17, name, align=0)
            self._cells.append((x, y, self._cellwidth, self._cellheight))
            
            x += self._cellwidth

    def hover(self, x, y):
        y -= self._y
        x -= self._x
        i = (y // self._cellheight) * self._per_row
        ij = x // self._cellwidth
        if ij >= self._per_row:
            ij = self._per_row - 1
        i = int(i + ij)
        if i >= len(self._STATES):
            i = None
        return i

    def focus(self, x, y):
        i = self.hover(x, y)

        if i is not None:
            self._BEFORE()
            self._STATES[i] = not self._STATES[i]
            self._callback(self._STATES, * self._params)
            self._SYNCHRONIZE()
            self._AFTER()

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        for i, cell in enumerate(self._cells):
            if self._STATES[i]:
                cr.set_source_rgb( * accent)

                cr.rectangle( * cell)
                cr.fill()
                
                cr.set_source_rgb(1, 1, 1)
            
            elif hover[1] == i:
                cr.set_source_rgb( * accent)
            else:
                cr.set_source_rgba(0, 0, 0, 0.7)
            cr.show_glyphs(self._texts[i])
