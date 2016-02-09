from itertools import chain
from cairo import ImageSurface

textstyles = {'emphasis': 'em', 'strong': 'strong', 'sup': 'sup', 'sub': 'sub'}

class Paragraph(object):
    def __init__(self, counts, element={}):
        self.P = counts
        self.EP = element
    
    def __str__(self):
        return '<p>'
    
    def __repr__(self):
        ptags = '&'.join(chain.from_iterable((P.name for i in range(V)) for P, V in self.P.items()))
        if ptags == 'body' and self.EP is None:
            return '<p>'
        elif not self.EP:
            return '<p class="' + ptags + '">'
        else:
            return '<p class="' + ptags + '" style="' + repr(self.EP.polaroid()[0]) + '">'

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
        if self.F.name in textstyles:
            return '<' + textstyles[self.F.name] + '>'
        else:
            return '<f class="' + self.F.name + '">'

    def __len__(self):
        return 3

class CloseFontpost(_Fontpost):
    def __str__(self):
        return '</f>'

    def __repr__(self):
        if self.F.name in textstyles:
            return '</' + textstyles[self.F.name] + '>'
        else:
            return '</f class="' + self.F.name + '">'

    def __len__(self):
        return 4

class Image(object):
    def __init__(self, src, width):
        self.src = src
        self.width = width

        # cache image surface creation
        self.image_surface = ImageSurface.create_from_png(src)
        self.factor = width / self.image_surface.get_width()

    def __str__(self):
        return '<image>'

    def __repr__(self):
        return '<image src="' + self.src + '" width=' + str(self.width) + ' />'

    def __len__(self):
        return 7
