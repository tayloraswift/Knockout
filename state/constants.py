accent = (1, 0.22, 0.50)
accent_light = (1, 0.22, 0.55)

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

shortcuts =    [('Ctrl 6', 'Ctrl asciicircum', 'small^sup'),
                ('Ctrl 7', 'Ctrl ampersand', 'small^sub'),
                ('Ctrl b', 'Ctrl B', 'strong'),
                ('Ctrl i', 'Ctrl I', 'emphasis'),
                ('Ctrl grave', 'Ctrl asciitilde', 'code'),
                ]

interface_tstyles = {'_interface:LABEL'  : {'fontsize'  : 11,
                                            'path'      : 'interface/FiraSans-Book.otf',
                                            'tracking'  : 1},
                     '_interface:REGULAR': {'color'     : (0, 0, 0, 1),
                                            'fontsize'  : 13.5,
                                            'path'      : 'interface/FiraSans-Book.otf'},
                     '_interface:ITALIC' : {'path'      : 'interface/FiraSans-BookItalic.otf'},
                     '_interface:STRONG' : {'path'      : 'interface/FiraSans-Medium.otf'},
                     '_interface:TITLE'  : {'fontsize'  : 18, 'tracking': 4},
                     '_interface:SPLASH' : {'fontsize'  : 36, 'tracking': 0},
                     '_interface:CODE'   : {'path'      : 'interface/Share-TechMono.otf', 'fontsize': 16}}

interface_bstyle =   [('_interface:REGULAR' , ()            ),
                      ('_interface:LABEL'   , ('label',)    ),
                      ('_interface:ITALIC'  , ('emphasis',) ),
                      ('_interface:STRONG'  , ('strong',)   ),
                      ('_interface:TITLE'   , ('title',)    ),
                      ('_interface:SPLASH'  , ('splash',)   ),
                      ('_interface:CODE'    , ('mono',)     )]
