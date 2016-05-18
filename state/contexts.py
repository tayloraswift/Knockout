from elements import datablocks
from edit import cursor, caramel
from state import noticeboard

class Text_context(object):
    def __init__(self):
        self.bk = None
        self.bs = None
        self.ts = None
        self.char = None
        
        self.ct = None
        self.c = None
        
        self.changed = set()

    def done(self, U):
        if U in self.changed:
            self.changed.remove(U)

    def update(self):
        BLOCK, TEXTSTYLE = cursor.fcursor.styling_at()
        C = cursor.fcursor.char(cursor.fcursor.i)
        
        if BLOCK is not self.bk:
            self.changed.update({'paragraph'})
            self.bk = BLOCK
            self.bs = datablocks.BSTYLES.project_b(BLOCK)
        
        if TEXTSTYLE != self.ts:
            self.changed.update({'font'})
            self.ts = TEXTSTYLE
        
        if C is not self.char:
            self.changed.update({'character'})
            self.char = C

    def update_channels(self):
        ct, c = caramel.delight.at()
        if c != self.c or ct is not self.ct:
            self.changed.update({'channels'})
            self.c = c
            self.ct = ct

    def update_force(self):
        BLOCK, TEXTSTYLE = cursor.fcursor.styling_at()
        C = cursor.fcursor.char(cursor.fcursor.i)
        
        self.changed.update({'paragraph'})
        self.bk = BLOCK
        self.bs = datablocks.BSTYLES.project_b(BLOCK)
    
        self.changed.update({'font'})
        self.ts = TEXTSTYLE
    
        self.changed.update({'character'})
        self.char = C
        
        self.ct, self.c = caramel.delight.at()
        self.changed.update({'channels'})

Text = Text_context()
