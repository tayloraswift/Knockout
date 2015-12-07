import _pickle as pickle

from fonts import fonts

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
    
    styles = fonts.paragraph_classes
    grid = meredith.mipsy.page_grid
    contexts = {'c': meredith.mipsy.C(), 'p': meredith.mipsy.page_context}
    
    doc = {'kitty': kitty, 'grid': grid, 'contexts': contexts, 'styles': styles, 'view': taylor.becky.read_display_state(), 'page': page}
    
    with open(constants.filename, 'wb') as fi:
        pickle.dump(doc, fi)

def load(name):
    with open(name, 'rb') as fi:
        constants.filename = name
        doc = pickle.load(fi)
    fonts.paragraph_classes = doc['styles']

    # compatibility
    
    for p in fonts.paragraph_classes:
        if 'hyphenate' not in fonts.paragraph_classes[p]:
            fonts.paragraph_classes[p]['hyphenate'] = (False, True)
        
        if not isinstance(p, tuple):
            _r_rename_p(p, ('P', p))


    for t in doc['kitty']:
        if 'cursors' not in t:
            t['cursors'] = 1, 1
    
#    doc['grid'] = [[], []]
#    doc['contexts'] = {'p': 0, 'c': 0}
    
    penclick.page = penclick.Page(doc['page'])
    meredith.mipsy = meredith.Meredith(doc['kitty'], grid=doc['grid'], contexts=doc['contexts'])
        
    from interface import taylor
    taylor.becky = taylor.Document_view(doc['view'])
    from model import un
    un.history.save()

def _r_rename_p(old, new):
    paragraph_classes = fonts.GET()
    for k in paragraph_classes:
        # travel through fontclasses
        if not paragraph_classes[k]['fontclasses'][0]:
            for f in paragraph_classes[k]['fontclasses'][1]:
            
                paragraph_classes[k]['fontclasses'][1][f] = list(paragraph_classes[k]['fontclasses'][1][f])
                
                # inherit flag
                if paragraph_classes[k]['fontclasses'][1][f][0]:
                    
                    paragraph_classes[k]['fontclasses'][1][f][1] = list(paragraph_classes[k]['fontclasses'][1][f][1])
                    
                    if paragraph_classes[k]['fontclasses'][1][f][1] [0] == old:
                        paragraph_classes[k]['fontclasses'][1][f][1] [0] = new
                    
                    paragraph_classes[k]['fontclasses'][1][f][1] = tuple(paragraph_classes[k]['fontclasses'][1][f][1])
                
                else:
                    paragraph_classes[k]['fontclasses'][1][f] = list(paragraph_classes[k]['fontclasses'][1][f])
                    
                    for a in paragraph_classes[k]['fontclasses'][1][f][1]:
                        paragraph_classes[k]['fontclasses'][1][f][1][a] = list(paragraph_classes[k]['fontclasses'][1][f][1][a])
                        # inherit flag
                        if paragraph_classes[k]['fontclasses'][1][f][1][a][0]:
                            
                            paragraph_classes[k]['fontclasses'][1][f][1][a][1] = list(paragraph_classes[k]['fontclasses'][1][f][1][a][1])

                            if paragraph_classes[k]['fontclasses'][1][f][1][a][1] [0] == old:
                                paragraph_classes[k]['fontclasses'][1][f][1][a][1] [0] = new
                            
                            paragraph_classes[k]['fontclasses'][1][f][1][a][1] = tuple(paragraph_classes[k]['fontclasses'][1][f][1][a][1])
                        
                        paragraph_classes[k]['fontclasses'][1][f][1][a] = tuple(paragraph_classes[k]['fontclasses'][1][f][1][a])
                    
                    paragraph_classes[k]['fontclasses'][1][f] = tuple(paragraph_classes[k]['fontclasses'][1][f])

                paragraph_classes[k]['fontclasses'][1][f] = tuple(paragraph_classes[k]['fontclasses'][1][f])
                    
            
        for l in paragraph_classes[k]:
            paragraph_classes[k][l] = list(paragraph_classes[k][l])
            # inherit flag
            if paragraph_classes[k][l][0]:
                if paragraph_classes[k][l][1] == old:
                    paragraph_classes[k][l][1] = new
            
            paragraph_classes[k][l] = tuple(paragraph_classes[k][l])
        
        if k == old:
            paragraph_classes[new] = paragraph_classes[k]
            del paragraph_classes[old]

