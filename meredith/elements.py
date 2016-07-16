from meredith.box import Box, random_serial
from meredith.styles import _text_DNA

font_serial_generator = random_serial()

class Fontpost(Box):
    name = '_f_'
    inline = True
    DNA = [('class', 'texttc', '')]

    def copy(self):
        return self.__class__(self.KT, self.attrs)

    def __eq__(self, other):
        return type(other) is self.__class__ and other['class'] == self['class']

class PosFontpost(Fontpost):
    name = 'fo'
    countersign = True
    
    fixed_attrs = {a[0] for a in _text_DNA}
    DNA = Fontpost.DNA + [A[:2] for A in _text_DNA]
    
    def __init__(self, * I , ** KI ):
        super().__init__( * I , ** KI )
        self.isbase = False
        self._update_hash()

    def _update_hash(self):
        if self.keys() & self.__class__.fixed_attrs:
            self.stylehash = next(font_serial_generator)
        else:
            self.stylehash = None
        
    def after(self, A):
        self._update_hash()
    
    def __str__(self):
        return '<fo/>'

class NegFontpost(Fontpost):
    name = 'fc'
    countersign = False
    
    DNA = Fontpost.DNA + [('pop', 'int', 0)]
    def __str__(self):
        return '<fc/>'

class Line_break(Box):
    name = 'br'
    inline = True

    def __str__(self):
        return '<br/>'

class Reverse(Box):
    name = 'reverse'
    inline = True
    DNA = [('language', 'language', None)]

members = (PosFontpost, NegFontpost, Line_break, Reverse)
