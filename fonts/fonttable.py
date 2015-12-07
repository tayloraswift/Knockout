import freetype

from fonts import pycairo_font
from fonts import fonts

_type_registry = {}

def _get_cairo_font(path):
    if path not in _type_registry:
        _type_registry[path] = pycairo_font.create_cairo_font_face_for_file(path)
    
    return _type_registry[path]


# extended fontface class
class _FFace(freetype.Face):
    
    def __init__(self, path):
        freetype.Face.__init__(self, path)
        
        self._widths = {
                None: 0
                }
        
        self._ordinals = {
                }
    
    def advance_pixel_width(self, character):
        try:
            return self._widths[character]
        except KeyError:
            p = self.get_advance(self.get_char_index(character), True)/self.units_per_EM
            self._widths[character] = p
            return p
    
    def character_index(self, character):
        try:
            return self._ordinals[character]
        except KeyError:
            i = self.get_char_index(character)
            self._ordinals[character] = i
            return i
    
    
class _Font_table(object):
    def __init__(self):
        self._table = {}

    def get_font(self, p, f):

        if (p, f) not in self._table:

            properties = {}
            
            properties['path'] = fonts.f_get_attribute('path', p, f)[1]
            properties['fontsize'] = fonts.f_get_attribute('fontsize', p, f)[1]
            properties['tracking'] = fonts.f_get_attribute('tracking', p, f)[1]
            
            properties['path_valid'] = True
            
    #        print(properties['path'])
            try:
                properties['fontmetrics'] = _FFace(properties['path'])
                properties['font'] = _get_cairo_font(properties['path'])
            except freetype.ft_errors.FT_Exception:
                pth = fonts.f_get_attribute('path', ('P', '_interface'), () )[1]
                properties['fontmetrics'] = _FFace(pth)
                properties['font'] = _get_cairo_font(pth)
                
                properties['path_valid'] = False
            
            self._table[(p, f)] = properties
    
        return self._table[(p, f)]

    def clear(self):
        self._table = {}

class _Paragraph_table(object):
    def __init__(self):
        self._table = {}

    def get_paragraph(self, p):

        if p not in self._table:

            properties = {}
            
            properties['leading'] = fonts.p_get_attribute('leading', p)[1]
            properties['margin_top'] = fonts.p_get_attribute('margin_top', p)[1]
            properties['margin_bottom'] = fonts.p_get_attribute('margin_bottom', p)[1]
            properties['margin_left'] = fonts.p_get_attribute('margin_left', p)[1]
            properties['margin_right'] = fonts.p_get_attribute('margin_right', p)[1]
#            properties['indent'] = fonts.p_get_attribute('indent', p)[1]
            properties['hyphenate'] = fonts.p_get_attribute('hyphenate', p)[1]
            
            # temporary (file compatibility)
            ir = fonts.p_get_attribute('indent_range', p)[1]
            if ir == 0:
                properties['indent_range'] = (0, )
            else:
                properties['indent_range'] = ir

            cc = fonts.p_get_attribute('indent', p)[1]
            if not isinstance(cc, tuple):  #  C  ±  K
                properties['indent'] = (0, 1, 0)
            else:
                properties['indent'] = cc

            
            self._table[p] = properties
    
        return self._table[p]

    def clear(self):
        self._table = {}

table = _Font_table()
p_table = _Paragraph_table()

def glyph_width(fontmetrics, size, c):
    return fontmetrics.advance_pixel_width(c)*size
