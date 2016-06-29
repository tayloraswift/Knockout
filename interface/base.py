from fonts.interfacefonts import ISTYLES
from fonts import hb

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

def text(x, y, text, font, fontsize=None, align=1, sub_minus=False, upper=False, grid=False):    
    if fontsize is None:
        fontsize = font['fontsize']
    xo = x
    line = []
    tracking = font['tracking']
    
    if grid:
        if sub_minus:
            iter_l = ('–' if c == '-' else c for c in text)
        else:
            iter_l = text
        
        for character in iter_l:
            try:
                line.append((font['__gridfont__'].character_index(character), x, y))
                x += (font['__gridfont__'].advance_pixel_width(character)*fontsize + tracking)
            except TypeError:
                line.append((-1, x, y))
    else:
        if upper:
            text = text.upper()
        if sub_minus:
            text = text.replace('-', '–')
        
        HBB = hb.buffer_create()
        cp = list(map(ord, text))
        hb.buffer_add_codepoints(HBB, cp, 0, len(cp))
        hb.buffer_guess_segment_properties(HBB)
        hb.shape(font['__hb_font__'], HBB, [])
        factor = font['__factor__']
        for N, P in zip(hb.buffer_get_glyph_infos(HBB), hb.buffer_get_glyph_positions(HBB)):
            line.append((N.codepoint, x + P.x_offset*factor, y))
            x += P.x_advance*factor + tracking

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
