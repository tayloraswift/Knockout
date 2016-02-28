from model.olivia import Atomic_text
from modules._graph import Cartesian

_namespace = 'mod:hist'

class Histogram(Cartesian):
    namespace = _namespace
    tags = {_namespace + ':' + T for T in ('x', 'y', 'dataset')}
    
    ADNA = {_namespace: [('height', 89, 'int'), ('tickwidth', 0.5, 'float'), ('round', 13, 'int')],
            'x': [('start', 0, 'float'), ('step', 1, 'float'), ('minor', 1, 'int'), ('major', 2, 'int'), ('every', 2, 'int')],
            'y': [('start', 0, 'float'), ('step', 22.25, 'float'), ('minor', 1, 'int'), ('major', 2, 'int'), ('every', '2', 'int'), ('stop', 89, 'float')],
            'dataset': [('data', (), '1D'), ('color', '#ff3085', 'rgba')]}
    documentation = [(0, _namespace), (1, 'x'), (1, 'y'), (1, 'dataset')]
    
    def _load(self, L):
        self._tree = L
        self.PP = L[0][2]
        
        self._graphheight, self._tw, self._roundto = self._get_attributes(_namespace)
        
        (xstart, xstep, xminor, xmajor, xevery), xlabel = next((tuple(self._get_attributes('x', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':x')
        (ystart, ystep, yminor, ymajor, yevery, ystop), ylabel = next((tuple(self._get_attributes('y', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':y')
        
        datasets, labels = zip( * (( tuple(self._get_attributes('dataset', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':dataset'))
        
        # horizontal computations
        datavalues, self._datacolors = zip( * ((tuple(dataset), attrs) for dataset, attrs in datasets) )
        bins = max(len(VV) for VV in datavalues)
                        #   pos  |     minor     |     major     |    str bool   |             str              |
        self._xnumbers = [(b/bins, not b % xminor, not b % xmajor, not b % xevery, str(self.U_1(xstart + xstep*b))) for b in range(bins + 1)]
        yrange = ystop - ystart
        yticks = int(yrange/ystep)
                          #   pos                    |     minor     |     major     |    str bool   |             str              |
        self._ynumbers = [(self._graphheight*b/yticks, not b % yminor, not b % ymajor, not b % yevery, str(self.V_1(ystart + b*ystep))) for b in range(yticks + 1)]
        
        self.process_data(datavalues, xstart, xstep, bins*xstep, ystart, ystep, yrange)
        self._bins = bins
        
        self._FLOW = [Atomic_text(text) for text in (xlabel, ylabel) + labels]

    def process_data(self, datavalues, x0, dx, xx, y0, dy, yy):
        self._barheights = [[self._graphheight*self.V(y - y0)/yy for y in VV] for VV in datavalues]
        
    def ink_graph(self, cr):
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
        for barset, color, (k1, k2) in zip(self._barheights, self._datacolors, self._ky):
            cr.set_source_rgba( * color )
            for i, ((x1, x2), bar) in enumerate(zip(barorigins, barset)):
                cr.rectangle(x1, -tide[i], x2 - x1, -bar)
                tide[i] += bar
            # key
            cr.rectangle(end, k1 + 4, -4, k2 - k1 - 4)
            cr.fill()
