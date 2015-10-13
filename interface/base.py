from math import floor

from state import constants

from fonts import fonttable

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

