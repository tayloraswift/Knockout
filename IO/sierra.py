from pprint import pformat
from ast import literal_eval

from state import constants, noticeboard

from meredith import datablocks, box

from IO import tree

def save():
    FI = ('<head><meta charset="UTF-8"></head>\n<title>', constants.filename, '</title>\n\n',
            tree.serialize([datablocks.DOCUMENT, datablocks.TSTYLES, datablocks.BSTYLES]))
    
    from edit import cursor, caramel
    textcontexts = (cursor.fcursor.plane_address, cursor.fcursor.i, cursor.fcursor.j)
    
    ct, c = caramel.delight.at()
    channelcontexts = datablocks.DOCUMENT.content.index(ct), c

    from interface import taylor
    
    DATA = {'text': textcontexts, 'channels': channelcontexts, 'view': taylor.becky.read_display_state()}
    
    with open(constants.filename, 'w') as fi:
        fi.write(''.join(FI))
        fi.write('\n<!-- #############\n')
        fi.write(pformat(DATA, width=189))
        fi.write('\n############# -->\n')

def load(name):
    with open(name, 'r') as fi:
        constants.filename = name
        doc = fi.read()

    DATA = literal_eval(doc[doc.find('<!-- #############') + 18 : doc.find('############# -->')])
    
    datablocks.TTAGS, datablocks.BTAGS = tree.deserialize('<texttags/><blocktags/>')
    datablocks.DOCUMENT, datablocks.TSTYLES, datablocks.BSTYLES = tree.deserialize(doc)
    
    import keyboard
    from state.contexts import Text
    from edit import cursor, caramel
    
    # aim editor objects
    caramel.delight = caramel.Channels_controls( * DATA['channels'] )
    keyboard.keyboard = keyboard.Keyboard(constants.shortcuts)
    cursor.fcursor = cursor.PlaneCursor( * DATA['text'] )
    
    datablocks.DOCUMENT.layout_all()
    Text.update()

    # start undo tracking
    from IO import un
    un.history = un.UN()
    box.Box.before = un.history.save
    
    from interface import karlie, taylor
    
    taylor.becky = taylor.Document_view(save, DATA['view'])
    noticeboard.refresh_properties_type.push_change(DATA['view']['mode'])
    karlie.klossy = karlie.Properties(DATA['view']['mode'], partition=1 )

    un.history.save()
