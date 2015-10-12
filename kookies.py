import bisect
import menu
import fonttable
import constants
from math import pi, floor

class Base_kookie(object):
    def __init__(self, x, y, width, height, font=None):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        
        self._active = None
        
        self._texts = []
        
        if font is None:
            self.font = fonttable.table.get_font('_interface', () )
        else:
            self.font = font
        
        self._x_right = x + width
        self._y_bottom = y + height
        
        self.y = self._y_bottom
    
    def translate(self, dx=0, dy=0):
        if dy != 0 and dx != 0:
            self._x += dx
            self._x_right += dx
            self._y += dy
            self._y_bottom += dy
            self.y += dy
            for glyphs in self._texts:
                glyphs[:] = [(g[0], g[1] + dx, g[2] + dy) for g in glyphs]
        elif dx != 0:
            self._x += dx
            self._x_right += dx
            for glyphs in self._texts:
                glyphs[:] = [(g[0], g[1] + dx, g[2]) for g in glyphs]
        else:
            self._y += dy
            self._y_bottom += dy
            self.y += dy
            for glyphs in self._texts:
                glyphs[:] = [(g[0], g[1], g[2] + dy) for g in glyphs]
        
        self._translate_other(dx, dy)
    
    def _translate_other(self, dx, dy):
        pass

    def _build_line(self, x, y, text, font, fontsize=None, align=1, sub_minus=False):
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
                line.append((None, x, y))

        if align == 0:
            dx = (xo - x)/2
            line = [(g[0], g[1] + dx, g[2]) for g in line]
        elif align == -1:
            dx = xo - x
            line = [(g[0], g[1] + dx, g[2]) for g in line]
        
        return line
    
    def _add_static_text(self, x, y, text, font=None, fontsize=None, upper=False, align=1):
        if font is None:
            font = self.font
        if upper:
            text = text.upper()
        self._texts.append(self._build_line(x, y, text, font, fontsize=fontsize, align=align))
    
    def is_over(self, x, y):
        if self._y <= y <= self._y_bottom and self._x <= x <= self._x_right:
            return True
        else:
            return False
    
    def is_over_hover(self, x, y):
        return False
    
    
    def type_box(self, name, char):
        pass
    
    def _render_fonts(self, cr):
        cr.set_font_size(self.font['fontsize'])
        cr.set_font_face(self.font['font'])


class Button(Base_kookie):
    def __init__(self, x, y, width, height, callback=None, string=''):
        Base_kookie.__init__(self, x, y, width, height, font=fonttable.table.get_font('_interface', ('strong',) ))
        
        self._callback = callback
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
            self._callback()
    
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
    def __init__(self, x, y, width, height, default=None, callback=None, callback_parameters = (), string=''):
        Base_kookie.__init__(self, x, y, width, height, font=fonttable.table.get_font('_interface', ('label', )) )
        
        if default:
            self._active = 1
        else:
            self._active = None
        
        self._callback = callback
        self._callback_parameters = callback_parameters

        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._add_static_text(self._x_right - 30, self._y_bottom - 5, string, align=-1)

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
        
        cr.set_source_rgb(0,0,0)
        cr.rectangle(self._x, self._y, self._width, self._height)
        cr.fill()
        
        if self._active:
            cr.set_source_rgb(1, 0.2, 0.6)
            
        elif hover[1]:
            cr.set_source_rgb(1, 0.2, 0.6)

        else:
            cr.set_source_rgb(0,0,0)
        
        cr.show_glyphs(self._texts[0])


class Tabs(Base_kookie):
    def __init__(self, x, y, width, height, default=0, callback=None, signals=None, strings=None):

        Base_kookie.__init__(self, x, y, width, height, font=fonttable.table.get_font('_interface', ('strong',) ))
        
        self._signals = signals
        self._strings = strings
        
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
    
    def _translate_other(self, dx, dy):
        if dx != 0:
            self._x_left[:] = [x + dx for x in self._x_left]
    
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

    # used only when initializing panel
    def active_name(self):
        return self._signals[self._active]

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


class Menu(Base_kookie):
    def __init__(self, x, y, width, item_height, signals=None):

        Base_kookie.__init__(self, x, y, width, item_height*len(signals))
        
        # 'centers' menu
        k = constants.window.get_k()
        if self._y > k/2:
            self.translate(dy = -self._height)
            
        if self._y < 0:
            self.translate(dy = -self._y)
        elif self._y_bottom > k:
            self.translate(dy = k - self._y_bottom)

        self._item_height = item_height
        self._signals = signals
        
        self._construct()
        
    def _construct(self):
        # build menu
        y = self._y
        for signal in self._signals:
            self._add_static_text(self._x + 10, y + self._item_height - 11, str(signal) )
            y += self._item_height

    def _target(self, y):
        y = (y - self._y)/self._item_height
        return int(floor(y))
            
    def press(self, y):
        i = self._target(y)
        return self._signals[i]

    def hover(self, y):
        return self._target(y)

    def draw(self, cr, hover=None):
        self._render_fonts(cr)
        
        cr.set_source_rgba(0.8, 0.8, 0.8, 1)
        cr.rectangle(self._x, self._y, self._width, self._height)
        cr.fill()
        cr.set_source_rgba(1, 1, 1, 1)
        cr.rectangle(self._x + 1, self._y + 1, self._width - 2, self._height - 2)
        cr.fill()
        
        for i, label in enumerate(self._texts):
            if i == hover:
                cr.set_source_rgba(1, 0.2, 0.6, 1)
                cr.rectangle(self._x, self._y + i*self._item_height, self._width, self._item_height)
                cr.fill()
                cr.set_source_rgb(1, 1, 1)
            else:
                cr.set_source_rgb(0,0,0)
            cr.show_glyphs(label)



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
        self._glyphs = []
        
        self._stamp_glyphs(self._text)
        self._reset_scroll()
        
    def _stamp_glyphs(self, text):
        self._template = self._build_line(self._x, self._y + self.font['fontsize'] + 5, text, self.font)

    def _reset_scroll(self):
        self._glyphs[:] = self._template[:]

    # translates stuff that was missed
    def _translate_other(self, dx, dy):
        if dy != 0 and dx != 0:
            self._template[:] = [(g[0], g[1] + dx, g[2] + dy) for g in self._template]
        elif dx != 0:
            self._template[:] = [(g[0], g[1] + dx, g[2]) for g in self._template]
        else:
            self._template[:] = [(g[0], g[1], g[2] + dy) for g in self._template]
        self._reset_scroll()
        
    def is_over(self, x, y):
        if self._y <= y <= self._y_bottom and self._x - 10 <= x <= self._x_right + 10:
            return True
        else:
            return False

    def _entry(self):
        return ''.join(self._text[:-1])

    # scrolling functions
    def _anchor_x(self, x):
        dx = x - self._x
        self._glyphs[:] = [(g[0], g[1] + dx, g[2]) for g in self._template]
    
    def _anchor(self, i, x):
        dx = self._template[i][1] - self._x - x
        self._glyphs[:] = [(g[0], g[1] - dx, g[2]) for g in self._template]

    def _center_x(self, x):
        relative_position = x - self._x
        if relative_position > self._width and self._glyphs[self._j][1] - self._x > self._width:
            self._anchor(self._j, self._width)
        elif relative_position < 0 and self._glyphs[self._j][1] - self._x < 0:
            self._anchor(self._j, 0)
            
    def _center_j(self):
        _relative_position = self._glyphs[self._j][1] - self._x
        if _relative_position > self._width:
            self._anchor(self._j, self._width)
        elif _relative_position < 0:
            self._anchor(self._j, 0)

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
            self._anchor_x(self._glyphs[0][1])
        self._center_j()
        
        return output

    # target glyph index
    def _target(self, x):
        i = bisect.bisect([g[1] for g in self._glyphs[:-1]], x)
        if i > 0 and x - self._glyphs[i - 1][1] < self._glyphs[i][1] - x:
            i -= 1
        return i


    def focus(self, x):
        self._active = True
        
        # clip to edges of visible text
        if x < self._x:
            self._i = self._target(self._x)
            # inch left or right
            if self._glyphs[self._i][1] > self._x:
                self._i -= 1
        elif x > self._x + self._width:
            self._i = self._target(self._x + self._width)
            
            if self._glyphs[self._i][1] < self._x + self._width:
                self._i += 1
        else:
            self._i = self._target(x)
        self._j = self._i
        
        self._center_x(self._glyphs[self._j][1])

    def focus_drag(self, x):
        self._j = self._target(x)
        
        self._center_x(x)

    def defocus(self):
        self._active = None
        self._dropdown_active = False
        self._text = list(self._entry()) + [None]
        self._stamp_glyphs(self._text)
        self._reset_scroll()
        # dump entry
        out = self._entry()
        if out != self._previous:
            self._previous = out
            self._callback(out)
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
            # print cursors
            cr.set_source_rgb(1, 0.2, 0.6)
            cr.rectangle(round(self._glyphs[self._i][1] - 1), 
                        self._y + 5, 
                        2, 
                        fontsize)
            cr.rectangle(round(self._glyphs[self._j][1] - 1), 
                        self._y + 5, 
                        2, 
                        fontsize)
            cr.fill()
            
            # print highlight
            if self._i != self._j:
                cr.set_source_rgba(0, 0, 0, 0.1)
                # find leftmost
                if self._i <= self._j:
                    root = self._glyphs[self._i][1]
                else:
                    root = self._glyphs[self._j][1]
                cr.rectangle(root, 
                        self._y + 5,
                        abs(self._glyphs[self._i][1] - self._glyphs[self._j][1]),
                        fontsize)
                cr.fill()
                
        if self._active:
            cr.set_source_rgba( * active_text_color)
        else:
            cr.set_source_rgba( * resting_text_color)
        # don't print the cap glyph
        cr.show_glyphs(self._glyphs[:-1])
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
            
            self._center_x(self._glyphs[self._j][1])
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
