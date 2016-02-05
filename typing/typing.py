from itertools import chain
import time

from fonts import styles
from model import meredith, cursor
from state.contexts import Text as CText

from elements.elements import Paragraph, OpenFontpost, CloseFontpost, Image

from model import un

def set_cursor(i):
    cursor.fcursor.i = cursor.fcursor.skip(i, 0)
    
def set_select(i):
    cursor.fcursor.j = cursor.fcursor.skip(i, 0)

def match_cursors():
    cursor.fcursor.j = cursor.fcursor.i

def hop(dl, CURSOR):
    try:
        l = cursor.fcursor.index_to_line(CURSOR)
        set_cursor(CText.tract.target_glyph(
                    cursor.fcursor.text_index_x(CURSOR, l), 
                    0, 
                    l + dl
                    ))
    except IndexError:
        pass

class Keyboard(dict):
    def __init__(self, shortcuts):
        _OPEN = set(k[0] for k in shortcuts)
        self._CLOSE = set(k[1] for k in shortcuts)
        self._special_names = set(_OPEN) | set(self._CLOSE)
        
        dict.__init__(self, chain.from_iterable(((key1, styles.FTAGS[name]), (key2, styles.FTAGS[name])) for key1, key2, name in shortcuts))
        
    def type_document(self, name, char, lastpress=[0], direction=[0]):

        CURSOR = cursor.fcursor.i
        
        # Non replacing
        if name == 'Left':
            un.history.undo_save(0)
            cursor.fcursor.i = cursor.fcursor.skip(CURSOR, -1)
            match_cursors()
                
        elif name == 'Right':
            un.history.undo_save(0)
            
            cursor.fcursor.i = cursor.fcursor.skip(CURSOR, 1)
            match_cursors()
            
        elif name == 'Up':
            un.history.undo_save(0)
            
            hop(-1, CURSOR)
            match_cursors()
        elif name == 'Down':
            un.history.undo_save(0)
            
            hop(1, CURSOR)
            match_cursors()

        elif name in ['Home', 'End']:
            un.history.undo_save(0)

            i, j = cursor.fcursor.front_and_back()
            if name == 'Home':
                set_cursor(i)
                match_cursors()
            else:
                set_cursor(j)
                match_cursors()

        elif name == 'All':
            un.history.undo_save(0)
            
            cursor.fcursor.expand_cursors()
        
        # replacing
        elif name in ['BackSpace', 'Delete']:
            
            if cursor.fcursor.take_selection():
                un.history.undo_save(3)
                cursor.fcursor.delete()
            elif name == 'BackSpace':            
                # for deleting paragraphs
                prec = cursor.fcursor.text[CURSOR - 1]
                if type(prec) is Paragraph:
                    # make sure that (1) we’re not trying to delete the first paragraph, 
                    # and that (2) we’re not sliding the cursor
                    if CURSOR > 1 and time.time() - lastpress[0] > 0.2:
                        un.history.undo_save(-2)
                        # for table objects
                        if cursor.fcursor.text[CURSOR - 2] != '</p>':
                            del cursor.fcursor.text[CURSOR - 2]
                            cursor.fcursor.delete(da = 0)
                        else:
                            cursor.fcursor.delete(da = -2)

                elif prec != '</p>':
                    un.history.undo_save(-1)
                    cursor.fcursor.delete(da = -1)
            else:
                # for deleting paragraphs (forward delete)
                if cursor.fcursor.text[CURSOR] == '</p>':
                    if time.time() - lastpress[0] > 0.2:
                        un.history.undo_save(-2)
                        if type(cursor.fcursor.text[CURSOR + 1]) is not Paragraph:
                            del cursor.fcursor.text[CURSOR + 1]
                            cursor.fcursor.delete(db = 0)
                        else:
                            cursor.fcursor.delete(db = 2)
                else:
                    un.history.undo_save(-1)
                    cursor.fcursor.delete(db = 1)
                    
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
            cursor.fcursor.insert(['<br>'])

        elif name == 'Paste':
            if char:
                un.history.undo_save(3)
                if cursor.fcursor.take_selection():
                    cursor.fcursor.delete()
                # char is a LIST in this case
                cursor.fcursor.insert(char)
        
        elif name == 'Copy':
            sel = cursor.fcursor.take_selection()
            if sel:
                return sel
        
        elif name == 'Cut':
            sel = cursor.fcursor.take_selection()
            if sel:
                un.history.undo_save(3)
                cursor.fcursor.delete()
            
                return sel
        

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
