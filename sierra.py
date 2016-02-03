import pprint, pickle, ast

from fonts import fonts, styles

from state import constants
from state.contexts import Text

from model import meredith, page, cursor
from model import kevin, un

from typing import typing

from interface import karlie, taylor, caramel, poptarts

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
            for t in meredith.mipsy.tracts]
    
    page = {
            'dimensions': (penclick.page.WIDTH, penclick.page.HEIGHT),
            'dual': penclick.page.dual
            }
    
    grid = meredith.mipsy.page_grid
    contexts = {'t': meredith.mipsy.tracts.index(Tract.tract),
#            'c': meredith.mipsy.C(), 
            'p': meredith.mipsy.page_context,
            'i': cursor.fcursor.i,
            'j': cursor.fcursor.j}
    
    PPP = styles.PARASTYLES.polaroid()
    FFF = {N: F.polaroid() for N, F in styles.FONTSTYLES.items()}
    
    GGG = {N: G.polaroid() for N, G in styles.PEGS.items()}
    PTT = [T.polaroid() for T in styles.PTAGS.values() if not T.is_group]
    FTT = [T.polaroid() for T in styles.FTAGS.values() if not T.is_group]

    doc = {'kitty': kitty, 'grid': grid, 'contexts': contexts, 'PARASTYLES': PPP, 'FONTSTYLES': FFF, 'PTAGLIST': PTT, 'FTAGLIST': FTT, 'PEGS': GGG, 'view': taylor.becky.read_display_state(), 'page': page}
    
    with open(constants.filename, 'w') as fi:
        pprint.pprint(doc, fi, width=120)

def load(name):
    with open(name, 'r') as fi:
        constants.filename = name
        doc = ast.literal_eval(fi.read())

    styles.daydream()
    styles.faith(doc)
    
    # set up page, tract model, page grid objects
    meredith.page = page.Page(doc['page'])
    meredith.mipsy = meredith.Meredith(doc['kitty'], grid=doc['grid'], ctxs=doc['contexts'])
    
    # aim editor objects
    cursor.fcursor = cursor.FCursor(meredith.mipsy.tracts[doc['contexts']['t']], 
            doc['contexts']['i'], 
            doc['contexts']['j'], 
            doc['contexts']['p'],
            doc['contexts']['t'])
    caramel.delight = caramel.Channels_controls(meredith.mipsy.tracts[doc['contexts']['t']], doc['contexts']['p'], poptarts.Sprinkles())
    typing.keyboard = typing.Keyboard(shortcuts)
    
    meredith.mipsy.recalculate_all()
    Text.update()

    # start undo tracking
    un.history = un.UN() 

    taylor.becky = taylor.Document_view(save, doc['view'])
    karlie.klossy = karlie.Properties(tabs = (('page', 'M'), ('tags', 'T'), ('paragraph', 'P'), ('font', 'F'), ('pegs', 'G')), default=2, partition=1 )

    un.history.save()

