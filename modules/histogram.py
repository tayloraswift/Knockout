from itertools import chain, accumulate
from bisect import bisect

from model.olivia import Atomic_text
from model.cat import cast_mono_line
from model.george import Subcell
from elements.elements import Block_element
from interface.base import accent

from modules._graph import generate_key, GraphBlock

_namespace = 'mod:hist'

class _Pie(object):
    def __init__(self, slices, radius, active=0):
        self.slices = slices
        self.active = active
        self.r = radius
        self.center = (0, 0)

class Histogram(Block_element):
    namespace = _namespace
    tags = {_namespace + ':' + T for T in ('x', 'y', 'dataset')}
    DNA = {'x': {}, 'y': {}, 'dataset': {}, 'num': {}}
    
    ADNA = {_namespace: [('height', 89, 'int'), ('tickwidth', 0.5, 'float')],
            'x': [('start', 0, 'float'), ('step', 1, 'float'), ('minor', 1, 'int'), ('major', 2, 'int'), ('every', 2, 'int')],
            'y': [('start', 0, 'float'), ('step', 22.25, 'float'), ('minor', 1, 'int'), ('major', 2, 'int'), ('every', '2', 'int'), ('stop', 89, 'float')],
            'dataset': [('data', (), 'float tuple'), ('color', '#ff3085', 'rgba')]}
    documentation = [(0, _namespace), (1, 'x'), (1, 'y'), (1, 'dataset')]
    
    def _load(self, L):
        self._tree = L
        self.PP = L[0][2]
        
        self._graphheight, self._tw = self._get_attributes(_namespace)
        
        (xstart, xstep, xminor, xmajor, xevery), xlabel = next((tuple(self._get_attributes('x', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':x')
        (ystart, ystep, yminor, ymajor, yevery, ystop), ylabel = next((tuple(self._get_attributes('y', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':y')
        
        datasets, labels = zip( * (( tuple(self._get_attributes('dataset', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':dataset'))
        
        # horizontal computations
        datavalues, self._barcolors = zip( * ((tuple(dataset), attrs) for dataset, attrs in datasets) )
        bins = max(len(VV) for VV in datavalues)
                        #   pos  |     minor     |     major     |    str bool   |      str            |
        self._xnumbers = [(b/bins, not b % xminor, not b % xmajor, not b % xevery, str(xstart + xstep*b)) for b in range(bins + 1)]
        yrange = ystop - ystart
        yticks = int(yrange/ystep)
                          #   pos                    |     minor     |     major     |    str bool   |         str         |
        self._ynumbers = [(self._graphheight*b/yticks, not b % yminor, not b % ymajor, not b % yevery, str(ystart + b*ystep)) for b in range(yticks + 1)]
        self._barheights = [[self._graphheight*value/yrange for value in VV] for VV in datavalues]
        self._bins = bins
        
        self._FLOW = [Atomic_text(text) for text in (xlabel, ylabel) + labels]
    
    def draw_bars(self, cr):
        barorigins = list(zip(self._origins, self._origins[1:]))
        
        # ticks
        # x
        tw = self._tw
        cr.set_source_rgb(0, 0, 0)
        for i, x in enumerate(self._origins):
            if self._xnumbers[i][2]:
                cr.rectangle(x, 0, tw, 8)
            elif self._xnumbers[i][1]:
                cr.rectangle(x, 0, tw, 4)
        # y
        for y, m, M, s, k in self._ynumbers:
            if M:
                cr.rectangle(0, -int(round(y)), -8, -tw)
            elif m:
                cr.rectangle(0, -int(round(y)), -4, -tw)
        cr.fill()
        
        # bars
        end = self._origins[-1]
        
        tide = [0] * self._bins
        for barset, color, (k1, k2) in zip(self._barheights, self._barcolors, self._ky):
            cr.set_source_rgba( * color )
            for i, ((x1, x2), bar) in enumerate(zip(barorigins, barset)):
                cr.rectangle(x1, -tide[i], x2 - x1, -bar)
                tide[i] += bar
            # key
            cr.rectangle(end, k1 + 4, -4, k2 - k1 - 4)
            cr.fill()
    
    def bar_annot(self, cr):
        cr.set_source_rgba( * self._barcolors[-1] )
        
    def regions(self, x, y):
        if y > 0:
            return 0
        elif y < -self._graphheight and x < self._yaxis_div:
            return 1
        else:
            return 2 + min(len(self._barheights) - 1, max(0, bisect(self._ki, y) - 1))
    
    def typeset(self, bounds, c, y, overlay):
        P_x, P_y, P_key, = self._modstyles(overlay, 'x', 'y', 'dataset')
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
        
        return GraphBlock(self._FLOW, self._printed_numbers, 
                    (top, self._FLOW[0].y, left, right), 
                    self.draw_bars, self.bar_annot, 
                    (px, py), self.regions, self.PP)
