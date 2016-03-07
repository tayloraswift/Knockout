from model import olivia
from model import george
from IO import kevin

class Meredith(list):
    def __init__(self, KT, grid):
        list.__init__(self, (olivia.Repeat_text(kevin.deserialize(T), george.Washington.from_list(C)) if repeat else
                            olivia.Chained_text(kevin.deserialize(T), george.Washington.from_list(C)) for (repeat, T), C in KT))

        self.page_grid = grid
    
    def recalculate_all(self):
        for tract in self:
            tract.deep_recalculate()

    def add_tract(self):
        self.append( olivia.Chained_text(kevin.deserialize('<p>{new}</p>'), george.Washington([self[-1].channels.generate_channel()])) )
        self[-1].deep_recalculate()

    def add_repeat_tract(self):
        self.append( olivia.Repeat_text(kevin.deserialize('<p>{new}</p>'), george.Not_his_markings([self[-1].channels.generate_channel()])) )
        self[-1].deep_recalculate()
        
    def delete_tract(self, tract):
        t = self.index(tract)
        del self[t]
