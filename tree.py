import meredith
import typing
import olivia
import properties

import constants

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
button = ui.Button('Add portal', meredith.mipsy.add_channel)
controls.buttons.append(button)



def take_event(x, y, event, key=False, char=None, mode=['text'], region=['document'], geometry=None):
    if key:
        if region[0] == 'document':
            if mode[0] == 'text':
                return typing.type_document(event, char)

            elif mode[0] == 'channels':
                name = event
                olivia.edit_channels(name, None, 'key')
                
        elif region[0] == 'properties':
            return properties.panel.key_input(event, char)
                
    else:
        # Changing regions
        
        if x > geometry[0] - constants.propertieswidth:
            if event == 'press' and region[0] != 'properties':
                region[0] = 'properties'

        else:
            if event == 'press' and region[0] != 'document':
                # if we're going from properties to document, dump properties
                if region[0] == 'properties':
                    properties.panel.press(x, y)
                region[0] = 'document'
                
        #############
        
        if event == 'press':
            if region[0] == 'document':
                clicked = controls.is_clicked(x, y)
                if clicked is not None:
                    out = clicked.cb()
                    # switch modes
                    if out is not None:
                        mode[0] = out
            
                # TEXT EDITING MODE
                elif mode[0] == 'text':
                    try:
                        t, c = meredith.mipsy.target_channel(x - 200, y - 100, 20)
                        meredith.mipsy.set_t(t)
                        meredith.mipsy.set_cursor_xy(x - 200, y - 100, c)
                        meredith.mipsy.match_cursors()
                    except IndexError:
                        # occurs if an empty channel is selected
                        pass
                elif mode[0] == 'channels':
                    olivia.edit_channels(x - 200, y - 100, event)
                    
            elif region[0] == 'properties':
                properties.panel.press(x, y)
                
        elif event == 'press_motion':
            if region[0] == 'document':
                # TEXT EDITING MODE
                if mode[0] == 'text':
                    try:
                        meredith.mipsy.set_select_xy(x - 200, y - 100)
                    except IndexError:
                        # occurs if an empty channel is selected
                        pass

                elif mode[0] == 'channels':
                    olivia.edit_channels(x - 200, y - 100, event)
                    
            elif region[0] == 'properties':
                properties.panel.press_motion(x)
                
        elif event == 'release':
            if region[0] == 'document':
                if mode[0] == 'channels':
                    olivia.edit_channels(x - 200, y - 100, event)
                
        elif event == 'motion':
            controls.update(x, y)
    
    return mode[0]


#def paste_local_text(self, clipboard, selectiondata, data=None):
#    characters = pickle.loads(clipboard.wait_for_text())
#    meredith.mipsy.tracts[meredith.mipsy.t].insert(characters)
#def paste_text(self, clipboard, text, data=None):
#    characters = [['<br>', '<p>', '</p>'][['\u000A', '\u2028', '\u2029'].index(u)] if u in ['\u000A', '\u2028', '\u2029'] else u for u in list(self.clipboard.wait_for_text()) ]
#    meredith.mipsy.tracts[meredith.mipsy.t].insert(characters)
