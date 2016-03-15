from pprint import pformat
from ast import literal_eval

from style import fonts, styles
from state import constants, noticeboard
from state.contexts import Text
from state.exceptions import Channel_Error
from model import meredith, page
from edit import cursor, caramel
from IO import kevin, un, xml
from typing import typing
from interface import karlie, taylor, poptarts
from modules import modulestyles, modules
from elements.elements import Node

def save():
    HEADER = '<head><meta charset="UTF-8"></head>\n<title>' + constants.filename + '</title>\n\n'
    
    SECTIONS, channels = zip( * (( (type(t).sign, kevin.serialize(t.text)), [(c.railings, c.page) for c in t.channels.channels]) for t in meredith.mipsy))
    SECTIONS = '<body>\n' + '\n\n'.join(sign + section + '\n</section>' for sign, section in SECTIONS) + '\n</body>\n'

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
    
    PTT = [T.polaroid() for T in styles.PTAGS.values() if not T.is_group]
    FTT = [T.polaroid() for T in styles.FTAGS.values() if not T.is_group]

    from interface import taylor
    
    DATA = {'outlines': channels, 'grid': grid, 'contexts': {'text': textcontexts, 'channels': channelcontexts}, 'PARASTYLES': PPP, 'FONTSTYLES': FFF, 'PTAGLIST': PTT, 'FTAGLIST': FTT, 'view': taylor.becky.read_display_state(), 'page': page}
    
    with open(constants.filename, 'w') as fi:
        fi.write(HEADER)
        fi.write(SECTIONS)
        fi.write('\n<!-- #############\n')
        fi.write(pformat(DATA, width=189))
        fi.write('\n############# -->\n')

def load(name):
    with open(name, 'r') as fi:
        constants.filename = name
        doc = fi.read()

    BODY = doc[doc.find('<body>') + 6 : doc.find('</body>')]
    DATA = literal_eval(doc[doc.find('<!-- #############') + 18 : doc.find('############# -->')])
    
    text = []
    for H in BODY.split('<section'):
        tagend = H.find('>') + 1
        end = H.find('</section>')
        section = H[tagend : end].strip()
        if section:
            text.append(( literal_eval(xml.read_tag('<section' + H[:tagend])[1].get('repeat', 'False')), section))
    channels = DATA['outlines']
    
    if len(text) == len(channels):
        KT = zip(text, channels)
    else:
        raise Channel_Error

    # unpack styles
    styles.daydream()
    styles.faith(DATA)
    Node.MSL = modulestyles.MS_Library(modules)
    
    # set up page, tract model, page grid objects
    meredith.page = page.Page(DATA['page'])
    meredith.mipsy = meredith.Meredith(KT, grid=DATA['grid'])
    
    # aim editor objects
    cursor.fcursor = cursor.FCursor(DATA['contexts']['text'])
    caramel.delight = caramel.Channels_controls(DATA['contexts']['channels'], poptarts.Sprinkles())
    typing.keyboard = typing.Keyboard(constants.shortcuts)
    
    meredith.mipsy.recalculate_all()
    Text.update()

    # start undo tracking
    un.history = un.UN() 

    taylor.becky = taylor.Document_view(save, DATA['view'])
    noticeboard.refresh_properties_type.push_change(DATA['view']['mode'])
    karlie.klossy = karlie.Properties(DATA['view']['mode'], partition=1 )

    un.history.save()
