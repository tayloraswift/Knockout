from fonts.interfacefonts import ISTYLES

# shapes
def plus_sign(cr, x, y):
    # w = 26
    cr.rectangle(x + 12, y + 8, 2, 10)
    cr.rectangle(x + 8, y + 12, 10, 2)

def minus_sign(cr, x, y):
    # w = 26
    cr.rectangle(x + 8, y + 12, 10, 2)

def downchevron(cr, x, y):
    # w = 24
    cr.move_to(x + 7, y + 10)
    cr.rel_line_to(5, 5)
    cr.rel_line_to(5, -5)

def upchevron(cr, x, y):
    # w = 24
    cr.move_to(x + 7, y + 15)
    cr.rel_line_to(5, -5)
    cr.rel_line_to(5, 5)

def cross(cr, x, y):
    # w = 24
    cr.move_to(x + 8, y + 9)
    cr.rel_line_to(8, 8)
    cr.rel_move_to(0, -8)
    cr.rel_line_to(-8, 8)

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

def set_fonts(cr, font, fontsize):
    cr.set_font_face(font)
    cr.set_font_size(fontsize)

def show_text(cr, textline):
    * F, T = textline
    set_fonts(cr, * F)
    cr.show_glyphs(T)

class Kookie(object):
    def __init__(self, x, y, width, height):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        
        self._active = None
        
        self._x_right = x + width
        self.y_bottom = y + height
    
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
