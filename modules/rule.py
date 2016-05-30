from meredith.paragraph import Blockelement

class Rule(Blockelement):
    name = 'hr'
    DNA = [('class', 'blocktc', ''), ('width', 'float', 1), ('color', 'rgba', '#000')]

    def _load(self):
        pass
    
    def _layout_block(self, frames, BSTYLE, cascade, overlay):
        frames.fit(BSTYLE['leading'])
        u = frames.read_u()
        x1, x2, y, pn = frames.at(u)
        def draw(cr):
            cr.set_source_rgba( * self['color'] )
            cr.rectangle(0, -BSTYLE['leading']*0.5, x2 - x1, self['width'])
            cr.fill()
        
        return u, [], [], [], [(pn, (draw, x1, y))]

members = [Rule]
