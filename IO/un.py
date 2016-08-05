class UN(object):
    def __init__(self):
        self._history   = []
        self._secondary = []
        
        self.pop = self._history.pop
    
    def reset(self, KT, context, panes):
        del self._history[:]
        del self._secondary[:]
        self._state = None
        
        self.serialize   = KT.miniserialize
        self.deserialize = KT.deserialize_high
        
        self.KT          = KT
        self.shortcuts()
        self.pcursor     = KT.PCURSOR
        self.scursor     = KT.SCURSOR
        self.context     = context
        
        self.panes = panes
    
    def shortcuts(self):
        KT = self.KT
        self.TTAGS       = KT.TTAGS
        self.BTAGS       = KT.BTAGS
        self.BODY        = KT.BODY
        self.TSTYLES     = KT.TSTYLES
        self.BSTYLES     = KT.BSTYLES
    
    def save(self):
        if len(self._history) > 989:
            del self._history[:-89]

        if self._secondary:
            del self._secondary[:]
        
        self._history.append(self.record())
    
    def record(self):
        kitty = self.serialize((self.TTAGS, self.BTAGS, self.BODY, self.TSTYLES, self.BSTYLES))
        DATA  = (self.pcursor.plane_address[:], self.pcursor.i, self.pcursor.j), self.scursor.at()
        return kitty, DATA, self.context.index_k()
    
    def _restore(self, record):
        kitty, DATA, activity = record
        print(DATA, activity)
        self.deserialize(kitty)
        self.shortcuts()
        self.BODY.layout_all()
        
        self.pcursor.reactivate(DATA[0])
        self.scursor.reactivate(DATA[1])
        self.context.__init__(self.KT)
        self.context.turnover_k( * activity )
        
        self.panes.shortcuts()
    
    def back(self):
        if self._history:
            self._secondary.append(self.record())
            self._restore(self._history.pop())
        else:
            print('No steps to undo')
            self._state = -89
    
    def forward(self):
        if self._secondary:
            self._history.append(self.record())
            self._restore(self._secondary.pop())
        else:
            print('No steps to redo')
            self._state = -89

    # prevents excessive savings
    def undo_save(self, state):
        if state != self._state or state == 3:
            if self._state != 0:
                self.save()
            self._state = state

history = UN()
