import _pickle as pickle

from fonts import fonts

from state import constants

from model.meredith import mipsy
from model import kevin


def save():
    kitty = [
            {
            'text': kevin.serialize(t.text), 
            'outline': [c.railings + [c.page] for c in t.channels.channels], 
            'cursors': (t.cursor.cursor, t.select.cursor)
            } 
            for t in mipsy.tracts]
    
    styles = fonts.paragraph_classes
    
    doc = {'kitty': kitty, 'styles': styles}
    
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
    for t in doc['kitty']:
        if 'cursors' not in t:
            t['cursors'] = 1, 1
    
    mipsy.reinit(doc['kitty'])
