import time
from model.wonder import character
from fonts import styles
from state.contexts import Text as CText
from model import meredith

from model import un

sup = styles.FTAGS['sup']
sub = styles.FTAGS['sub']
emphasis = styles.FTAGS['emphasis']
strong = styles.FTAGS['strong']
_OPEN = {'Ctrl equal': sup, 'Ctrl minus': sub, 'Ctrl b': strong, 'Ctrl i': emphasis }
_CLOSE = {'Ctrl underscore': sub, 'Ctrl plus': sup, 'Ctrl B': strong, 'Ctrl I': emphasis }
special_names = set(_OPEN) | set(_CLOSE)

def set_cursor(i):
    CText.tract.cursor.set_cursor(i, CText.tract.text)
def set_select(i):
    CText.tract.select.set_cursor(i, CText.tract.text)

def match_cursors():
    CText.tract.select.cursor = CText.tract.cursor.cursor

def hop(dl, CURSOR):
    try:
        set_cursor(CText.tract.target_glyph(
                    CText.tract.text_index_x(CURSOR), 
                    0, 
                    CText.tract.index_to_line(CURSOR) + dl
                    ))
    except IndexError:
        pass

def type_document(name, char, lastpress=[0], direction=[0]):

    CURSOR = CText.tract.cursor.cursor
    MT = CText.tract
    
    # Non replacing
    if name == 'Left':
        if CURSOR > 1:
            un.history.undo_save(0)
            
            MT.cursor.skip(-1, MT.text)
            match_cursors()
    elif name == 'Right':
        if CURSOR < len(MT.text):
            un.history.undo_save(0)
            
            MT.cursor.skip(1, MT.text)
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
        
        li = MT.index_to_line(CURSOR)
        i, j = MT.line_indices(li)
        if name == 'Home':
            set_cursor(i)
            match_cursors()
        else:
            set_cursor(j)
            match_cursors()

    elif name == 'All':
        un.history.undo_save(0)
        
        MT.expand_cursors()
    
    # replacing

    elif name in ['BackSpace', 'Delete']:
        
        if MT.take_selection():
            un.history.undo_save(3)
            MT.delete()
        elif name == 'BackSpace':            
            # for deleting paragraphs
            if character(CText.tract.text[CURSOR - 1]) == '<p>':
                # make sure that (1) we’re not trying to delete the first paragraph, 
                # and that (2) we’re not sliding the cursor
                if CURSOR > 1 and time.time() - lastpress[0] > 0.2:
                    un.history.undo_save(-2)
                    MT.delete(da = -2)

            else:
                un.history.undo_save(-1)
                MT.delete(da = -1)
        else:
            # for deleting paragraphs (forward delete)
            if CText.tract.text[CURSOR] == '</p>':
                if time.time() - lastpress[0] > 0.2:
                    un.history.undo_save(-2)
                    MT.delete(db = 2)
            else:
                un.history.undo_save(-1)
                MT.delete(db = 1)
                
        # record time
        lastpress[0] = time.time()
    
    elif name == 'paragraph':
        un.history.undo_save(2)
#        name = meredith.mipsy.paragraph_at()[0].name
#        if name[0] == 'h' and name[1].isdigit() and meredith.mipsy.at_absolute(CURSOR) == '</p>' and 'body' in styles.PARASTYLES:
#            name = 'body'
        MT.insert(['</p>', ['<p>', CText.tract.pp_at()[0].copy() ]])
        
    elif name == 'Return':
        un.history.undo_save(1)
        MT.insert(['<br>'])

    elif name == 'Paste':
        if char:
            un.history.undo_save(3)
            if MT.take_selection():
                MT.delete()
            # char is a LIST in this case
            MT.insert(char)
    
    elif name == 'Copy':
        sel = MT.take_selection()
        if sel:
            return sel
    
    elif name == 'Cut':
        sel = MT.take_selection()
        if sel:
            un.history.undo_save(3)
            MT.delete()
        
            return sel
    

    elif name in special_names:
        if name in _OPEN:
            T = _OPEN[name]
            B = True
            F = '<f>'
        else:
            T = _CLOSE[name]
            B = False
            F = '</f>'
        if MT.take_selection():
            un.history.undo_save(3)
            if not MT.bridge(T, B):
                un.history.pop()
        else:
            un.history.undo_save(1)
            MT.insert([(F, T)])
    else:
        un.history.undo_save(13)
        MT.insert([char])
