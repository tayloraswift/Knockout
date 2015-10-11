import freetype
import pycairo_font

import fonts

ordinalmap = {
        'other': -1,
        '<br>': -2,
        '<p>': -3,
        '</p>': -4,
        
        '<f>': -5,
        '</f>': -6
        }

_type_registry = {}

def _get_cairo_font(path):
    if path not in _type_registry:
        _type_registry[path] = pycairo_font.create_cairo_font_face_for_file(path)
    
    return _type_registry[path]


# extended fontface class
class _FFace(freetype.Face):
    
    def advance_width(self, character):
        if len(character) == 1:
            avw = self.get_advance(self.get_char_index(character), True)
        elif character == '<br>':
            avw = 0
        elif character == '<p>':
            avw = 0
        
        elif character in ['<f>', '</f>']:
            avw = 0
        else:
            avw = 1000
            
        return avw

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
                pth = fonts.f_get_attribute('path', '_interface', () )[1]
                properties['fontmetrics'] = _FFace(pth)
                properties['font'] = _get_cairo_font(pth)
                
                properties['path_valid'] = False
            
            self._table[(p, f)] = properties
    
        return self._table[(p, f)]

    def clear(self):
        self._table = {}

table = _Font_table()

def character_index(fontmetrics, c):
    try:
        return (fontmetrics.get_char_index(c))
    except TypeError:
        return ordinalmap[c]

def glyph_width(fontmetrics, size, c):
    return fontmetrics.advance_width(c)/fontmetrics.units_per_EM*size
