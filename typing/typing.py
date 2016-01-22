import time

from fonts import styles

from model import meredith

from model import un

sup = styles.FTAGS['sup']
sub = styles.FTAGS['sub']
emphasis = styles.FTAGS['emphasis']
strong = styles.FTAGS['strong']
_OPEN = {'Ctrl equal': sup, 'Ctrl minus': sub, 'Ctrl b': strong, 'Ctrl i': emphasis }
_CLOSE = {'Ctrl underscore': sub, 'Ctrl plus': sup, 'Ctrl B': strong, 'Ctrl I': emphasis }
special_names = set(_OPEN) | set(_CLOSE)

def type_document(name, char, lastpress=[0], direction=[0]):

    CURSOR = meredith.mipsy.tracts[0].cursor.cursor
    MT = meredith.mipsy.tracts[0]
    
    # Non replacing
    if name == 'Left':
        if CURSOR > 1:
            un.history.undo_save(0)
            
            MT.cursor.skip(-1, MT.text)
            meredith.mipsy.match_cursors()
    elif name == 'Right':
        if CURSOR < len(MT.text):
            un.history.undo_save(0)
            
            MT.cursor.skip(1, MT.text)
            meredith.mipsy.match_cursors()
    elif name == 'Up':
        un.history.undo_save(0)
        
        meredith.mipsy.hop(-1)
        meredith.mipsy.match_cursors()
    elif name == 'Down':
        un.history.undo_save(0)
        
        meredith.mipsy.hop(1)
        meredith.mipsy.match_cursors()

    elif name in ['Home', 'End']:
        un.history.undo_save(0)
        
        li = MT.index_to_line(CURSOR)
        i, j = MT.line_indices(li)
        if name == 'Home':
            meredith.mipsy.set_cursor(i)
            meredith.mipsy.match_cursors()
        else:
            meredith.mipsy.set_cursor(j)
            meredith.mipsy.match_cursors()

    elif name == 'All':
        un.history.undo_save(0)
        
        meredith.mipsy.tracts[0].expand_cursors()
    
    # replacing

    elif name in ['BackSpace', 'Delete']:
        
        if MT.take_selection():
            un.history.undo_save(3)
            MT.delete()
        elif name == 'BackSpace':            
            # for deleting paragraphs
            if meredith.mipsy.at_absolute(CURSOR - 1) == '<p>':
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
            if meredith.mipsy.at_absolute(CURSOR) == '</p>':
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
        MT.insert(['</p>', ['<p>', meredith.mipsy.paragraph_at()[0].copy() ]])
        
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
        MT.insert([char])
