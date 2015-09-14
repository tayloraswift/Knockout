import freetype
import pycairo_font

ordinalmap = {
        'other': -1,
        '<br>': -2,
        '<p>': -3,
        '</p>': -4,
        
        '<f>': -5,
        '</f>': -6
        }

_type_registry = {}

def get_cairo_font(path):
    if path not in _type_registry:
        _type_registry[path] = pycairo_font.create_cairo_font_face_for_file(path)
    
    return _type_registry[path]


# extended fontface class
class FFace(freetype.Face):
    
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
        
        
class TypeClass(object):
    def __init__(self, path, fontsize, tracking = 0):
        self.path = path
        self.path_valid = True
        
        self.fontface = FFace(path)
        self.fontsize = fontsize
        
        self.tracking = tracking
        
        self.font = get_cairo_font(self.path)
    
    def character_index(self, c):
        try:
            return (self.fontface.get_char_index(c))
        except TypeError:
            return ordinalmap[c]
    
    def glyph_width(self, c):
        return self.fontface.advance_width(c)/self.fontface.units_per_EM*self.fontsize
    
    def update_path(self, path):
        self.path = path
        self.fontface = FFace(path)
        
        self.font = get_cairo_font(self.path)
    
    def update_size(self, size):
        self.fontsize = size
    
    def update_tracking(self, tracking):
        self.tracking = tracking


class ParagraphClass(object):
    def __init__(self, leading, margin_bottom):
        self.fontclasses = {}
        self.leading = leading
        self.margin_bottom = margin_bottom

    def update_leading(self, leading):
        self.leading = leading

    def update_margin(self, margin):
        self.margin_bottom = margin
            
    def replace_fontclass(self, names, fontclass):
        self.fontclasses[names] = fontclass



_interface_class = ParagraphClass(16, 5)
_interface_class.replace_fontclass((), TypeClass('/home/kelvin/.fonts/NeueFrutiger45.otf', 13, tracking=0.5))
_interface_class.replace_fontclass(('strong',), TypeClass('/home/kelvin/.fonts/NeueFrutiger65.otf', 13, tracking=1))
_interface_class.replace_fontclass(('title',), TypeClass('/home/kelvin/.fonts/NeueFrutiger45.otf', 18, tracking=4))

_h1_class = ParagraphClass(28, 10)
_h1_class.replace_fontclass((), TypeClass("/home/kelvin/.fonts/NeueFrutiger45.otf", 18))
_h1_class.replace_fontclass(('caption',), TypeClass("/home/kelvin/.fonts/NeueFrutiger45.otf", 15))
_h1_class.replace_fontclass(('emphasis',), TypeClass("/home/kelvin/.fonts/NeueFrutiger45Italic.otf", 18))
_h1_class.replace_fontclass(('strong',), TypeClass("/home/kelvin/.fonts/NeueFrutiger65.otf", 18))
_h1_class.replace_fontclass(('emphasis', 'strong'), TypeClass("/home/kelvin/.fonts/NeueFrutiger65Italic.otf", 18))

_body_class = ParagraphClass(20, 5)
_body_class.replace_fontclass((), TypeClass("/home/kelvin/.fonts/Proforma-Book.otf", 15))
_body_class.replace_fontclass(('caption',), TypeClass("/home/kelvin/.fonts/NeueFrutiger45.otf", 13))
_body_class.replace_fontclass(('emphasis',), TypeClass("/home/kelvin/.fonts/Proforma-BookItalic.otf", 15))
_body_class.replace_fontclass(('strong',), TypeClass("/home/kelvin/.fonts/Proforma-Bold.otf", 15))
_body_class.replace_fontclass(('emphasis', 'strong',), TypeClass("/home/kelvin/.fonts/Proforma-BoldItalic.otf", 15))

_q_class = ParagraphClass(20, 5)
_q_class.replace_fontclass((), TypeClass("/home/kelvin/.fonts/Proforma-BookItalic.otf", 15))
_q_class.replace_fontclass(('caption',), TypeClass("/home/kelvin/.fonts/NeueFrutiger45.otf", 13))
_q_class.replace_fontclass(('emphasis',), TypeClass("/home/kelvin/.fonts/Proforma-Book.otf", 15))
_q_class.replace_fontclass(('strong',), TypeClass("/home/kelvin/.fonts/Proforma-BoldItalic.otf", 15))
_q_class.replace_fontclass(('emphasis', 'strong',), TypeClass("/home/kelvin/.fonts/Proforma-Bold.otf", 15))

paragraph_classes = {'_interface': _interface_class,
        'body': _body_class,
        'quotation': _q_class,
        'h1': _h1_class
        }

print(paragraph_classes['body'].leading)
