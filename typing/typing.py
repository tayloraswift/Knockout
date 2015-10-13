import time

from model import meredith
from model.text_t import character


def type_document(name, char, lastpress=[0]):
    if name == 'paragraph':
        meredith.mipsy.tracts[meredith.mipsy.t].insert(['</p>', ['<p>', 'body']])
    
    elif name in ['BackSpace', 'Delete']:
        
        if meredith.mipsy.tracts[meredith.mipsy.t].take_selection():
            meredith.mipsy.tracts[meredith.mipsy.t].delete( * meredith.mipsy.selection())
        elif name == 'BackSpace':

            # for deleting paragraphs
            if character(meredith.mipsy.at(-1)) == '<p>':
                # make sure that (1) we’re not trying to delete the first paragraph, 
                # and that (2) we’re not sliding the cursor
                if meredith.mipsy.tracts[meredith.mipsy.t].cursor.cursor > 1 and time.time() - lastpress[0] > 0.2:
                    meredith.mipsy.cdelete(-2, 0)
            else:
                meredith.mipsy.tracts[meredith.mipsy.t].delete()
        else:
            # for deleting paragraphs (forward delete)
            if character(meredith.mipsy.at()) == '</p>':
                if time.time() - lastpress[0] > 0.2:
                    meredith.mipsy.cdelete(0, 2)
            else:
                meredith.mipsy.tracts[meredith.mipsy.t].delete(meredith.mipsy.tracts[meredith.mipsy.t].cursor.cursor)
                
        # record time
        lastpress[0] = time.time()
            
    elif name == 'Left':
        if meredith.mipsy.active_cursor() > 1:
            meredith.mipsy.tracts[meredith.mipsy.t].cursor.skip(-1, meredith.mipsy.tracts[meredith.mipsy.t].text)
            meredith.mipsy.match_cursors()
    elif name == 'Right':
        if meredith.mipsy.active_cursor() < len(meredith.mipsy.tracts[meredith.mipsy.t].text):
            meredith.mipsy.tracts[meredith.mipsy.t].cursor.skip(1, meredith.mipsy.tracts[meredith.mipsy.t].text)
            meredith.mipsy.match_cursors()
    elif name == 'Up':
        meredith.mipsy.hop(-1)
        meredith.mipsy.match_cursors()
    elif name == 'Down':
        meredith.mipsy.hop(1)
        meredith.mipsy.match_cursors()
    elif name == 'Return':
        meredith.mipsy.tracts[meredith.mipsy.t].insert(['<br>'])
    elif name in ['Home', 'End']:
        li = meredith.mipsy.tracts[meredith.mipsy.t].index_to_line(meredith.mipsy.tracts[meredith.mipsy.t].cursor.cursor)
        if name == 'Home':
            meredith.mipsy.tracts[meredith.mipsy.t].cursor.set_cursor(meredith.mipsy.tracts[meredith.mipsy.t].glyphs[li].startindex, meredith.mipsy.tracts[meredith.mipsy.t].text)
            meredith.mipsy.match_cursors()
        else:
            meredith.mipsy.tracts[meredith.mipsy.t].cursor.set_cursor(meredith.mipsy.tracts[meredith.mipsy.t].glyphs[li].startindex + len(meredith.mipsy.tracts[meredith.mipsy.t].glyphs[li].glyphs), meredith.mipsy.tracts[meredith.mipsy.t].text)
            meredith.mipsy.match_cursors()
            
    elif name == 'Paste':
        
        if meredith.mipsy.tracts[meredith.mipsy.t].take_selection():
            meredith.mipsy.tracts[meredith.mipsy.t].delete( * meredith.mipsy.selection())
        # char is a LIST in this case
        meredith.mipsy.tracts[meredith.mipsy.t].insert(char)
    elif name == 'Copy':
        sel = meredith.mipsy.tracts[meredith.mipsy.t].take_selection()
        if sel:
            return sel
    elif name == 'Cut':
        sel = meredith.mipsy.tracts[meredith.mipsy.t].take_selection()
        if sel:
            meredith.mipsy.tracts[meredith.mipsy.t].delete( * meredith.mipsy.selection())
            return sel
            
    else:
        meredith.mipsy.tracts[meredith.mipsy.t].insert([char])
