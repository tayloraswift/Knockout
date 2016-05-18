from pprint import pformat
from ast import literal_eval

from style import fonts, styles
from state import constants, noticeboard
from model import meredith
from IO import tree, un, xml
#from modules import modulestyles
#from elements import modules
from elements.node import Node

from elements import datablocks

def save():
    FI = ('<head><meta charset="UTF-8"></head>\n<title>', constants.filename, '</title>\n\n',
            '<body>\n',
            kevin.serialize([F.NODE for F in meredith.mipsy], indent=-1),
            '\n</body>\n')

    page = {'dimensions': (meredith.page.WIDTH, meredith.page.HEIGHT),
            'dual': meredith.page.dual}
    
    grid = meredith.mipsy.page_grid
    textcontexts = cursor.fcursor.polaroid()
    
    ct, c = caramel.delight.at()
    channelcontexts = {'t': meredith.mipsy.index(ct),
                    'c': c, 
                    'p': caramel.delight.PG
                    }
    
    PPP = styles.PARASTYLES.polaroid()
    FFF = {N: F.polaroid() for N, F in styles.FONTSTYLES.items()}
    
    PTT = list(sorted(T.polaroid() for T in styles.PTAGS.values() if not T.is_group))
    FTT = list(sorted(T.polaroid() for T in styles.FTAGS.values() if not T.is_group))

    from interface import taylor
    
    DATA = {'grid': grid, 'contexts': {'text': textcontexts, 'channels': channelcontexts}, 'PARASTYLES': PPP, 'FONTSTYLES': FFF, 'PTAGLIST': PTT, 'FTAGLIST': FTT, 'view': taylor.becky.read_display_state(), 'page': page}
    
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

    # unpack styles
#    styles.faith(DATA)
#    Node.MSL = modulestyles.MS_Library(modules)
    
    # set up tract model, page grid objects
    datablocks.TTAGS, datablocks.BTAGS, datablocks.DOCUMENT, datablocks.TSTYLES, datablocks.BSTYLES = tree.deserialize(doc)
    
    from interface import karlie, taylor
    from state.contexts import Text
    from edit import cursor, caramel
    from typing import typing
    
    # aim editor objects
    caramel.delight = caramel.Channels_controls(DATA['contexts']['channels'])
#    typing.keyboard = typing.Keyboard(constants.shortcuts)
    cursor.fcursor = cursor.PlaneCursor( * DATA['contexts']['text'] )
    typing.keyboard = None
    
    datablocks.DOCUMENT.layout_all()
#    Text.update()

    # start undo tracking
    un.history = un.UN() 

    

    taylor.becky = taylor.Document_view(save, DATA['view'])
    noticeboard.refresh_properties_type.push_change(DATA['view']['mode'])
#    karlie.klossy = karlie.Properties(DATA['view']['mode'], partition=1 )
    class KK(object):
        render = lambda *k: None
        hover = lambda *k: None
    
    karlie.klossy = KK()

#    un.history.save()
