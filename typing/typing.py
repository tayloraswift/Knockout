from itertools import chain
import time

from style import styles
from edit import cursor

from elements.elements import Paragraph, OpenFontpost, CloseFontpost

from IO import un, kevin

class Keyboard(dict):
    def __init__(self, shortcuts):
        self._shortcuts = shortcuts
        self.turnover()

    def turnover(self):
        shortcuts = self._shortcuts
        _OPEN = set(k[0] for k in shortcuts)
        self._CLOSE = set(k[1] for k in shortcuts)
        self._special_names = set(_OPEN) | set(self._CLOSE)
        
        dict.__init__(self, chain.from_iterable(((key1, styles.FTAGS[name]), (key2, styles.FTAGS[name])) for key1, key2, name in shortcuts))
        
    def type_document(self, name, char, lastpress=[0], direction=[0]):
        CURSOR = cursor.fcursor.i
        
        # Non replacing
        if name == 'Left':
            un.history.undo_save(0)
            cursor.fcursor.i -= 1
            cursor.fcursor.j = cursor.fcursor.i
                
        elif name == 'Right':
            un.history.undo_save(0)
            
            cursor.fcursor.i += 1
            cursor.fcursor.j = cursor.fcursor.i
            
        elif name == 'Up':
            un.history.undo_save(0)
            
            cursor.fcursor.hop(False)
            cursor.fcursor.j = cursor.fcursor.i
            
        elif name == 'Down':
            un.history.undo_save(0)
            
            cursor.fcursor.hop(True)
            cursor.fcursor.j = cursor.fcursor.i

        elif name in ['Home', 'End']:
            un.history.undo_save(0)

            i, j = cursor.fcursor.front_and_back()
            if name == 'Home':
                cursor.fcursor.i = i
                cursor.fcursor.j = i
            else:
                cursor.fcursor.i = j
                cursor.fcursor.j = j

        elif name == 'All':
            un.history.undo_save(0)
            
            cursor.fcursor.expand_cursors()
        
        # replacing
        elif name in ['BackSpace', 'Delete']:
            if cursor.fcursor.take_selection():
                un.history.undo_save(3)
                cursor.fcursor.insert([])
            elif name == 'BackSpace':            
                # for deleting paragraphs
                if type(cursor.fcursor.text[CURSOR - 1]) is Paragraph:
                    # make sure that we’re not sliding the cursor
                    if time.time() - lastpress[0] > 0.13:
                        un.history.undo_save(-2)
                        cursor.fcursor.delspace(False)
                else:
                    un.history.undo_save(-1)
                    cursor.fcursor.delspace(False)

            else:
                # for deleting paragraphs (forward delete)
                if cursor.fcursor.text[CURSOR] == '</p>':
                    if time.time() - lastpress[0] > 0.13:
                        un.history.undo_save(-2)
                        cursor.fcursor.delspace(True)
                else:
                    un.history.undo_save(-1)
                    cursor.fcursor.delspace(True)
                    
            # record time
            lastpress[0] = time.time()
        
        elif name == 'paragraph':
            un.history.undo_save(2)
    #        name = meredith.mipsy.paragraph_at()[0].name
    #        if name[0] == 'h' and name[1].isdigit() and meredith.mipsy.at_absolute(CURSOR) == '</p>' and 'body' in styles.PARASTYLES:
    #            name = 'body'
            P = cursor.fcursor.pp_at().P.copy()
            cursor.fcursor.insert(['</p>', Paragraph(P)])
            
        elif name == 'Return':
            un.history.undo_save(1)
            cursor.fcursor.insert(['<br/>'])
        elif name == 'Ctrl Alt':
            un.history.undo_save(1)
            cursor.fcursor.insert(kevin.deserialize('<mi char="' + char + '"/>', fragment=True))
            
        elif name == 'Paste':
            if char:
                un.history.undo_save(3)
                cursor.fcursor.insert(kevin.deserialize(char, fragment=True))
        
        elif name == 'Copy':
            sel = cursor.fcursor.take_selection()
            if sel:
                return kevin.serialize(sel)
        
        elif name == 'Cut':
            sel = cursor.fcursor.take_selection()
            if sel:
                un.history.undo_save(3)
                cursor.fcursor.insert([])
            
                return kevin.serialize(sel)

        elif name in self._special_names:
            T = self[name]
            if name in self._CLOSE:
                B = False
                F = CloseFontpost
            else:
                B = True
                F = OpenFontpost
            if cursor.fcursor.take_selection():
                un.history.undo_save(3)
                if not cursor.fcursor.bridge(T, B):
                    un.history.pop()
            else:
                un.history.undo_save(1)
                cursor.fcursor.insert([F(T)])
        else:
            un.history.undo_save(13)
            cursor.fcursor.insert([char])
