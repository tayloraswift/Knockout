import bisect

from math import pi

from fonts import fonttable

from interface.base import Base_kookie
from interface import menu


class Button(Base_kookie):
    def __init__(self, x, y, width, height, callback=None, string='', params=() ):
        Base_kookie.__init__(self, x, y, width, height, font=fonttable.table.get_font('_interface', ('strong',) ))
        
        self._callback = callback
        self._params = params
#        self._string = string
        
        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._add_static_text(x + width/2, self._y_bottom - self._height/2 + 5, string, align=0)
    
    def focus(self, x):
        self._active = 1
    
    def focus_drag(self, x):
        pass
    
    def release(self, action=True):
        self._active = None
        if action:
            self._callback( * self._params)
    
    def defocus(self):
        pass

    def hover(self, x):
        return 1

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        if self._active:
            cr.set_source_rgba(1, 0.2, 0.6, 1)

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
            cr.set_source_rgba(1, 0.2, 0.6, 1)

        else:
            cr.set_source_rgb(0,0,0)
        cr.show_glyphs(self._texts[0])

class Checkbox(Button):
    def __init__(self, x, y, width, callback, callback_parameters = (), value_acquire=None, string=''):
        Base_kookie.__init__(self, x, y, width, 20, font=fonttable.table.get_font('_interface', ('label', )) )
        
        self._get_value = value_acquire
        self._ACQUIRE_REPRESENT()
        self._SYNCHRONIZE = self._ACQUIRE_REPRESENT
        
        self._callback = callback
        self._callback_parameters = callback_parameters

        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._add_static_text(self._x + 20, self._y_bottom - 5, string, align=1)

    def _ACQUIRE_REPRESENT(self):
        self._STATE = self._get_value()

    def focus(self, x):
        self._callback(not self._STATE, * self._callback_parameters)
        self._ACQUIRE_REPRESENT()

    def release(self, action=True):
        pass

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

        Base_kookie.__init__(self, x, y, width, height, font=fonttable.table.get_font('_interface', ('strong',) ))
        
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

    def focus(self, x):
        self._active = self._target(x)
        self._callback(self._signals[self._active])
    
    def focus_drag(self, x):
        pass
    
    def defocus(self):
        pass

    def hover(self, x):
        return self._target(x)

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        for i, button in enumerate(self._x_left):
            if i == self._active:
                cr.set_source_rgba(1, 0.2, 0.6, 1)

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
                cr.set_source_rgba(1, 0.2, 0.6, 1)

            else:
                cr.set_source_rgb(0,0,0)
            cr.show_glyphs(self._texts[i])

class Heading(Base_kookie):
    def __init__(self, x, y, width, height, text, font=fonttable.table.get_font('_interface', ('title',) ), fontsize=None, upper=False):
        
        Base_kookie.__init__(self, x, y, width, height)
        
        self.font = font
        if fontsize is None:
            fontsize = self.font['fontsize']
        
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
    def __init__(self, x, y, width, callback, value_acquire, params = (), name=''):
        self.broken = False
        
        Base_kookie.__init__(self, x, y, width, 28)

        self._callback = callback
        self._value_acquire = value_acquire
        
        self._SYNCHRONIZE()
        
        self._params = params
        
        self._domain = lambda k: k
        self._name = name
        
        self.is_over_hover = self.is_over
        
        # cursors
        self._i = len(self._LIST) - 1
        self._j = self._i
        
        # build static texts
        self._add_static_text(self._x, self._y + 40, self._name, font=fonttable.table.get_font('_interface', ('label', )) , upper=True)
        
        self._resting_bar_color = (0, 0, 0, 0.4)
        self._active_bar_color = (0, 0, 0, 0.8)
        self._resting_text_color = (0, 0, 0, 0.6)
        self._active_text_color = (0, 0, 0, 1)
        
        self._broken_resting_bar_color = (1, 0.15, 0.2, 0.8)
        self._broken_active_bar_color = (1, 0.15, 0.2, 1)
        self._broken_resting_text_color = (1, 0.15, 0.2, 0.8)
        self._broken_active_text_color = (1, 0.15, 0.2, 1)
        
        self._scroll = 0

    def _ACQUIRE_REPRESENT(self):
        self._VALUE = self._value_acquire()
        self._LIST = list(self._VALUE) + [None]
        self._stamp_glyphs(self._LIST)

    def _SYNCHRONIZE(self):
        self._ACQUIRE_REPRESENT()
        self._PREV_VALUE = self._VALUE

    def _stamp_glyphs(self, glyphs):
        self._template = self._build_line(self._x, self._y + self.font['fontsize'] + 5, glyphs, self.font)
        
    def is_over(self, x, y):
        return self._y <= y <= self._y_bottom and self._x - 10 <= x <= self._x_right + 10

    def _entry(self):
        return ''.join(self._LIST[:-1])
    
    # scrolling function
    def _center_j(self):
        position = self._template[self._j][1] - self._x
        if position + self._scroll > self._width:
            self._scroll = -(position - self._width)
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


    def focus(self, x):
        self._active = True
        
        # clip to edges of visible text
        if x < self._x:
            self._i = self._target(self._x)
            # inch left or right
            if self._template[self._i][1] > self._x:
                self._i -= 1
        elif x > self._x + self._width:
            self._i = self._target(self._x + self._width)
            if self._template[self._i][1] < self._x + self._width and self._i < len(self._template) - 1:
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
            self._callback(self._domain(self._VALUE), * self._params)
            self._SYNCHRONIZE()
        else:
            return False
        return True

    def hover(self, x):
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
            
        fontsize = round(self.font['fontsize'])
        
        cr.rectangle(self._x - 1, self._y, self._width + 2, self._height)
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
            cr.set_source_rgb(1, 0.2, 0.6)
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
            cr.move_to(self._x, self._y + self.font['fontsize'] + 5)
            cr.set_font_size(11)
            # print label
            for label in self._texts:
                cr.show_glyphs(label)
        
        if self._active:
            cr.set_source_rgba( * active_bar_color)
        else:
            cr.set_source_rgba( * resting_bar_color)
        cr.rectangle(self._x, self._y + fontsize + 10, self._width, 1)
        cr.fill()


class Numeric_field(Blank_space):
    def __init__(self, x, y, width, callback, value_acquire, params=(), name=None):
    
        Blank_space.__init__(self, x, y, width, callback, value_acquire, params, name)
        
        self._digits = lambda k: ''.join([c for c in k if c in '1234567890.-'])
        self._domain = lambda k: float(self._digits(k)) if '.' in k else int(self._digits(k))

    def _stamp_glyphs(self, text):
        self._template = self._build_line(self._x, self._y + self.font['fontsize'] + 5, text, self.font, sub_minus=True)

class Integer_field(Numeric_field):
    def __init__(self, x, y, width, callback, value_acquire, params=(), name=None):
    
        Numeric_field.__init__(self, x, y, width, callback, value_acquire, params, name)

        self._domain = lambda k: int(float(self._digits(k)))

class Enumerate_field(Blank_space):
    def __init__(self, x, y, width, callback, value_acquire, params=(), name=None):
    
        Blank_space.__init__(self, x, y, width, callback, value_acquire, params, name)

        self._domain = lambda k: set( int(v) for v in [''.join([c for c in val if c in '1234567890']) for val in k.split(',')] if v )

    def _stamp_glyphs(self, text):
        self._template = self._build_line(self._x, self._y + self.font['fontsize'] + 5, text, self.font, sub_minus=True)

        
#########
class Selection_menu(Base_kookie):
    def __init__(self, x, y, width, height, menu_callback, options_acquire, value_acquire, source):
        Base_kookie.__init__(self, x, y, width, height, font=fonttable.table.get_font('_interface', ('strong',) ))
        
        self._get_value = value_acquire
        self._get_options = options_acquire
        
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
        label = self._lookup_label[self._get_value()]
        self._texts = []
        self._add_static_text(self._x_right, self._y_bottom - self._height/2 + 5, label, align=-1)

    def _SYNCHRONIZE(self):
        self._ACQUIRE_OPTIONS()
        self._ACQUIRE_REPRESENT()
    
    def _MENU_PUSH(self, * args):
        self._menu_callback( * args)
        self._SYNCHRONIZE()
    
    def release(self, action=True):
        pass
    
    def focus(self, x):
        menu.menu.create(self._x, self._y_bottom - 5, 200, self._menu_options, self._MENU_PUSH, (), source=self._source )
        self._active = True
        self._dropdown_active = True
        print('DROPDOWN')

    def defocus(self):
        self._active = None
        self._dropdown_active = False

        return False

    def hover(self, x):
        return 1
    
    def draw(self, cr, hover=(None, None)):
        
        self._render_fonts(cr)
        
        if hover[1] == 1:
            cr.set_source_rgb(1, 0.2, 0.6)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
            
        cr.show_glyphs(self._texts[0])
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
        label = self._lookup_label[V[0]][V[1]]
        label = str(V[0]) + ' › ' + str(label)
        self._texts = []
        self._add_static_text(self._x_right, self._y_bottom - self._height/2 + 5, label, align=-1)
        
    def _MENU_PUSH(self, branch):
        menu.menu.create(self._x, self._y_bottom - 5, 200, self._options_acquire_l2(branch), self._DOUBLE_MENU_PUSH, (), extend_life=True, source=self._source )
    
    def _DOUBLE_MENU_PUSH(self, * args):
        self._menu_callback( * args)
        self._SYNCHRONIZE()

class Object_menu(Blank_space):
    def __init__(self, x, y, width, callback, addition_callback, menu_callback, menu_options, value_acquire, name=None, source=0):
        Blank_space.__init__(self, x, y, width, callback, value_acquire, (), name)

        self._addition_callback = addition_callback
        self._menu_callback = menu_callback
        self._menu_options = menu_options
        self.broken = False
        self._dropdown_active = False
        
        self._source = source
    
    def focus(self, x):
        if x < self._x + self._width - 40:
            self._active = True
            self._dropdown_active = False
            self._i = self._target(x)
            self._j = self._i
            
            self._center_j()
        else:
            self.defocus()
            if x < self._x + self._width - 20:
                self._addition_callback()
            else:
                menu.menu.create(self._x_right - 170, self._y_bottom - 5, 170, self._menu_options, self._menu_callback, (), source=self._source )
                self._active = True
                self._dropdown_active = True
                print('DROPDOWN')
            
    def hover(self, x):
        if x < self._x + self._width - 40:
            j = 1
        elif x < self._x + self._width - 20:
            j = 2
        else:
            j = 3
        return j
        
    def _sup_draw(self, cr, hover=(None, None)):
        if self._dropdown_active:
            cr.set_source_rgb(1, 0.2, 0.6)
        elif hover[1] == 3:
            cr.set_source_rgb(1, 0.2, 0.6)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        cr.move_to(self._x + self._width - 5, self._y + 8)
        cr.rel_line_to(8, 0)
        cr.rel_line_to(-4, 4*1.41)
        cr.close_path()
        cr.fill()

        if hover[1] == 2:
            cr.set_source_rgb(1, 0.2, 0.6)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        cr.rectangle(self._x + self._width - 25 - 8, self._y + 5, 2, 12)
        cr.rectangle(self._x + self._width - 25 - 13, self._y + 5 + 5, 12, 2)
        cr.fill()
