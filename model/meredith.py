from model import olivia
from model import george
from IO import kevin

class Meredith(list):
    def __init__(self, kitty, grid):
        list.__init__(self, (olivia.Chained_text(kevin.deserialize(k['text']), george.Washington([george.Swimming_pool( * c ) for c in k['outline']])) for k in kitty if k['outline']))
        self.page_grid = grid
    
    def recalculate_all(self):
        for tract in self:
            tract.deep_recalculate()

    def add_tract(self):
        self.append( olivia.Chained_text(kevin.deserialize('<p>{new}</p>'), george.Washington([self[-1].channels.generate_channel()])) )
        self.recalculate_all()
    
    def delete_tract(self, tract):
        t = self.index(tract)
        del self[t]

