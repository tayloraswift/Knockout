from model.olivia import Block

def generate_key(FLOW, subcell, c, top, py, P):
    ky = [top - py]
    for S in FLOW:
        S.cast(subcell, c, ky[-1] + py, P)
        ky.append(S.y - py + 4)
    return ky, list(zip(ky, ky[1:]))

class GraphBlock(Block):
    def __init__(self, FLOW, MONO, box, draw, draw_annot, origin, regions, PP):
        Block.__init__(self, FLOW, * box, PP)
        self._origin = origin
        self._MONO = MONO
        self._draw = draw
        self._draw_annot = draw_annot
        self._regions = regions

    def _print_annot(self, cr, O):
        if O in self._FLOW:
            self._draw_annot(cr)
            self._handle(cr)
            cr.fill()
    
    def I(self, x, y):
        if x <= self['right']:
            dx, dy = self._origin
            return self._FLOW[self._regions(x - dx, y - dy)]
        else:
            return self['i']
    
    def deposit(self, repository):
        repository['_paint'].append((self._draw, * self._origin )) # come before to avoid occluding child elements
        repository['_paint_annot'].append((self._print_annot, 0, 0))
        for A in self._FLOW:
            A.deposit(repository)
        for A in self._MONO:
            A.deposit(repository, * self._origin)
