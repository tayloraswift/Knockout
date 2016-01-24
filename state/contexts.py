from fonts import styles
from model import meredith
from state import noticeboard

class Text_context(object):
    def __init__(self):
        self._previous_p = None
        self._previous_pi = None
        self._previous_t = None
        self._FSTYLE = None
        self.update()
    def update(self):
        self.tract = meredith.mipsy.tracts[0]
        PP, FSTYLE = self.tract.styling_at()
        P, P_i = PP
        if P_i != self._previous_pi or self.tract is not self._previous_t:
            print('update paragraph context')
            self.paragraph =  self.tract.text[P_i]
            self._previous_pi = P_i
            self._previous_t = self.tract
            
            if P is not self._previous_p:
                print('update parastyle context')
                self._previous_p = P
                Parastyle.update(self.paragraph[1])
                noticeboard.refresh_properties_stack.push_change()

        if self._FSTYLE is not FSTYLE:
            print('update font context')
            self._FSTYLE = FSTYLE
            Fontstyle.update(FSTYLE)
            noticeboard.refresh_properties_stack.push_change()

    def update_force(self):
        self.tract = meredith.mipsy.tracts[0]
        PP, self._FSTYLE = self.tract.styling_at()
        P, P_i = PP
        self.paragraph =  self.tract.text[P_i]
        self._previous_pi = None
        self._previous_t = self.tract
        self._previous_p = None
        Parastyle.update(self.paragraph[1])
        Fontstyle.update(self._FSTYLE)
        noticeboard.refresh_properties_stack.push_change()

class Paragraph_context(object):
    def __init__(self):
        pass
    def update(self, P):
        self.parastyle = styles.PARASTYLES.project_p(P)

class Font_context(object):
    def __init__(self):
        pass
    
    def update(self, FSTYLE):
        self.fontstyle = FSTYLE

Fontstyle = Font_context()
Parastyle = Paragraph_context()
Text = Text_context()
