from model import olivia
from model import george
from IO import kevin

class Meredith(list):
    def __init__(self, KT, grid):
        list.__init__(self, (olivia.Repeat_flowing_text(kevin.deserialize(T), george.Washington.from_list(C)) if repeat else
                            olivia.Chained_flowing_text(kevin.deserialize(T), george.Washington.from_list(C)) for (repeat, T), C in KT))

        self.page_grid = grid
    
    def recalculate_all(self):
        for tract in self:
            tract.layout()

    def _gen_tract(self, cls):
        self.append(cls(kevin.deserialize('<p>{new}</p>'), george.Washington([self[-1].channels.generate_channel()])))
        self[-1].layout()

    def add_tract(self):
        self._gen_tract(olivia.Chained_flowing_text)

    def add_repeat_tract(self):
        self._gen_tract(olivia.Repeat_flowing_text)
        
    def delete_tract(self, tract):
        t = self.index(tract)
        del self[t]
