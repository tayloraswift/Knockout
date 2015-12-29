import freetype

from fonts import pycairo_font

_type_registry = {}

def get_cairo_font(path):
    if path not in _type_registry:
        _type_registry[path] = pycairo_font.create_cairo_font_face_for_file(path)
    
    return _type_registry[path]

# extended fontface class
class Memo_font(freetype.Face):
    
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
