import _pickle as pickle

from fonts import fonts
from model.meredith import mipsy
from model import kevin


def save():
    kitty = [{'text': kevin.serialize(t.text), 'outline': [c.railings for c in t.channels.channels]} for t in mipsy.tracts]
    styles = fonts.paragraph_classes
    
    doc = {'kitty': kitty, 'styles': styles}
    print(doc)
    
    with open('doc.txt', 'wb') as fi:
        pickle.dump(doc, fi)

def load():
    with open('doc.txt', 'rb') as fi:
        doc = pickle.load(fi)
    fonts.paragraph_classes = doc['styles']
    
#    print(fonts.paragraph_classes)
    
    for p in fonts.paragraph_classes:
        if 'hyphenate' not in fonts.paragraph_classes[p]:
            fonts.paragraph_classes[p]['hyphenate'] = (False, True)
    
    mipsy.reinit(doc['kitty'])
