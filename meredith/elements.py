from meredith.box import Box

class _Fontpost(Box):
    name = '_f_'
    inline = True
    DNA = [('class', 'texttc', '_undefined_')]

    def copy(self):
        return self.__class__(self.attrs)

    def __eq__(self, other):
        return type(other) is self.__class__ and other['class'] == self['class']

class PosFontpost(_Fontpost):
    name = 'fo'
    def __str__(self):
        return '<fo/>'

class NegFontpost(_Fontpost):
    name = 'fc'
    def __str__(self):
        return '<fc/>'

class Line_break(Box):
    name = 'br'
    inline = True

members = (PosFontpost, NegFontpost, Line_break)
