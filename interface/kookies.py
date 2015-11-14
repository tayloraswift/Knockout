import bisect

from math import pi

from state import noticeboard

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
    def __init__(self, x, y, width, default=None, callback=None, callback_parameters = (), string=''):
        Base_kookie.__init__(self, x, y, width, 20, font=fonttable.table.get_font('_interface', ('label', )) )
        
        if default:
            self._active = 1
        else:
            self._active = None
        
        self._callback = callback
        self._callback_parameters = callback_parameters

        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._add_static_text(self._x + 20, self._y_bottom - 5, string, align=1)

    def focus(self, x):
        if self._active is None:
            self._callback(True, * self._callback_parameters)
            self._active = 1
        else:
            self._callback(False, * self._callback_parameters)
            self._active = None
    
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
        if not self._active:
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
    def __init__(self, x, y, width, default, callback, name=None):
        
        Base_kookie.__init__(self, x, y, width, 28)
        
        # must be list
        self._text = list(default) + [None]
        self._previous = ''.join(default)

        self._callback = callback
        self._name = name
        
        self.broken = False
        
        self.is_over_hover = self.is_over
        
        # cursors
        self._i = len(self._text) - 1
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
        
        self._template = []
        self._scroll = 0
        
        self._stamp_glyphs(self._text)
        
    def _stamp_glyphs(self, text):
        self._template = self._build_line(self._x, self._y + self.font['fontsize'] + 5, text, self.font)
        
    def is_over(self, x, y):
        if self._y <= y <= self._y_bottom and self._x - 10 <= x <= self._x_right + 10:
            return True
        else:
            return False

    def _entry(self):
        return ''.join(self._text[:-1])

    def _domain(self, entry):
        return entry
    
    # scrolling function
            
    def _center_j(self):
        position = self._template[self._j][1] - self._x
        print(position + self._scroll)
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
                del self._text[self._i : self._j]
                changed = True
                self._j = self._i
                
            elif name == 'BackSpace':
                if self._i > 0:
                    del self._text[self._i - 1]
                    changed = True
                    self._i -= 1
                    self._j -= 1
            else:
                if self._i < len(self._text) - 2:
                    del self._text[self._i]
                    changed = True

        elif name == 'Left':
            if self._i > 0:
                self._i -= 1
                self._j = self._i
        elif name == 'Right':
            if self._i < len(self._text) - 1:
                self._i += 1
                self._j = self._i
        elif name == 'Home':
            self._i = 0
            self._j = 0
        elif name == 'End':
            self._i = len(self._text) - 1
            self._j = len(self._text) - 1
        
        elif name == 'Paste':
            # check to make sure string contains no dangerous entities
            if all(isinstance(e, str) for e in char):
                # delete selection
                if self._i != self._j:
                    # sort
                    if self._i > self._j:
                        self._i, self._j = self._j, self._i
                    del self._text[self._i : self._j]
                    self._j = self._i
                # take note that char is a LIST now
                self._text[self._i:self._i] = char
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
                
                output = self._text[self._i : self._j]
        
        elif name == 'Cut':
            # delete selection
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                output = self._text[self._i : self._j]
                del self._text[self._i : self._j]
                changed = True
                self._j = self._i
            
        
        elif char is not None:
            # delete selection
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                del self._text[self._i : self._j]
                self._j = self._i
            self._text[self._i:self._i] = [char]
            changed = True
            self._i += 1
            self._j += 1
        
        if changed:
            self._stamp_glyphs(self._text)
        
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
            
            if self._template[self._i][1] < self._x + self._width:
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
            noticeboard.refresh.push_change()

    def defocus(self):
        self._active = None
        self._dropdown_active = False
        self._text = list(self._entry()) + [None]
        self._stamp_glyphs(self._text)
        self._scroll = 0
        # dump entry
        out = self._entry()
        if out != self._previous:
            self._previous = out
            self._callback(self._domain(out))
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
        cr.save()
        cr.translate(round(self._scroll), 0)
        
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
                
        if self._active:
            cr.set_source_rgba( * active_text_color)
        else:
            cr.set_source_rgba( * resting_text_color)
        # don't print the cap glyph
        cr.show_glyphs(self._template[:-1])
        
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
    def __init__(self, x, y, width, default, callback, name=None):
    
        Blank_space.__init__(self, x, y, width, default, callback, name)

        self.broken = False
        
    def _entry(self):
        num = ''.join([c for c in self._text[:-1] if c in '1234567890.-'])

        return num
    
    def _to_number(self, string):
        if '.' in string:
            number = float(string)
        else:
            number = int(string)
        return number

    def _stamp_glyphs(self, text):
        self._template = self._build_line(self._x, self._y + self.font['fontsize'] + 5, text, self.font, sub_minus=True)

class Integer_field(Blank_space):
    def __init__(self, x, y, width, default, callback, name=None):
    
        Blank_space.__init__(self, x, y, width, default, callback, name)

        self.broken = False
        
    def _entry(self):
        num = ''.join([c for c in self._text[:-1] if c in '1234567890-'])

        return num
    
    def domain(self, entry):
        return int(entry)

    def _stamp_glyphs(self, text):
        self._template = self._build_line(self._x, self._y + self.font['fontsize'] + 5, text, self.font, sub_minus=True)

#########
class Selection_menu(Base_kookie):
    def __init__(self, x, y, width, height, callback, menu_callback, menu_options, default):
        Base_kookie.__init__(self, x, y, width, height, font=fonttable.table.get_font('_interface', ('strong',) ))
        
        self._callback = callback
        self._menu_callback = menu_callback
        self._menu_options = menu_options

        self._dropdown_active = False
        
        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._add_static_text(self._x_right, self._y_bottom - self._height/2 + 5, str(default), align=-1)
    
    def focus(self, x):
        menu.menu.create(self._x_right - 170, self._y_bottom - 5, 200, self._menu_options, self._menu_callback, () )
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

class Object_menu(Blank_space):
    def __init__(self, x, y, width, default, callback, addition_callback, menu_callback, menu_options, name=None):
        Blank_space.__init__(self, x, y, width, default, callback, name)

        self._addition_callback = addition_callback
        self._menu_callback = menu_callback
        self._menu_options = menu_options
        self.broken = False
        self._dropdown_active = False
    
    def focus(self, x):
        if x < self._x + self._width - 40:
            self._active = True
            self._dropdown_active = False
            self._i = self._target(x)
            self._j = self._i
            
            self._center_x(self._template[self._j][1])
        else:
            self.defocus()
            if x < self._x + self._width - 20:
                self._addition_callback()
            else:
                menu.menu.create(self._x_right - 170, self._y_bottom - 5, 170, self._menu_options, self._menu_callback, () )
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
