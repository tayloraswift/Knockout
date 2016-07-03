from random import randint

from meredith.box import Box
from meredith.styles import _text_DNA

class Fontpost(Box):
    name = '_f_'
    inline = True
    DNA = [('class', 'texttc', '')]

    def copy(self):
        return self.__class__(self.attrs)

    def __eq__(self, other):
        return type(other) is self.__class__ and other['class'] == self['class']

class PosFontpost(Fontpost):
    name = 'fo'
    countersign = True
    isbase = False
    
    DNA = Fontpost.DNA + [A[:2] for A in _text_DNA]
    
    def __init__(self, * I , ** KI ):
        super().__init__( * I , ** KI )
        self.after('__attrs__')
    
    def after(self, A):
        self.hash = randint(0, 1989000000)
    
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
