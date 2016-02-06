import pprint, ast

from style import fonts, styles
from state import constants
from state.contexts import Text
from model import meredith, page
from edit import cursor, caramel
from IO import kevin, un
from typing import typing
from interface import karlie, taylor, poptarts

shortcuts = [
        ('Ctrl equal', 'Ctrl plus', 'sup'),
        ('Ctrl minus', 'Ctrl underscore', 'sub'),
        ('Ctrl b', 'Ctrl B', 'strong'),
        ('Ctrl i', 'Ctrl I', 'emphasis')
        ]

def save():
    from interface import taylor
    kitty = [
            {
            'text': kevin.serialize(t.text), 
            'outline': [(c.railings, c.page) for c in t.channels.channels], 
            } 
            for t in meredith.mipsy]
    
    page = {
            'dimensions': (meredith.page.WIDTH, meredith.page.HEIGHT),
            'dual': meredith.page.dual
            }
    
    grid = meredith.mipsy.page_grid
    textcontexts = cursor.fcursor.polaroid()
    channelcontexts = {'t': meredith.mipsy.index(caramel.delight.TRACT),
                    'c': caramel.delight.C(), 
                    'p': caramel.delight.PG
                    }
    
    PPP = styles.PARASTYLES.polaroid()
    FFF = {N: F.polaroid() for N, F in styles.FONTSTYLES.items()}
    
    GGG = {N: G.polaroid() for N, G in styles.PEGS.items()}
    PTT = [T.polaroid() for T in styles.PTAGS.values() if not T.is_group]
    FTT = [T.polaroid() for T in styles.FTAGS.values() if not T.is_group]

    doc = {'kitty': kitty, 'grid': grid, 'contexts': {'text': textcontexts, 'channels': channelcontexts}, 'PARASTYLES': PPP, 'FONTSTYLES': FFF, 'PTAGLIST': PTT, 'FTAGLIST': FTT, 'PEGS': GGG, 'view': taylor.becky.read_display_state(), 'page': page}
    
    with open(constants.filename, 'w') as fi:
        pprint.pprint(doc, fi, width=120)

def load(name):
    with open(name, 'r') as fi:
        constants.filename = name
        doc = ast.literal_eval(fi.read())

    with open('r:X.html', 'r') as fi:
        D = fi.read()

    styles.daydream()
    styles.faith(doc)
    
    doc['kitty'][0]['text'] = D
    
    # set up page, tract model, page grid objects
    meredith.page = page.Page(doc['page'])
    meredith.mipsy = meredith.Meredith(doc['kitty'], grid=doc['grid'])
    
    # aim editor objects
    cursor.fcursor = cursor.FCursor(doc['contexts']['text'])
    caramel.delight = caramel.Channels_controls(doc['contexts']['channels'], poptarts.Sprinkles())
    typing.keyboard = typing.Keyboard(shortcuts)
    
    meredith.mipsy.recalculate_all()
    Text.update()

    # start undo tracking
    un.history = un.UN() 

    taylor.becky = taylor.Document_view(save, doc['view'])
    karlie.klossy = karlie.Properties(tabs = (('page', 'M'), ('tags', 'T'), ('paragraph', 'P'), ('font', 'F'), ('pegs', 'G')), default=2, partition=1 )

    un.history.save()

