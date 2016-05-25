from pprint import pformat
from ast import literal_eval

from state import constants, noticeboard
#from modules import modulestyles
#from elements import modules

from meredith import datablocks

from IO import tree, un

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
#    Node.MSL = modulestyles.MS_Library(modules)
    
    datablocks.TTAGS, datablocks.BTAGS, datablocks.DOCUMENT, datablocks.TSTYLES, datablocks.BSTYLES = tree.deserialize(doc)

    import keyboard
    from state.contexts import Text
    from edit import cursor, caramel
    
    # aim editor objects
    caramel.delight = caramel.Channels_controls(DATA['contexts']['channels'])
    keyboard.keyboard = keyboard.Keyboard(constants.shortcuts)
    cursor.fcursor = cursor.PlaneCursor( * DATA['contexts']['text'] )
    
    datablocks.DOCUMENT.layout_all()
    Text.update()

    # start undo tracking
    un.history = un.UN() 
    
    from interface import karlie, taylor
    
    taylor.becky = taylor.Document_view(save, DATA['view'])
    noticeboard.refresh_properties_type.push_change(DATA['view']['mode'])
    karlie.klossy = karlie.Properties(DATA['view']['mode'], partition=1 )

    un.history.save()
