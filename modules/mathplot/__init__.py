from math import sqrt

from itertools import chain

from meredith.paragraph import Blockelement
from olivia.frames import Subcell
from layout.line import cast_mono_line

from state.exceptions import LineOverflow

from .data import Data
from .cartesian import Cartesian, Axis
from . import slope

class Plot(Blockelement):
    name = 'mod:plot'
    DNA = Blockelement.DNA + [('height', 'int', 189), ('azm', 'float', 0), ('alt', 'float', 0), ('rot', 'float', 0)]
    
    def _load(self):
        system = Cartesian(self.find_nodes(Axis, Axis, Axis), self['azm'], self['alt'], self['rot'])
        self._FLOW = list(chain(system, self.filter_nodes(Data)))
        for DS in self._FLOW:
            DS.compact(system, -self['height'])
        self._origin = system.to(0, 0, 0)
        self._CS = system
        
    def regions(self, x, y):
        if y > 0:
            return 0
        elif y < -self['height'] and x < self._yaxis_div:
            return 1
        else:
            return len(self._CS) + self._KEY.target(y)
    
    def _layout_block(self, frames, BSTYLE, cascade, overlay):
        u = frames.read_u()
        
        planes = []
        X, Y, * DATA = self._FLOW
        if Y.content and X.content:
            if overlay is not None:
                Y_ol = overlay + Y['class']
                X_ol = overlay + X['class']
            else:
                Y_ol = Y['class']
                X_ol = X['class']
            Y.layout(Subcell(frames, -0.15, 0.15), u=u, overlay=Y_ol)

            frames.space(20)
            u, x1, x2, y, c, pn = frames.fit(self['height'])
            frames.space(20)
            X.layout(frames, u=u, overlay=X_ol)
            u = frames.read_u()
            planes += [Y, X]
        else:
            u, x1, x2, y, c, pn = frames.fit(self['height'])

        ytop = y - self['height']
        width = x2 - x1
        
        slug = {'l': 0, 'c': c, 'page': pn}
        
        monos = []
        paint_functions = []
        paint_annot_functions = []
        for E in self._FLOW:
            mono, paint, paint_annot = E.inflate(width, x1, y, slug, self)
            monos.extend(mono)
            paint_functions.extend((pn, (F, x1, y)) for F in paint)
            #paint_annot_functions.extend((pn, (F, x1, y)) for F in paint_annot)
        
        if all(A.floating for A in self._CS):
            perp_x, perp_y = map(sum, zip( * (A.lettervector for A in self._CS) ))
            mag = sqrt(perp_x**2 + perp_y**2)
            O_label = cast_mono_line(slug, ['O'], 0, self, self._CS[0]['cl_variable'])
            O_label.nail_to(x1 + self._origin[0]*width + perp_x,
                            y + self._origin[1]*-self['height'] + perp_y, align=round(perp_x/mag))
            monos.append(O_label)
        
        return u, monos, [], planes, paint_functions

members = [Plot, Axis]
members.extend(chain.from_iterable(D.members for D in (slope,)))
