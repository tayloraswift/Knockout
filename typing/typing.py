import time

from model import meredith

from model import un
            

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
        MT.insert(['</p>', ('<p>', 'body')])
        
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
    
    # encapsulating
    elif name == 'Ctrl_I':
        un.history.undo_save(3)
        if not MT.bridge('emphasis', True):
            un.history.pop()
    elif name == 'Ctrl_B':
        un.history.undo_save(3)
        if not MT.bridge('strong', True):
            un.history.pop()

    elif name == 'Ctrl_Shift_I':
        un.history.undo_save(3)
        if not MT.bridge('emphasis', False):
            un.history.pop()
    elif name == 'Ctrl_Shift_B':
        un.history.undo_save(3)
        if not MT.bridge('strong', False):
            un.history.pop()
    
    # inserting
    else:
        un.history.undo_save(1)
        MT.insert([char])
