from meredith.paragraph import Plane

class Data(Plane):
    name = 'mod:plot:data'
    DNA = [('class', 'blocktc', '_right^key')]
    
    def set_key_height(self, k):
        self._key_height = k
    
    def paint_key(self, cr):
        cr.set_source_rgba( * self['color'] )
        cr.rectangle(0, 0, 4, self._key_height)
        cr.fill()
    
    def get_legend(self):
        return self,
