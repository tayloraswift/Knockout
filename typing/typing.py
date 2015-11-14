import time

from model import meredith
from model.wonder import character

from model import un
            

def type_document(name, char, lastpress=[0], direction=[0]):

    CURSOR = meredith.mipsy.selection()[0]
    
    # Non replacing
    if name == 'Left':
        if CURSOR > 1:
            un.history.undo_save(0)
            
            meredith.mipsy.tracts[meredith.mipsy.t].cursor.skip(-1, meredith.mipsy.tracts[meredith.mipsy.t].text)
            meredith.mipsy.match_cursors()
    elif name == 'Right':
        if CURSOR < len(meredith.mipsy.tracts[meredith.mipsy.t].text):
            un.history.undo_save(0)
            
            meredith.mipsy.tracts[meredith.mipsy.t].cursor.skip(1, meredith.mipsy.tracts[meredith.mipsy.t].text)
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
        
        li = meredith.mipsy.tracts[meredith.mipsy.t].index_to_line(CURSOR)
        i, j = meredith.mipsy.tracts[meredith.mipsy.t].line_indices(li)
        if name == 'Home':
            meredith.mipsy.set_cursor(meredith.mipsy.t, i)
            meredith.mipsy.match_cursors()
        else:
            meredith.mipsy.set_cursor(meredith.mipsy.t, j)
            meredith.mipsy.match_cursors()

    elif name == 'All':
        un.history.undo_save(0)
        
        meredith.mipsy.select_all()
    
    # replacing

    elif name in ['BackSpace', 'Delete']:
        
        if meredith.mipsy.tracts[meredith.mipsy.t].take_selection():
            un.history.undo_save(3)
            meredith.mipsy.tracts[meredith.mipsy.t].delete()
        elif name == 'BackSpace':            
            # for deleting paragraphs
            if character(meredith.mipsy.at_absolute(CURSOR - 1)) == '<p>':
                # make sure that (1) we’re not trying to delete the first paragraph, 
                # and that (2) we’re not sliding the cursor
                if CURSOR > 1 and time.time() - lastpress[0] > 0.2:
                    un.history.undo_save(-2)
                    meredith.mipsy.tracts[meredith.mipsy.t].delete(da = -2)

            else:
                un.history.undo_save(-1)
                meredith.mipsy.tracts[meredith.mipsy.t].delete(da = -1)
        else:
            # for deleting paragraphs (forward delete)
            if character(meredith.mipsy.at_absolute(CURSOR)) == '</p>':
                if time.time() - lastpress[0] > 0.2:
                    un.history.undo_save(-2)
                    meredith.mipsy.tracts[meredith.mipsy.t].delete(db = 2)
            else:
                un.history.undo_save(-1)
                meredith.mipsy.tracts[meredith.mipsy.t].delete(db = 1)
                
        # record time
        lastpress[0] = time.time()
    
    elif name == 'paragraph':
        un.history.undo_save(2)
        meredith.mipsy.tracts[meredith.mipsy.t].insert(['</p>', ('<p>', 'body')])
        
    elif name == 'Return':
        un.history.undo_save(1)
        meredith.mipsy.tracts[meredith.mipsy.t].insert(['<br>'])

    elif name == 'Paste':
        if char:
            un.history.undo_save(3)
            if meredith.mipsy.tracts[meredith.mipsy.t].take_selection():
                meredith.mipsy.tracts[meredith.mipsy.t].delete()
            # char is a LIST in this case
            meredith.mipsy.tracts[meredith.mipsy.t].insert(char)
    
    elif name == 'Copy':
        sel = meredith.mipsy.tracts[meredith.mipsy.t].take_selection()
        if sel:
            return sel
    
    elif name == 'Cut':
        sel = meredith.mipsy.tracts[meredith.mipsy.t].take_selection()
        if sel:
            un.history.undo_save(3)
            meredith.mipsy.tracts[meredith.mipsy.t].delete()
        
            return sel
    
    # encapsulating
    elif name == 'Ctrl_I':
        un.history.undo_save(3)
        if not meredith.mipsy.tracts[meredith.mipsy.t].bridge('emphasis', True):
            un.history.pop()
    elif name == 'Ctrl_B':
        un.history.undo_save(3)
        if not meredith.mipsy.tracts[meredith.mipsy.t].bridge('strong', True):
            un.history.pop()

    elif name == 'Ctrl_Shift_I':
        un.history.undo_save(3)
        if not meredith.mipsy.tracts[meredith.mipsy.t].bridge('emphasis', False):
            un.history.pop()
    elif name == 'Ctrl_Shift_B':
        un.history.undo_save(3)
        if not meredith.mipsy.tracts[meredith.mipsy.t].bridge('strong', False):
            un.history.pop()
    
    # inserting
    else:
        un.history.undo_save(1)
        meredith.mipsy.tracts[meredith.mipsy.t].insert([char])
