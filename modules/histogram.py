from modules._graph import Cartesian, cart_ADNA

_namespace = 'mod:hist'

class Histogram(Cartesian):
    namespace = _namespace
    tags = {_namespace + ':' + T for T in ('x', 'y', 'dataset')}
    
    ADNA = {_namespace: cart_ADNA['GRAPH'],
            'x': [('start', 0, 'float'), ('step', 1, 'float'), ('minor', 1, 'int'), ('major', 2, 'int'), ('every', 2, 'int')],
            'y': cart_ADNA['y'],
            'dataset': [('data', (), '1D'), ('color', '#ff3085', 'rgba')]}
    documentation = [(0, _namespace), (1, 'x'), (1, 'y'), (1, 'dataset')]
    
    def _load(self, L):
        self._tree = L
        self.PP = L[0][2]
        
        xaxis, xlabel = next((tuple(self._get_attributes('x', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':x')
        yaxis, ylabel = next((tuple(self._get_attributes('y', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':y')
        
        datasets, labels = zip( * (( tuple(self._get_attributes('dataset', tag[1])), E) for tag, E in L[1] if tag[0] == self.namespace + ':dataset'))
        datavalues, self._datacolors = zip( * ((tuple(dataset), attrs) for dataset, attrs in datasets) )
        
        self._bins = max(len(VV) for VV in datavalues)
        xaxis += (xaxis[0] + xaxis[1]*self._bins,)
        
        self._assemble_graph(xaxis, yaxis, (xlabel, ylabel) + labels, datavalues)

    def process_data(self, datavalues, x0, dx, xx, y0, dy, yy):
        return [[self._graphheight*(self.V(y) - y0)/yy for y in VV] for VV in datavalues]
    
    def _draw_data(self, cr, data):
        for rectangle in data:
            cr.rectangle( * rectangle )

    def transform_data(self, width):
        # TRANSFORM POINTS
        barorigins = list(zip(self._origins, self._origins[1:]))

        RR = []
        tide = [0] * self._bins
        for barset in self._data_unscaled:
            rectangles = []
            for i, ((x1, x2), bar) in enumerate(zip(barorigins, barset)):
                rectangles.append((x1, -tide[i], x2 - x1, -bar))
                tide[i] += bar
            RR.append(rectangles)

        return list(zip(RR, self._datacolors, self._ky))
