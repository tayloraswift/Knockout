from meredith import datablocks

from edit import cursor, caramel

from state import contexts

def reinitialize(kitty, deserialize):
        kttags, kbtags, kdocument, ktstyles, kbstyles = kitty
        TTAGS   = deserialize(kttags)[0]
        BTAGS   = deserialize(kbtags)[0]
        
        datablocks.TTAGS.__init__(TTAGS.attrs, TTAGS.content)
        datablocks.BTAGS.__init__(BTAGS.attrs, BTAGS.content)
        
        TSTYLES = deserialize(ktstyles)[0]
        datablocks.TSTYLES.__init__(TSTYLES.attrs, TSTYLES.content)
        
        BSTYLES = deserialize(kbstyles)[0]
        datablocks.BSTYLES.__init__(BSTYLES.attrs, BSTYLES.content)
        
        DOC     = deserialize(kdocument)[0]
        datablocks.DOCUMENT.__init__(DOC.attrs, DOC.content)
        datablocks.DOCUMENT.layout_all()
        
        contexts.Text.__init__()
        # don’t forget to run update_force and turnover_k on the cursor
        
class UN(object):
    def __init__(self, serialize, deserialize):
        self._history = []
        self._i = 0
        
        self._state = None
        
        self.serialize   = serialize
        self.deserialize = deserialize
    
    def save(self):
        
        if len(self._history) > 989:
            del self._history[:89]
            self._i -= 89

        if len(self._history) > self._i:
            del self._history[self._i:]
                
        kitty = [self.serialize([k]) for k in (datablocks.TTAGS, datablocks.BTAGS, datablocks.DOCUMENT, datablocks.TSTYLES, datablocks.BSTYLES)]
        DATA = (cursor.fcursor.plane_address[:], cursor.fcursor.i, cursor.fcursor.j), caramel.delight.at()

        self._history.append((kitty, DATA, contexts.Text.index_k()))
        self._i = len(self._history)
        
    def pop(self):
        del self._history[-1]
        self._i = len(self._history)
        
    def _restore(self, i):
        kitty, DATA, activity = self._history[i]
        
        reinitialize(kitty, self.deserialize)
        
        cursor.fcursor.initialize_from_params ( * DATA[0] )
        caramel.delight.initialize_from_params( * DATA[1] )
        
        contexts.Text.update_force()
        contexts.Text.turnover_k( * activity )
    
    def back(self):
        if self._i > 0:
            if self._i == len(self._history):
                self.save()
                self._i -= 1
            
            self._i -= 1
            self._restore(self._i)
            
            return True
        else:
            print('No steps to undo')
            self._state = -89
            return False
    
    def forward(self):
        try:
            self._restore(self._i + 1)
            self._i += 1
            
            return True
        except IndexError:
            print('No steps to redo')
            self._state = -89
            return False

    # prevents excessive savings
    def undo_save(self, state):
        if state != self._state or state == 3:
            if self._state != 0:
                self.save()
            self._state = state

