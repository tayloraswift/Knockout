import bisect
import fonts
from math import pi, floor

_ui_font = fonts.paragraph_classes['_interface'].fontclasses[()]

class Panel_object(object):
    def __init__(self):
        pass

    def _build_line(self, x, y, text, font, factor=1, align=1, sub_minus=False):
        xo = x
        line = []
        for character in text:
            if sub_minus and character == '-':
                character = '–'
            try:
                line.append((font.character_index(character), x, y))
                x += (font.glyph_width(character) + font.tracking)*factor
            except TypeError:
                line.append((None, x, y))
        if align == 1:
            return line
        elif align == 0:
            dx = (xo - x)/2
            return [(g[0], g[1] + dx, g[2]) for g in line]
        elif align == -1:
            dx = xo - x
            return [(g[0], g[1] + dx, g[2]) for g in line]
    
    def _stamp_glyphs(self, factor=1):
        self._template = self._build_line(self.x, self.y, self._text, self.font, factor)


    def _anchor_0(self):
        self._glyphs[:] = self._template[:]
    
    def hover_in_borders(self, x):
        return None
        
    def translate(self, dx):
        self.x += dx
        self._template[:] = [(g[0], g[1] + dx, g[2]) for g in self._template]
        self._anchor_0()

class heading(Panel_object):
    def __init__(self, x, y, width, text):
        
        self.x = x
        self.y = y
        self.width = width
        self._text = text.upper()
        
        self.font = fonts.paragraph_classes['_interface'].fontclasses[('title',)]
        
        self._glyphs = []
        self._stamp_glyphs()
        self._anchor_0()
    
    def in_borders(self, x):
        return None
        
    def draw(self, cr):
        
        cr.set_source_rgb(0,0,0)
        
        cr.rectangle(self.x, self.y + 10, self.width, 2)
        cr.fill()
        
        cr.set_font_size(self.font.fontsize)
        cr.set_font_face(self.font.font)
        cr.show_glyphs(self._glyphs)

class Mode_Buttons(Panel_object):
    def __init__(self, x, y, width, active_default, callback=None, names=None, labels=None):
    
        self.x = x
        self.y = y
        self.width = width
        self._names = names
        self._L = labels
        
        # list
        self._callback = callback
        
        self.hover_in_borders = self.in_borders
        
        self.font = fonts.paragraph_classes['_interface'].fontclasses[('strong',)]
        
        self._active = active_default
        self._hover = None
       
        self._labels = []

        self._button_width = self.width/len(self._names)
        self._x_left = []
        xo = self.x - width/2
        for label in self._L:
            self._labels.append(
                    self._build_line(xo + self._button_width/2, self.y - 6, label, self.font, align=0)
                    )
            self._x_left.append(int(round(xo)))
            xo += self._button_width
            
    def translate(self, dx):
        self.x += dx
        self._x_left[:] = [x + dx for x in self._x_left]
        
        for glyphs in self._labels:
            glyphs[:] = [(g[0], g[1] + dx, g[2]) for g in glyphs]


    def in_borders(self, x):
        if abs(x - self.x) < self.width/2:
            return x
        else:
            return None
    
    def focus(self, x):
        # this is intentionally exaggerated by one so that 0 means false
        self._active = bisect.bisect(self._x_left, x)
        if self._callback is not None:
            self._callback(self._names[self._active - 1])

    
    def focus_drag(self, x):
        pass
    
    def defocus(self):
        pass
#        self._active = False

    def hover(self, x):
        # this is intentionally exaggerated by one so that 0 means false
        self._hover = bisect.bisect(self._x_left, x)

           
    def draw(self, cr):
        cr.set_font_size(self.font.fontsize)
        cr.set_font_face(self.font.font)
        
        for i, button in enumerate(self._x_left):
            if i == self._active - 1:
                cr.set_source_rgba(1, 0.2, 0.6, 1)
#                cr.rectangle(button, self.y - 25, self._button_width, 30)
                radius = 5
                y1, y2, x1, x2 = self.y - 25, self.y + 5, button, button + int(round(self._button_width))
                cr.arc(x1 + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
                cr.arc(x2 - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
                cr.arc(x2 - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
                cr.arc(x1 + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
                cr.close_path()

                cr.fill()


            if i == self._active - 1:
                cr.set_source_rgb(1,1,1)
            elif self._hover is not None and i == self._hover - 1:
                cr.set_source_rgba(1, 0.2, 0.6, 1)
            else:
                cr.set_source_rgb(0,0,0)
            cr.show_glyphs(self._labels[i])
        
        self._hover = None
    
    def active_name(self):
        return self._names[self._active - 1]

class Menu(Panel_object):
    def __init__(self, x, y, width, item_height, callback=None, names=None):
        self.x = x
        self.y = y
        self.width = width
        self._item_height = item_height
        self._names = names
        
        self._bottom_extents = self.y + item_height*len(names)
        
        self._callback = callback
        
#        self.hover_in_borders = self.in_borders
        
        self.font = fonts.paragraph_classes['_interface'].fontclasses[()]
        
        self._hover = None
        
        self._labels = []
        
        # build menu
        y = self.y
        for name in self._names:
            self._labels.append(
                    self._build_line(self.x + 10, y + self.font.fontsize + 6, name, self.font)
                    )
            y += self._item_height
    
#    def in_borders(self, x):
#        if self.x <= x <= self.x + self.width:
#            return x
#        else:
#            return None
    
    def _target(self, x, y):
        if self.x <= x <= self.x + self.width and self.y <= y <= self._bottom_extents:
            y = (y - self.y)/self._item_height
            return int(floor(y))
        else:
            return None
    
    def hover(self, x, y):
        self._hover = self._target(x, y)
        if self._hover is None:
            return False
        else:
            return True
            
    def press(self, x, y):
        i = self._target(x, y)
        if i is None:
            return False
        else:
            self._callback(self._names[i])
            return True
            
    def translate(self, dx):
        self.x += dx
        
        for glyphs in self._labels:
            glyphs[:] = [(g[0], g[1] + dx, g[2]) for g in glyphs]
                
    def draw(self, cr):
        cr.set_source_rgba(0.8, 0.8, 0.8, 1)
        cr.rectangle(self.x, self.y, self.width, self._bottom_extents - self.y)
        cr.fill()
        cr.set_source_rgba(1, 1, 1, 1)
        cr.rectangle(self.x + 1, self.y, self.width - 2, self._bottom_extents - self.y - 1)
        cr.fill()

        
        cr.set_font_size(self.font.fontsize)
        cr.set_font_face(self.font.font)
        
        for i, name in enumerate(self._names):
            if self._hover is not None and i == self._hover:
                cr.set_source_rgba(1, 0.2, 0.6, 1)
                cr.rectangle(self.x, self.y + i*self._item_height, self.width, self._item_height)
                cr.fill()
                cr.set_source_rgb(1, 1, 1)
                self._hover = None
            else:
                cr.set_source_rgb(0,0,0)
            cr.show_glyphs(self._labels[i])
        
        
class Blank_Space(Panel_object):
    def __init__(self, default, x, y, width, callback, name=None, update=False):
        # must be list
        self._text = default + [None]
        self._previous = ''.join(default)
        

        
        self._callback = callback
        
        self._common(x, y, width, name, update)
    
    def _common(self, x, y, width, name, update=False):

        self.x = x
        self.y = y
        self.width = width
        self.name = name
        
        try: 
            self.font.fontsize
        except AttributeError:
            self.font = fonts.paragraph_classes['_interface'].fontclasses[()]
        
        self._resting_bar_color = (0, 0, 0, 0.4)
        self._active_bar_color = (0, 0, 0, 0.8)
        self._resting_text_color = (0, 0, 0, 0.6)
        self._active_text_color = (0, 0, 0, 1)
        
        self._broken_resting_bar_color = (1, 0.15, 0.2, 0.8)
        self._broken_active_bar_color = (1, 0.15, 0.2, 1)
        self._broken_resting_text_color = (1, 0.15, 0.2, 0.8)
        self._broken_active_text_color = (1, 0.15, 0.2, 1)
        
        self._i = len(self._text) - 1
        self._j = self._i
        
        self._glyphs = []
        self._label = self._build_line(self.x, self.y + self.font.fontsize + 5, self.name.upper(), self.font, factor=11/self.font.fontsize)
        
        self._active = False
        self._should_update = update
        
        self._dropdown_active = False
       
        self._stamp_glyphs()
        self._anchor_0()

    def translate(self, dx):
        self.x += dx
        self._template[:] = [(g[0], g[1] + dx, g[2]) for g in self._template]
        self._anchor_0()
        
        self._label[:] = [(g[0], g[1] + dx, g[2]) for g in self._label]
    
    def in_borders(self, x):
        if self.x - 10 < x < self.x + self.width + 10:
            if x < self.x:
                x = self.x
            elif x > self.x + self.width:
                x = self.x + self.width
            return x
        else:
            return None

    def _entry(self):
        return ''.join(self._text[:-1])


    def _anchor_x(self, x):
        dx = x - self.x
        self._glyphs[:] = [(g[0], g[1] + dx, g[2]) for g in self._template]
    
    def _anchor(self, i, x):
        dx = self._template[i][1] - self.x - x
        self._glyphs[:] = [(g[0], g[1] - dx, g[2]) for g in self._template]

    def _center_x(self, x):
        _relative_position = x - self.x
        if _relative_position > self.width and self._glyphs[self._j][1] - self.x > self.width:
            self._anchor(self._j, self.width)
        elif _relative_position < 0 and self._glyphs[self._j][1] - self.x < 0:
            self._anchor(self._j, 0)
            
    def _center_j(self):
        _relative_position = self._glyphs[self._j][1] - self.x
        if _relative_position > self.width:
            self._anchor(self._j, self.width)
        elif _relative_position < 0:
            self._anchor(self._j, 0)
    
    
    
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
            self._stamp_glyphs()
            self._anchor_x(self._glyphs[0][1])
        self._center_j()
        
        return output


    
    def _target(self, x):
        i = bisect.bisect([g[1] for g in self._glyphs[:-2]], x)
        if i > 0 and x - self._glyphs[i - 1][1] < self._glyphs[i][1] - x:
            i -= 1
        return i

    
    def focus(self, x):
        self._active = True
        self._i = self._target(x)
        self._j = self._i
        
        self._center_x(self._glyphs[self._j][1])
#        self._stamp_glyphs()
    
    def focus_drag(self, x):
        self._j = self._target(x)
        
        self._center_x(x)
    
    def defocus(self):
        self._active = False
        self._dropdown_active = False
        self._text = list(self._entry()) + [None]
        self._stamp_glyphs()
        self._anchor_0()
        # dump entry
        out = self._entry()
        if out != self._previous:
            self._previous = out
            self._callback(out)
        else:
            return False
        return self._should_update

    def _sup_draw(self, cr):
        pass
    
    def draw(self, cr):
    
        self._sup_draw(cr)
        
        if self.broken:
            resting_bar_color = self._broken_resting_bar_color
            active_bar_color = self._broken_active_bar_color
            resting_text_color = self._broken_resting_text_color
            active_text_color = self._broken_active_text_color
        else:
            resting_bar_color = self._resting_bar_color
            active_bar_color = self._active_bar_color
            resting_text_color = self._resting_text_color
            active_text_color = self._active_text_color
            
        fontsize = round(self.font.fontsize)
        
        cr.rectangle(self.x - 1, self.y - fontsize - 5, self.width + 2, fontsize + 15)
        cr.clip()
        if self._active:
            # print cursors
            cr.set_source_rgb(1, 0.2, 0.6)
            cr.rectangle(round(self._glyphs[self._i][1] - 1), 
                        self.y - fontsize, 
                        2, 
                        fontsize)
            cr.rectangle(round(self._glyphs[self._j][1] - 1), 
                        self.y - fontsize, 
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
                        self.y - fontsize,
                        abs(self._glyphs[self._i][1] - self._glyphs[self._j][1]),
                        fontsize)
                cr.fill()
                
        cr.set_font_size(self.font.fontsize)
        cr.set_font_face(self.font.font)
        if self._active:
            cr.set_source_rgba( * active_text_color)
        else:
            cr.set_source_rgba( * resting_text_color)
        # don't print the cap glyph
        cr.show_glyphs(self._glyphs[:-2])
        cr.reset_clip()
                
        if self.name is not None:
            cr.move_to(self.x, self.y + self.font.fontsize + 5)
            cr.set_font_size(11)
            cr.show_glyphs(self._label)
        
        if self._active:
            cr.set_source_rgba( * active_bar_color)
        else:
            cr.set_source_rgba( * resting_bar_color)
        cr.rectangle(self.x, self.y + 5, self.width, 1)
        cr.fill()

class Numeric_Field(Blank_Space):
    def __init__(self):
        pass

    def _entry(self):
        num = ''.join([c for c in self._text[:-1] if c in '1234567890.-'])

        return num
    
    def _to_number(self, string):
        if '.' in string:
            number = float(string)
        else:
            number = int(string)
        return number

    def _stamp_glyphs(self, factor=1):
        self._template = self._build_line(self.x, self.y, self._text, self.font, factor, sub_minus=True)

class Object_Menu(Blank_Space):
    def __init__(self, default, x, y, width, callback, menu_callback, name=None, update=False):
        # must be list
        self._text = default + [None]
        self._previous = ''.join(default)

        
        self._callback = callback
        self._menu_callback = menu_callback
        
        self._common(x, y, width, name, update)
    
    def focus(self, x):
        if x < self.x + self.width - 40:
            self._active = True
            self._i = self._target(x)
            self._j = self._i
            
            self._center_x(self._glyphs[self._j][1])
        else:
            self.defocus()
            self._menu_callback()
            self._active = True
            self._dropdown_active = True
            print('DROPDOWN')
    
    def _sup_draw(self, cr):
        if self._dropdown_active:
            cr.set_source_rgb(1, 0.2, 0.6)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        cr.move_to(self.x + self.width - 5, self.y - 7)
        cr.rel_line_to(8, 0)
        cr.rel_line_to(-4, 4*1.41)
        cr.close_path()
        cr.fill()
    
