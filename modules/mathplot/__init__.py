from math import sqrt

from itertools import chain

from meredith.paragraph import Blockelement
from olivia.frames import Subcell
from olivia import Tagcounter

from layout.line import cast_mono_line

from state.exceptions import LineOverflow

from .data import Data
from .cartesian import Cartesian, Axis
from . import slope, histogram

class Plot(Blockelement):
    name = 'mod:plot'
    DNA = Blockelement.DNA + [('height', 'int', 189), ('azm', 'float', 0), ('alt', 'float', 0), ('rot', 'float', 0),
                              ('key_shift', 'float', 4), ('key_bottom', 'float', 4)]
    
    def _load(self):
        system = Cartesian(self.find_nodes(Axis, Axis, Axis), self['azm'], self['alt'], self['rot'])
        self._DS = tuple(self.filter_nodes(Data))
        for box in chain(system, self._DS):
            box.compact(system, -self['height'])
        self._origin = system.to(0, 0, 0)
        self._CS = system
        self._legend = tuple(chain.from_iterable(box.get_legend() for box in self._DS))

    def which(self, x, u, r):
        if r:
            if self._planeaxes:
                if u <= self._graph_top_u:
                    return ((1, self._CS[1]), * self._CS[1].which(x, u, r - 1))
                elif x > self.left_edge:
                    if u >= self._graph_bottom_u:
                        return ((0, self._CS[0]), * self._CS[0].which(x, u, r - 1))
        
        return ()

    def _layout_axes(self, frames, overlay, planes):
        block_top_u = frames.read_u()
        if len(self._CS) == 2 and self._CS[0].content and self._CS[1].content:
            X, Y = self._CS
            Y.layout(Subcell(frames, -0.15, 0.15), u=block_top_u, overlay=Y['class'] + overlay)
            frames.space(30)
            u, x1, x2, y, c, pn = frames.fit(self['height'])
            frames.space(10)
            self._graph_bottom_u = frames.read_u()
            X.layout(frames, u=self._graph_bottom_u, overlay=X['class'] + overlay)
            block_bottom_u = frames.read_u()
            planes += [Y, X]
            self._planeaxes = True
            
        else:
            u, x1, x2, y, c, pn = frames.fit(self['height'])
            block_bottom_u = u
            self._planeaxes = False
        self._graph_top_u = u - self['height']
        return x1, x2 - x1, y, c, pn, block_top_u, block_bottom_u
    
    def _layout_keys(self, frames, overlay, planes, paint_functions, block_top_u):
        frames.save_u()
        frames.start(block_top_u)
        keycell = Subcell(frames, 0.2, 1)
        for dataset in (ds for ds in self._legend if ds.content):
            dataset.layout(keycell, u = frames.read_u(), overlay = dataset['class'] + overlay)
            u1, u2 = dataset.u_extents()
            kx1, kx2, ky1, kpn = keycell.at(u1 + self['key_shift'])
            ky2 = keycell.at(u2 + self['key_shift'])[2]
            dataset.set_key_height(ky2 - ky1)
            
            keycell.space(self['key_bottom'])
            
            paint_functions.append((kpn, (dataset.paint_key, kx2, ky1)))
            planes.append(dataset)
        frames.restore_u()
    
    def _layout_block(self, frames, BSTYLE, cascade, overlay):
        monos = []
        planes = []
        paint_functions = []
        paint_annot_functions = []
        
        if overlay is None:
            overlay = Tagcounter()
        x1, width, y, c, pn, block_top_u, block_bottom_u = self._layout_axes(frames, overlay, planes)
        
        self._layout_keys(frames, overlay, planes, paint_functions, block_top_u)
        
        slug = {'l': 0, 'c': c, 'page': pn}
        
        for E in chain(self._CS, self._DS):
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
        
        return block_bottom_u, monos, [], planes, paint_functions

members = [Plot, Axis]
members.extend(chain.from_iterable(D.members for D in (slope, histogram)))
