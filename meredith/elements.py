from meredith.box import Box

class Fontpost(Box):
    name = '_f_'
    inline = True
    DNA = [('class', 'texttc', '_undefined_')]

    def copy(self):
        return self.__class__(self.attrs)

    def __eq__(self, other):
        return type(other) is self.__class__ and other['class'] == self['class']

class PosFontpost(Fontpost):
    name = 'fo'
    countersign = True
    def __str__(self):
        return '<fo/>'

class NegFontpost(Fontpost):
    name = 'fc'
    countersign = False
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
