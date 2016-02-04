class Paragraph(object):
    def __init__(self, counts):
        self.P = counts
    
    def __str__(self):
        return '<p>'

    def __len__(self):
        return 3

class OpenFontpost(object):
    def __init__(self, F):
        self.F = F

    def __str__(self):
        return '<f>'

    def __len__(self):
        return 3
    
    def __eq__(self, other):
        return type(other) is self.__class__ and other.F is self.F
            

class CloseFontpost(object):
    def __init__(self, F):
        self.F = F

    def __str__(self):
        return '</f>'

    def __len__(self):
        return 4

    def __eq__(self, other):
        return type(other) is self.__class__ and other.F is self.F

class Image(object):
    def __init__(self, src, width):
        self.src = src
        self.width = width

    def __str__(self):
        return '<image>'

    def __len__(self):
        return 7

class FTable(object):
    pass
