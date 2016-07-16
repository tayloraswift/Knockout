from itertools import chain

from meredith.paragraph import Paragraph_block, Text

from IO import un

class Keyboard(dict):
    def __init__(self, KT, shortcuts):
        self.cursor = KT.PCURSOR
        _OPEN = set(k[0] for k in shortcuts)
        self._CLOSE = set(k[1] for k in shortcuts)
        self._special_names = set(_OPEN) | set(self._CLOSE)
        
        dict.__init__(self, chain.from_iterable(((key1, name), (key2, name)) for key1, key2, name in shortcuts))
        
    def type_document(self, name, char):
        CURSOR = self.cursor.i
        
        # Non replacing
        if name == 'Left':
            un.history.undo_save(0)
            self.cursor.i = self.cursor.increment_cursor(CURSOR, -1)
            self.cursor.j = self.cursor.i
                
        elif name == 'Right':
            un.history.undo_save(0)
            self.cursor.i = self.cursor.increment_cursor(CURSOR, 1)
            self.cursor.j = self.cursor.i
            
        elif name == 'Up':
            un.history.undo_save(0)
            
            self.cursor.hop(-1)
            
        elif name == 'Down':
            un.history.undo_save(0)
            
            self.cursor.hop(1)

        elif name in ['Home', 'End']:
            un.history.undo_save(0)
            self.cursor.home_end(name == 'End')

        elif name == 'All':
            un.history.undo_save(0)
            
            self.cursor.expand_cursors()
        
        # replacing
        elif name in ['BackSpace', 'Delete']:
            if self.cursor.i != self.cursor.j:
                un.history.undo_save(3)
                self.cursor.delete()
            elif name == 'BackSpace':            
                un.history.undo_save(-1)
                self.cursor.delete(da=-1)
            else:
                un.history.undo_save(-1)
                self.cursor.delete(db=1)
        
        elif name == 'paragraph':
            un.history.undo_save(2)
            P1 = self.cursor.PLANE.content[CURSOR[0]]
            if len(CURSOR) == 2:
                P = P1.copy_empty()
                self.cursor.insert([P, P])
            else:
                P0 = self.cursor.PLANE.content[max(0, CURSOR[0] - 1)]
                if isinstance(P0, Paragraph_block):
                    P = P0.copy_empty()
                elif isinstance(P1, Paragraph_block):
                    P = P1.copy_empty()
                else:
                    P = Paragraph_block({}, Text())
                self.cursor.insert([P])
            
        elif name == 'Return':
            un.history.undo_save(1)
            self.cursor.paste('<br/>')
        
        elif name == 'Ctrl Lock':
            un.history.undo_save(1)
            self.cursor.paste('<mi>' + char + '</mi>')
            
        elif name == 'Paste':
            if char:
                un.history.undo_save(3)
                self.cursor.paste(char)
        
        elif name == 'Copy':
            sel = self.cursor.copy_selection()
            if sel:
                return sel
        
        elif name == 'Cut':
            sel = self.cursor.copy_selection()
            if sel:
                un.history.undo_save(3)
                self.cursor.delete()
                return sel

        elif name in self._special_names:
            un.history.undo_save(3)
            if not self.cursor.bridge(self[name], name not in self._CLOSE):
                un.history.pop()
        else:
            un.history.undo_save(13)
            self.cursor.insert_chars([char])
