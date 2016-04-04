from model.olivia import Block
from elements.node import Block_element
from state.exceptions import LineOverflow

class Rule(Block_element):
    name = 'hr'
    DNA = {}

    ADNA = [('width', 1, 'float'), ('color', '#000000', 'rgba')]
    documentation = [(0, name)]

    def _load(self):
        pass
    
    def typeset(self, bounds, c, y, y2, overlay):

        bottom = y + self['width']
        if bottom > y2:
            raise LineOverflow        
        left, right = bounds.bounds(y)
        def draw(cr):
            cr.set_source_rgba( * self['color'] )
            cr.rectangle(left, y, right - left, self['width'])
            cr.fill()

        return _MBlock(draw, [], y, bottom, left, right, self.PP)

class _MBlock(Block):
    def __init__(self, draw, * args):
        Block.__init__(self, * args )
        self._draw = draw

    def deposit(self, repository):
        repository['_paint'].append((self._draw, 0, 0))

members = [Rule]
inline = False
