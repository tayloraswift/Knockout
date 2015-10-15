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
    
    mipsy.reinit(doc['kitty'])
