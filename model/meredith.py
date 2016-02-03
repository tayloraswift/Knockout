from model import olivia
from model import george
from model import kevin

class Meredith(object):
    def __init__(self, kitty, grid, ctxs):
        self.tracts = [olivia.Chained_text(kevin.deserialize(k['text']), george.Washington([george.Swimming_pool( * c ) for c in k['outline']])) for k in kitty if k['outline']]
        self.page_grid = grid
    
    def recalculate_all(self):
        for tract in self.tracts:
            tract.deep_recalculate()

    def add_tract(self):
        self.tracts.append( olivia.Chained_text(kevin.deserialize('<p>{new}</p>'), george.Washington([self.tracts[-1].channels.generate_channel()])) )
        self.recalculate_all()
    
    def delete_tract(self, tract):
        t = self.tracts.index(tract)
        del self.tracts[t]

