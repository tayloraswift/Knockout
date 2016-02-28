from math import log10
from bisect import bisect

from model.olivia import Block, Atomic_text
from elements.elements import Block_element
from model.george import Subcell
from model.cat import cast_mono_line

def generate_key(FLOW, subcell, c, top, py, P):
    ky = [top - py]
    for S in FLOW:
        S.cast(subcell, c, ky[-1] + py, P)
        ky.append(S.y - py + 4)
    return ky, list(zip(ky, ky[1:]))

class Cartesian(Block_element):
    namespace = '_graph'
    DNA = {'x': {}, 'y': {}, 'dataset': {}, 'num': {}}

    def U(self, x):
        return x
    def U_1(self, u):
        return u
    
    def V(self, y):
        return y
    def V_1(self, v):
        return v
    
    def _load(self, L):
        self._tree = L
        self.PP = L[0][2]
        
        self._graphheight, self._tw = self._get_attributes(self.namespace)
        
        (xstart, xstep, xminor, xmajor, xevery, xstop), xlabel = next((tuple(self._get_attributes('x', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':x')
        (ystart, ystep, yminor, ymajor, yevery, ystop), ylabel = next((tuple(self._get_attributes('y', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':y')
        
        datasets, labels = zip( * (( tuple(self._get_attributes('dataset', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':dataset'))
        
        # horizontal computations
        datavalues, self._datacolors = zip( * datasets )

        Xrange = xstop - xstart
        xticks = int(Xrange/xstep)
                        #   pos    |     minor     |     major     |    str bool   |         str             |
        self._xnumbers = [(b/xticks, not b % xminor, not b % xmajor, not b % xevery, str(self.U_1(xstart + b*xstep))) for b in range(xticks + 1)]
        
        yrange = ystop - ystart
        yticks = int(yrange/ystep)
                          #   pos                    |     minor     |     major     |    str bool   |            str          |
        self._ynumbers = [(self._graphheight*b/yticks, not b % yminor, not b % ymajor, not b % yevery, str(self.V_1(ystart + b*ystep))) for b in range(yticks + 1)]
        
        self.process_data(datavalues, xstart, Xrange, ystart, yrange)
        
        self._FLOW = [Atomic_text(text) for text in (xlabel, ylabel) + labels]
    
    def ink_annot(self, cr):
        cr.set_source_rgba( * self._datacolors[-1] )
        
    def regions(self, x, y):
        if y > 0:
            return 0
        elif y < -self._graphheight and x < self._yaxis_div:
            return 1
        else:
            return 2 + min(len(self._FLOW) - 3, max(0, bisect(self._ki, y) - 1))
    
    def transform_data(self, width):
        pass
    
    def typeset(self, bounds, c, y, overlay):
        P_x, P_y, P_key, = self._modstyles(overlay, 'x', 'y', 'dataset', cls=Cartesian)
        F_num, = self._modstyles(None, 'num')

        top = y
        left, right = bounds.bounds(y + self._graphheight/2)

        # y axis
        self._FLOW[1].cast(Subcell(bounds, -0.15, 0.15), c, y, P_y)
        y = self._FLOW[1].y
        
        px = left
        py = int(y + self._graphheight) + 10
        
        self._printed_numbers = []
        # y labels
        for ly, m, M, s, k in self._ynumbers:
            if s:
                YT = cast_mono_line({'R': 0, 'l': 0, 'c': c, 'page': bounds.page}, k, 13, self.PP, F_num)
                YT['x'] = -YT['advance'] - 10
                YT['y'] = -ly + 4
                self._printed_numbers.append(YT)
                
        # x axis
        w = right - left
        self._yaxis_div = w*0.15
        self._origins = []
        self._FLOW[0].cast(bounds, c, py + 20, P_x)
        
        for b, m, M, s, k in self._xnumbers:
            x = int(b*w)
            if s:
                XT = cast_mono_line({'R': 0, 'l': 0, 'c': c, 'page': bounds.page}, k, 13, self.PP, F_num)
                XT['x'] = x - XT['advance']/2
                XT['y'] = 20
                self._printed_numbers.append(XT)
            self._origins.append(x)
        
        self._ki, self._ky = generate_key(self._FLOW[2:], Subcell(bounds, 0.2, 1), c, top, py, P_key)
        
        self.transform_data(w)
        
        return GraphBlock(self._FLOW, self._printed_numbers, 
                    (top, self._FLOW[0].y, left, right), 
                    self.ink_graph, self.ink_annot, 
                    (px, py), self.regions, self.PP)
        
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
