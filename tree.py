import time
import _pickle as pickle
from gi.repository import Gtk, Gdk
from text_t import character
import meredith
import olivia

import ui

controls = ui.Panel(100, [])

def switch_mode_text():
    return 'text'

def switch_mode_channels():
    return 'channels'
    
button = ui.Button('Text', switch_mode_text)
controls.buttons.append(button)
button = ui.Button('Channels', switch_mode_channels)
controls.buttons.append(button)
button = ui.Button('Add portal', meredith.mere.add_channel)
controls.buttons.append(button)


def take_event(x, y, event, key=False, value=None, lastpress=[0], mode=['text']):
    if key and mode[0] == 'text':
        name = event
        # conflict with paragraph sign
        if event == 'paragraph':
            meredith.mere.tracts[meredith.mere.t].insert(['</p>', ['<p>', 'body']])
        
        elif name in ['BackSpace', 'Delete']:
            
            if meredith.mere.tracts[meredith.mere.t].take_selection():
                meredith.mere.tracts[meredith.mere.t].delete( * meredith.mere.selection())
            elif name == 'BackSpace':

                # for deleting paragraphs
                if character(meredith.mere.at(-1)) == '<p>':
                    # make sure that (1) we’re not trying to delete the first paragraph, 
                    # and that (2) we’re not sliding the cursor
                    if meredith.mere.tracts[meredith.mere.t].cursor.cursor > 1 and time.time() - lastpress[0] > 0.2:
                        meredith.mere.cdelete(-2, 0)
                else:
                    meredith.mere.tracts[meredith.mere.t].delete()
            else:
                # for deleting paragraphs (forward delete)
                if character(meredith.mere.at()) == '</p>':
                    if time.time() - lastpress[0] > 0.2:
                        meredith.mere.cdelete(0, 2)
                else:
                    meredith.mere.tracts[meredith.mere.t].delete(meredith.mere.tracts[meredith.mere.t].cursor.cursor)
                    
            # record time
            lastpress[0] = time.time()
                
        elif name == 'Left':
            if meredith.mere.active_cursor() > 1:
                meredith.mere.tracts[meredith.mere.t].cursor.skip(-1, meredith.mere.tracts[meredith.mere.t].text)
                meredith.mere.match_cursors()
        elif name == 'Right':
            if meredith.mere.active_cursor() < len(meredith.mere.tracts[meredith.mere.t].text):
                meredith.mere.tracts[meredith.mere.t].cursor.skip(1, meredith.mere.tracts[meredith.mere.t].text)
                meredith.mere.match_cursors()
        elif name == 'Up':
            meredith.mere.hop(-1)
            meredith.mere.match_cursors()
        elif name == 'Down':
            meredith.mere.hop(1)
            meredith.mere.match_cursors()
        elif name == 'Return':
            meredith.mere.tracts[meredith.mere.t].insert(['<br>'])
        elif name in ['Home', 'End']:
            li = meredith.mere.tracts[meredith.mere.t].index_to_line(meredith.mere.tracts[meredith.mere.t].cursor.cursor)
            if name == 'Home':
                meredith.mere.tracts[meredith.mere.t].cursor.set_cursor(meredith.mere.tracts[meredith.mere.t].glyphs[li].startindex, meredith.mere.tracts[meredith.mere.t].text)
                meredith.mere.match_cursors()
            else:
                meredith.mere.tracts[meredith.mere.t].cursor.set_cursor(meredith.mere.tracts[meredith.mere.t].glyphs[li].startindex + len(meredith.mere.tracts[meredith.mere.t].glyphs[li].glyphs), meredith.mere.tracts[meredith.mere.t].text)
                meredith.mere.match_cursors()
        else:
            # turn key name into unicode value then into character
            cc = chr(Gdk.keyval_to_unicode(value))
            meredith.mere.tracts[meredith.mere.t].insert([cc])


    elif key and mode[0] == 'channels':
        name = event
        olivia.edit_channels(name, None, 'key')

    else:
        if event == 'press':
            clicked = controls.is_clicked(x, y)
            if clicked is not None:
                out = clicked.cb()
                # switch modes
                if out is not None:
                    mode[0] = out
            
            # TEXT EDITING MODE
            elif mode[0] == 'text':
                try:
                    t, c = meredith.mere.target_channel(x - 200, y - 100, 20)
                    meredith.mere.set_t(t)
                    meredith.mere.set_cursor_xy(x - 200, y - 100, c)
                    meredith.mere.match_cursors()
                except IndexError:
                    # occurs if an empty channel is selected
                    pass
            elif mode[0] == 'channels':
                olivia.edit_channels(x - 200, y - 100, event)
                
        elif event == 'press_motion':
            # TEXT EDITING MODE
            if mode[0] == 'text':
                try:
                    meredith.mere.set_select_xy(x - 200, y - 100)
                except IndexError:
                    # occurs if an empty channel is selected
                    pass

            elif mode[0] == 'channels':
                olivia.edit_channels(x - 200, y - 100, event)
        elif event == 'release':
            if mode[0] == 'channels':
                olivia.edit_channels(x - 200, y - 100, event)
                
        elif event == 'motion':
            controls.update(x, y)
    
    return mode[0]


def paste_local_text(self, clipboard, selectiondata, data=None):
    characters = pickle.loads(clipboard.wait_for_text())
    meredith.mere.tracts[meredith.mere.t].insert(characters)
def paste_text(self, clipboard, text, data=None):
    characters = [['<br>', '<p>', '</p>'][['\u000A', '\u2028', '\u2029'].index(u)] if u in ['\u000A', '\u2028', '\u2029'] else u for u in list(self.clipboard.wait_for_text()) ]
    meredith.mere.tracts[meredith.mere.t].insert(characters)
