from model import meredith

class Text_context(object):
    def __init__(self):
        self.update()
    def update(self):
        self.tract = meredith.mipsy.tracts[0]
        self.paragraph =  self.tract.text[meredith.mipsy.paragraph_at()[1]]
        Parastyle.update(self.paragraph[1])
    
    def update_p(self, p):
        self.paragraph = self.tract.text[p[1]]
        Parastyle.update(self.paragraph[1])

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

Fontstyle = Font_context()
Keymap = Keymap_context()
Parastyle = Paragraph_context()
Text = Text_context()
