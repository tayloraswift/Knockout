from fonts import styles
from model import meredith
from state import noticeboard

class Tag_context(object):
    def __init__(self):
        self.update()

    def update(self):
        self.tag = styles.TAGLIST.ordered[styles.TAGLIST.active]

#############

class Text_context(object):
    def __init__(self):
        self._previous_p = None
        self._previous_pi = None
        self._previous_t = None
        self.update()
    def update(self):
        self.tract = meredith.mipsy.tracts[0]
        P, P_i = meredith.mipsy.paragraph_at()
        if P_i is not self._previous_pi or self.tract is not self._previous_t:
            print('update paragraph context')
            self.paragraph =  self.tract.text[P_i]
            self._previous_pi = P_i
            self._previous_t = self.tract
            
            if P is not self._previous_p:
                print('update parastyle context')
                self._previous_p = P
                Parastyle.update(self.paragraph[1])
                noticeboard.refresh_properties_stack.push_change()

    def update_force(self):
        self.tract = meredith.mipsy.tracts[0]
        P, P_i = meredith.mipsy.paragraph_at()
        self.paragraph =  self.tract.text[P_i]
        self._previous_pi = P_i
        self._previous_t = self.tract
        self._previous_p = P
        Parastyle.update(self.paragraph[1])
        noticeboard.refresh_properties_stack.push_change()

class Paragraph_context(object):
    def __init__(self):
        pass
    
    def update(self, P):
        self.parastyle = P
        Keymap.update(self.parastyle.fontclasses)

class Keymap_context(object):
    def __init__(self):
        pass
    
    def update(self, M):
        self.keymap = M
        try:
            Fontstyle.update(self.keymap.elements[self.keymap.active])
        except IndexError:
            Fontstyle.update(None)

class Font_context(object):
    def __init__(self):
        pass
    
    def update(self, F=None):
        if F is not None:
            self.fontstyle = F
        else:
            try:
                self.fontstyle = Keymap.keymap.elements[Keymap.keymap.active]
            except IndexError:
                self.fontstyle = None
        Pegs.update()

class Pegs_context(object):
    def __init__(self):
        pass
    
    def update(self, G=None):
        if G is not None:
            self.pegs = G
        else:
            try:
                self.pegs = Fontstyle.fontstyle.pegs
            except AttributeError:
                self.pegs = None

Pegs = Pegs_context()
Fontstyle = Font_context()
Keymap = Keymap_context()
Parastyle = Paragraph_context()
Text = Text_context()

Tag = Tag_context()
