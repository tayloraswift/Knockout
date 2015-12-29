import pprint, pickle, ast

from fonts import fonts, styles

from state import constants

from model import meredith, penclick
from model import kevin

def save():
    from interface import taylor
    kitty = [
            {
            'text': kevin.serialize(t.text), 
            'outline': [c.railings + [c.page] for c in t.channels.channels], 
            'cursors': (t.cursor.cursor, t.select.cursor)
            } 
            for t in meredith.mipsy.tracts]
    
    page = {
            'dimensions': (penclick.page.WIDTH, penclick.page.HEIGHT),
            'dual': penclick.page.dual
            }
    
    grid = meredith.mipsy.page_grid
    contexts = {'c': meredith.mipsy.C(), 'p': meredith.mipsy.page_context}
    
    PPP = {N: P.polaroid() for N, P in styles.PARASTYLES.items()}
    FFF = {N: F.polaroid() for N, F in styles.FONTSTYLES.items()}
    
    GGG = {N: G.polaroid() for N, G in styles.PEGS.items()}
    MMM = {N: M.polaroid() for N, M in styles.MAPS.items()}
    TTT = [styles.TAGLIST.active] + [T.polaroid() for T in styles.TAGLIST.ordered]

    doc = {'kitty': kitty, 'grid': grid, 'contexts': contexts, 'PARASTYLES': PPP, 'FONTSTYLES': FFF, 'MAPS': MMM, 'TAGLIST': TTT, 'PEGS': GGG, 'view': taylor.becky.read_display_state(), 'page': page}
    
    with open(constants.filename, 'w') as fi:
        pprint.pprint(doc, fi)

def load(name):
    try:
        with open(name, 'r') as fi:
            constants.filename = name
            doc = ast.literal_eval(fi.read())
    except UnicodeDecodeError:
        with open(name, 'rb') as fi:
            constants.filename = name
            doc = pickle.load(fi)
    styles.daydream()
    styles.faith(doc)
    
    penclick.page = penclick.Page(doc['page'])
    meredith.mipsy = meredith.Meredith(doc['kitty'], grid=doc['grid'], contexts=doc['contexts'])
        
    from interface import taylor
    taylor.becky = taylor.Document_view(doc['view'])
    from model import un
    un.history.save()

