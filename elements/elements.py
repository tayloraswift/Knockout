from elements.box import Box

class _Fontpost(Box):
    name = '_f_'
    inline = True
    DNA = [('class', 'texttc', '_undefined_')]

#    def __eq__(self, other):
#        return type(other) is self.__class__ and other.F is self.F

class PosFontpost(_Fontpost):
    name = 'fo'
    def __str__(self):
        return '<fo/>'

class NegFontpost(_Fontpost):
    name = 'fc'
    def __str__(self):
        return '<fc/>'

members = (PosFontpost, NegFontpost)
