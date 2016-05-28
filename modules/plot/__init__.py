from bisect import bisect
from itertools import chain

from meredith.paragraph import Plane, Blockelement
from olivia.frames import Subcell
from .cartesian import namespace, Axis, axismembers, Cartesian
from .data import Data
from state.exceptions import LineOverflow

from . import scatterplot, f, histogram

class Plot_key(object):
    def __init__(self, keys, subcell, c, top, py, overlay):
        if keys:
            texts, self._icons, colors = zip( * keys )
            self.color = colors[-1]

            self._i = len(texts) - 1
            y = top
            ky = []
            for FTX in texts:
                FTX.layout(subcell, c, y, overlay)
                leading1 = FTX.LINES[0] ['leading']
                leading2 = FTX.LINES[-1]['leading']
                ky.append((int(y - py + leading1*0.25), int(FTX.y - py + leading2*0.25)))
                y = FTX.y + leading2*0.25
            
            self._ky = ky
            self._ki = [k[1] for k in ky]
        else:
            self._i = -1
            self.color = (0, 0, 0, 1)
            self._icons = ()
            self._ky = []
            self._ki = []
    
    def draw(self, cr):
        for icon, cell in zip(self._icons, self._ky):
            icon(cr, * cell)
    
    def target(self, y):
        return min(self._i, max(0, bisect(self._ki, y)))

class Plot(Blockelement):
    name = namespace
    DNA = [('height', 'int', 89), ('azm', 'float', 0), ('alt', 'float', 'pi*0.5'), ('rot', 'float', 0), ('tickwidth', 'float', 0.5)]
    
    def _load(self):
        system = Cartesian(self.find_nodes(Axis, Axis, Axis))
        
        self._datasets = [PL.unit(system) for PL in self.filter_nodes(Data)]
        self._FLOW = system + self._datasets
        self._CS = system
        self._hk = (None, None)
    
    def ink_graph(self, cr):
        cr.set_source_rgb(0, 0, 0)
        self._CS.draw(cr, self['tickwidth'])
        cr.fill()
        
        for PL in self._datasets:
            PL.draw(cr)
        self._KEY.draw(cr)
    
    def ink_annot(self, cr):
        cr.set_source_rgba( * self._KEY.color )
        
    def regions(self, x, y):
        if y > 0:
            return 0
        elif y < -self['height'] and x < self._yaxis_div:
            return 1
        else:
            return len(self._CS) + self._KEY.target(y)
    
    def typeset(self, bounds, c, y, y2, overlay):
        P_axis, P_key, P_right = self.styles(overlay, 'axis', 'key', '_right')
        F_num, = self.styles(None, 'num')

        top = y
        left, right = bounds.bounds(y + self['height']/2)
        width = right - left
        self._yaxis_div = width*0.15

        # y axis
        self._FLOW[1].layout(Subcell(bounds, -0.15, 0.15), c, y, P_axis)
        y = self._FLOW[1].y
        
        px = left
        py = int(y + self['height']) + 10
        if py > y2:
            raise LineOverflow
        
        hk = (width, -self['height'])
        system = self._CS
        if self._hk != hk:
            self._hk = hk
            system.freeze( * hk )
            for PL in self._datasets:
                PL.freeze(system)
        
        MONO = list(system.yield_numbers({'R': 0, 'l': 0, 'c': c, 'page': bounds.page}, self.PP, F_num))
        
        # x axis
        self._FLOW[0].layout(bounds, c, py + 20, P_axis)
        
        self._KEY = Plot_key(self._keys, Subcell(bounds, 0.2, 1), c, top, py, P_key + P_right)
        
        return GraphBlock(self._FLOW, MONO, 
                    (top, self._FLOW[0].y, left, right), 
                    self.ink_graph, self.ink_annot, 
                    (px, py), self.regions, self.PP)
        

members = [Plot] + axismembers
members += f.members
#members.extend(chain.from_iterable(D.members for D in (scatterplot, f, histogram)))
