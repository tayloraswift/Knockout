from IO import kevin

class Meredith(list):
    def __init__(self, KT, grid):
        list.__init__(self, (section.create_wrapper() for section in KT))

        self.page_grid = grid
    
    def recalculate_all(self):
        for tract in self:
            tract.layout()

    def _gen_tract(self, S):
        self.append(kevin.deserialize(S)[0].create_wrapper())
        self[-1].layout()

    def add_tract(self):
        self._gen_tract('''<section outlines="10,10 10,30 ; 30,10 30,30 ; 0">
    <p>{new}</p>
</section>''')

    def add_repeat_tract(self):
        self._gen_tract('''<section repeat="0:1" outlines="10,10 10,30 ; 30,10 30,30 ; 0">
    <p>{new}</p>
</section>''')
        
    def delete_tract(self, tract):
        t = self.index(tract)
        del self[t]
