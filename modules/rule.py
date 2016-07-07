from meredith.paragraph import Blockelement

class Rule(Blockelement):
    name = 'hr'
    DNA = Blockelement.DNA + [('rule_width', 'float', 1), ('color', 'rgba', '#000')]

    def _load(self):
        pass
    
    def _paint(self, cr, render):
        cr.set_source_rgba( * self['color'] )
        cr.rectangle( * self._rect_info )
        cr.fill()
    
    def _layout_block(self, frames, BSTYLE, overlay):
        frames.fit(BSTYLE['leading'])
        u = frames.read_u()
        x1, x2, y, pn = frames.at(u)
        self._rect_info = 0, -BSTYLE['leading']*0.5, x2 - x1, self['rule_width']
        
        return u, [], [], [], [(pn, (self._paint, x1, y, 0))]

members = [Rule]
