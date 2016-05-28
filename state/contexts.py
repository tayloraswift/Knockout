from meredith import datablocks

from edit import cursor, caramel

from state import noticeboard

class Text_context(object):
    def __init__(self):
        self.bk = None
        self.bs = None
        self.ts = None
        self.char = None
        
        self.sc = None
        self.c = None
        
        self.kbt = None
        self.ktt = None
        self.kbs = None
        self.kbm = None
        
        self.changed = set()

    def done(self, U):
        if U in self.changed:
            self.changed.remove(U)

    def update(self):
        BLOCK, TEXTSTYLE = cursor.fcursor.styling_at()
        C = cursor.fcursor.at()
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

    def update_frames(self):
        sc, c = caramel.delight.at()
        if sc != self.sc:
            self.changed.update({'frames', 'section'})
            self.c = c
            self.sc = sc
        elif c != self.c:
            self.changed.update({'frames'})
            self.c = c

    def update_force(self):
        BLOCK, TEXTSTYLE = cursor.fcursor.styling_at()
        C = cursor.fcursor.at()
        
        self.changed.update({'paragraph'})
        self.bk = BLOCK
        self.bs = datablocks.BSTYLES.project_b(BLOCK)
    
        self.changed.update({'font'})
        self.ts = TEXTSTYLE
    
        self.changed.update({'character'})
        self.char = C
        
        self.sc, self.c = caramel.delight.at()
        self.changed.update({'frames'})

    def push_active(self, A, node):
        if A == 'kbs':
            self.kbs = node
            self.changed.update({'paragraph'})
        elif A == 'kbm':
            self.kbm = node
            self.changed.update({'font'})
        elif A == 'kbt':
            self.kbt = node
            self.changed.update({'tags'})
        elif A == 'ktt':
            self.ktt = node
            self.changed.update({'tags'})
        else:
            raise NotImplementedError
    
    def index_k(self):
        try:
            kbs = datablocks.BSTYLES.content.index(self.kbs)
        except ValueError:
            return None, None
        try:
            kbm = self.kbs.content.index(self.kbm)
        except ValueError:
            return kbs, None
        return kbs, kbm
    def turnover_k(self, kbs, kbm):
        if kbs is not None:
            kbs_O = datablocks.BSTYLES.content[kbs]
            self.push_active('kbs', kbs_O)
            
            if kbm is not None:
                kbm_O = kbs_O.content[kbm]
                self.push_active('kbm', kbm_O)
        
Text = Text_context()
