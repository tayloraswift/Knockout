import pprint, pickle, ast

from fonts import fonts, styles

from state import constants

from model import meredith, penclick, cursor
from model import kevin

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
    contexts = {'t': meredith.mipsy.tracts.index(meredith.CText.tract),
            'c': meredith.mipsy.C(), 
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
    
    penclick.page = penclick.Page(doc['page'])
    meredith.mipsy = meredith.Meredith(doc['kitty'], grid=doc['grid'], ctxs=doc['contexts'])
        
    from interface import taylor
    taylor.becky = taylor.Document_view(doc['view'])
    from model import un
    un.history.save()

