from itertools import chain
from fonts import styles

class Paragraph(object):
    def __init__(self, counts):
        self.P = counts
    
    def __str__(self):
        return '<p>'
    
    def __repr__(self):
        ptags = '&'.join(chain.from_iterable((P.name for i in range(V)) for P, V in self.P.items()))
        if ptags == 'body':
            return '<p>'
        else:
            return '<p class="' + ptags + '">'

    def __len__(self):
        return 3

class _Fontpost(object):
    def __init__(self, F):
        self.F = F

    def __eq__(self, other):
        return type(other) is self.__class__ and other.F is self.F

class OpenFontpost(_Fontpost):
    def __str__(self):
        return '<f>'

    def __repr__(self):
        if self.F.name == 'emphasis':
            return '<em>'
        elif self.F.name == 'strong':
            return '<strong>'
        else:
            return '<f class="' + self.F.name + '">'

    def __len__(self):
        return 3

class CloseFontpost(_Fontpost):
    def __str__(self):
        return '</f>'

    def __repr__(self):
        if self.F.name == 'emphasis':
            return '</em>'
        elif self.F.name == 'strong':
            return '</strong>'
        else:
            return '</f class="' + self.F.name + '">'

    def __len__(self):
        return 4

class Image(object):
    def __init__(self, src, width):
        self.src = src
        self.width = width

    def __str__(self):
        return '<image>'

    def __repr__(self):
        return '<image src="' + self.src + '" width="' + str(self.width) + '">'

    def __len__(self):
        return 7

class FTable(object):
    pass
