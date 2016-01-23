import cairo

HINTS = cairo.FontOptions()

def default_hints():
    return [(0, 'Default'), (1, 'None'), (2, 'Slight'), (3, 'Medium'), (4, 'Strong')]

def default_antialias():
    return [(0, 'Default'), (1, 'None'), (2, 'Grayscale'), (3, 'Subpixel')]

default_hint = default_hints()[1]
HINTS.set_hint_style(default_hint[0])

filename = ''

UI = [0, 900]

class Window(object):
    def __init__(self, h, k):
        self.h = h
        self.k = k
    def get_k(self):
        return self.k
    
    def get_h(self):
        return self.h
    
    def resize(self, h, k):
        self.h = h
        self.k = k

window = Window(1200, 800)


interface_fstyles = {'_interface:LABEL': {'fontsize': 11,
                                     'path': 'interface/FiraSans-Book.otf',
                                     'tracking': 1},
                '_interface:REGULAR': {'color': (0, 0, 0, 1),
                                       'fontsize': 13.5,
                                       'path': 'interface/FiraSans-Book.otf',
                                       'tracking': 0},
                '_interface:STRONG': {'path': 'interface/FiraSans-Medium.otf',
                                      'tracking': 0.5},
                '_interface:TITLE': {'fontsize': 18, 'tracking': 4}}

interface_pstyle = [((), '_interface:REGULAR'),
                          (('label',), '_interface:LABEL'),
                          (('strong',), '_interface:STRONG'),
                          (('title',), '_interface:TITLE')]
