from math import log, log10
from bisect import bisect

from model.olivia import Block, Flowing_text
from elements.elements import Block_element
from model.george import Subcell
from model.cat import cast_mono_line

_namespace = 'mod:_graph'

def generate_key(FLOW, subcell, c, top, py, P):
    ky = [top - py]
    for FTX in FLOW:
        FTX.layout(subcell, c, ky[-1] + py, P)
        ky.append(FTX.y - py + 4)
    return ky, list(zip(ky, ky[1:]))

def soft_int(n, decimals):
    if type(n) is float:
        if n.is_integer():
            n = int(n)
        else:
            n = round(n, decimals)
    return n

cart_ADNA = {'GRAPH': [('height', 89, 'int'), ('tickwidth', 0.5, 'float'), ('round', 13, 'int'), ('log', False, 'bool')],
        'x': [('start', 0, 'float'), ('step', 1, 'float'), ('minor', 1, 'int'), ('major', 2, 'int'), ('every', 2, 'int'), ('stop', 89, 'float')],
        'y': [('start', 0, 'float'), ('step', 22.25, 'float'), ('minor', 1, 'int'), ('major', 2, 'int'), ('every', '2', 'int'), ('stop', 89, 'float')]}
        
class Cartesian(Block_element):
    namespace = '_graph'
    DNA = {'x': {}, 'y': {}, 'dataset': {}, 'num': {}}
    
    def U(self, x):
        return x
    def U_1(self, u):
        return str(soft_int(u, self._roundto)).replace('-', '−')
    
    def lin_V(self, y):
        return y
    def lin_V_1(self, v):
        return str(soft_int(v, self._roundto)).replace('-', '−')
    
    def log_V(self, y):
        if y > 0:
            return log10(y)
        else:
            return self._min
    
    def log_V_1(self, v):
        exp = soft_int(v, self._roundto)
        if -4 < exp < 4:
            return str(10**exp).replace('-', '−')
        else:
            return '10 E ' + str(exp).replace('-', '−')

    def logB_V(self, y):
        if y > 0:
            return log(y, self._logB)
        else:
            return self._min
    
    def logB_V_1(self, v):
        exp = soft_int(v, self._roundto)
        if -4 < exp < 4:
            return str(self._logB**exp).replace('-', '−')
        else:
            return str(self._logB) + ' E ' + str(exp).replace('-', '−')
    
    def _load(self, L):
        self._tree = L
        self.PP = L[0][2]
        
        xaxis, xlabel = next((tuple(self._get_attributes('x', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':x')
        yaxis, ylabel = next((tuple(self._get_attributes('y', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':y')

        datasets, labels = zip( * (( tuple(self._get_attributes('dataset', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':dataset') )
        datavalues, self._datacolors = zip( * datasets )
        
        self._assemble_graph(xaxis, yaxis, (xlabel, ylabel) + labels, datavalues)
    
    def _assemble_graph(self, xaxis, yaxis, labels, datavalues):
        self._graphheight, self._tw, self._roundto, use_log = self._get_attributes(self.namespace)
        
        xstart, xstep, xminor, xmajor, xevery, xstop = xaxis
        ystart, ystep, yminor, ymajor, yevery, ystop = yaxis
        
        if use_log:
            self._min = ystart
            if type(use_log) is int and use_log not in {1, 10}:
                self._logB = use_log
                self.V = self.logB_V
                self.V_1 = self.logB_V_1
            else:
                self.V = self.log_V
                self.V_1 = self.log_V_1
        else:
            self.V = self.lin_V
            self.V_1 = self.lin_V_1
        
        xr = xstop - xstart
        xticks = int(xr/xstep)
        yr = ystop - ystart
        yticks = int(yr/ystep)

                        #   pos    |     minor     |     major     |    str bool   |         str             |
        self._xnumbers = [(b/xticks, not b % xminor, not b % xmajor, not b % xevery, self.U_1(xstart + b*xstep)) for b in range(xticks + 1)]
                          #   pos                    |     minor     |     major     |    str bool   |            str          |
        self._ynumbers = [(self._graphheight*b/yticks, not b % yminor, not b % ymajor, not b % yevery, self.V_1(ystart + b*ystep)) for b in range(yticks + 1)]
        
        self._data_unscaled = self.process_data(datavalues, xstart, xstep, xr, ystart, ystep, yr)
        
        self._FLOW = [Flowing_text(text) for text in labels]
    
    def _draw_grid(self, cr):
        # ticks
        # x
        tw = self._tw
        cr.set_source_rgb(0, 0, 0)
        for i, x in enumerate(self._origins):
            if self._xnumbers[i][2]:
                cr.rectangle(x, 0, tw, 8)
            elif self._xnumbers[i][1]:
                cr.rectangle(x, 0, tw, 4)
     # y || y, m, M, s, k
        for Y             in self._ynumbers:
            if Y[2]:
                cr.rectangle(0, -int(round(Y[0])), -8, -tw)
            elif Y[1]:
                cr.rectangle(0, -int(round(Y[0])), -4, -tw)
        cr.fill()

    def ink_graph(self, cr):        
        self._draw_grid(cr)
        
        # bars
        end = self._origins[-1]
        for data, color, (k1, k2) in self._DRAWDATA:
            cr.set_source_rgba( * color )
            self._draw_data(cr, data)
            # key
            cr.rectangle(end, k1 + 4, -4, k2 - k1 - 4)
            cr.fill()
    
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
        self._FLOW[1].layout(Subcell(bounds, -0.15, 0.15), c, y, P_y)
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
        self._FLOW[0].layout(bounds, c, py + 20, P_x)
        
        for b, m, M, s, k in self._xnumbers:
            x = int(b*w)
            if s:
                XT = cast_mono_line({'R': 0, 'l': 0, 'c': c, 'page': bounds.page}, k, 13, self.PP, F_num)
                XT['x'] = x - XT['advance']/2
                XT['y'] = 20
                self._printed_numbers.append(XT)
            self._origins.append(x)
        
        self._ki, self._ky = generate_key(self._FLOW[2:], Subcell(bounds, 0.2, 1), c, top, py, P_key)
        
        self._DRAWDATA = self.transform_data(w)
        
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
    
    def target(self, x, y):
        if x <= self['right']:
            dx, dy = self._origin
            return self._regions(x - dx, y - dy)
        else:
            return None
    
    def deposit(self, repository):
        repository['_paint'].append((self._draw, * self._origin )) # come before to avoid occluding child elements
        repository['_paint_annot'].append((self._print_annot, 0, 0))
        for A in self._FLOW:
            A.deposit(repository)
        for A in self._MONO:
            A.deposit(repository, * self._origin)
