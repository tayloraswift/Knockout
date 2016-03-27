from ast import literal_eval

from style.styles import Paragraph_style, cast_parastyle, PTAGS
from bulletholes.counter import TCounter as Counter
from IO.xml import count_styles, print_attrs, print_styles
from elements.node import Inline_element, Block_element

class Paragraph(object):
    def __init__(self, counts, element=None):
        self.P = counts
        if element is None:
            self.EP = Paragraph_style()
        else:
            self.EP = element
        self.I_ = None
    
    @classmethod
    def from_attrs(cls, attrs):
        if 'class' in attrs:
            ptags = Counter({PTAGS[T.strip()]: V for T, V in count_styles(attrs['class'])})
        else:
            ptags = Counter({PTAGS['body']: 1})
        if 'style' in attrs:
            EP = cast_parastyle(literal_eval(attrs['style']))
        else:
            EP = None
        return cls(ptags, EP)
    
    def __str__(self):
        return '<p>'
    
    def __repr__(self):
        attrs = print_styles(self)
        return '<' + print_attrs('p', attrs) + '>'

    def __len__(self):
        return 3


class _Fontpost(Inline_element):
    textfacing = True
    ADNA = [('class', '_undefined_', 'ftag')]
    
    def _load(self):
        self.F = self['class']
        self.attrs['class'] = self.F

    def __eq__(self, other):
        return type(other) is self.__class__ and other.F is self.F

class OpenFontpost(_Fontpost):
    name = 'fo'
    def __str__(self):
        return '<fo/>'

    def __len__(self):
        return 5

class CloseFontpost(_Fontpost):
    name = 'fc'
    def __str__(self):
        return '<fc/>'

    def __len__(self):
        return 5
    
members = [OpenFontpost, CloseFontpost]
inline = True
