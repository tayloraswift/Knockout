filename = ''

UI = [0, 950]

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

window = Window(1300, 800)

shortcuts = [('Ctrl equal', 'Ctrl plus', 'small^sup'),
        ('Ctrl minus', 'Ctrl underscore', 'small^sub'),
        ('Ctrl b', 'Ctrl B', 'strong'),
        ('Ctrl i', 'Ctrl I', 'emphasis')
        ]

interface_fstyles = {'_interface:LABEL': {'fontsize': 11,
                                     'path': 'interface/FiraSans-Book.otf',
                                     'tracking': 1},
                '_interface:REGULAR': {'color': (0, 0, 0, 1),
                                       'fontsize': 13.5,
                                       'path': 'interface/FiraSans-Book.otf',
                                       'tracking': 0},
                '_interface:STRONG': {'path': 'interface/FiraSans-Medium.otf',
                                      'tracking': 0.5},
                '_interface:TITLE': {'fontsize': 18, 'tracking': 4},
                '_interface:CODE': {'path': 'interface/Share-TechMono.otf', 'fontsize': 16}}

interface_pstyle = [('_interface:REGULAR', ()),
                          ('_interface:LABEL', ('label',)),
                          ('_interface:STRONG', ('strong',)),
                          ('_interface:TITLE', ('title',)),
                          ('_interface:CODE', ('mono',))]
