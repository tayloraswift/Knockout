from math import sqrt, inf
from itertools import chain
from bisect import bisect

from meredith.paragraph import Blockelement
from olivia.frames import Subcell

from layout.otline import cast_mono_line

from .data import Data
from .cartesian import Cartesian, Axis, LogAxis
from . import slope, histogram, scatterplot, f, surface

_internal_div = 0.15

def search_cell(address, box, cell):
    for b, B in enumerate(box.content):
        if B is cell:
            return address + ((b, B),)
        elif not type(B).textfacing:
            A = search_cell(address + ((b, B),), B, cell)
            if A is not None:
                return A

class Plot_keys(object):
    def __init__(self, DS):
        self._legend = tuple(chain.from_iterable(box.get_legend() for box in DS))
        self._visible_legend = tuple(ds for ds in self._legend if ds.content)
    
    def layout_keys(self, frames, overlay, planes, paint_functions, block_top_u, block_bottom_u, key_shift, key_bottom):
        frames.save_u()
        frames.start(block_top_u)
        keycell = Subcell(frames, 0.2, 1)
        key_u = []
        for dataset in self._visible_legend:
            dataset.layout(keycell, u = frames.read_u(), overlay=overlay)
            u1, u2 = dataset.u_extents()
            kx1, kx2, ky1, kpn = keycell.at(u1 + key_shift)
            ky2 = keycell.at(u2 + key_shift)[2]
            key_u.append(u1 + key_shift)
            dataset.set_key_height(ky2 - ky1)
            
            keycell.space(key_bottom)
            
            paint_functions.append((kpn, (dataset.paint_key, kx2, ky1, inf)))
            planes.append(dataset)
        u_key_bottom = frames.read_u()
        frames.restore_u()
        self._key_u = key_u
        
        if u_key_bottom > block_bottom_u:
            frames.start(u_key_bottom)
            return u_key_bottom
        else:
            return block_bottom_u
    
    def get_color(self):
        if self._legend:
            return self._legend[-1]['color']
        else:
            return None
        
    def which(self, u):
        i = bisect(self._key_u, u) - 1
        return i, self._visible_legend[i]
    
    def __bool__(self):
        return bool(self._visible_legend)

class Plot(Blockelement):
    name = 'mod:plot'
    DNA = Blockelement.DNA + [('height', 'int', 189), ('azm', 'float', 0), ('alt', 'float', 0), ('rot', 'float', 0),
                              ('graph_top', 'float', 20), ('graph_bottom', 'float', 15), ('key_shift', 'float', 4), ('key_bottom', 'float', 4), 
                              ('cl_axes', 'blocktc', 'h1^tablecell'), ('cl_key', 'blocktc', 'key')]
    
    def _load(self):
        system = Cartesian(self.find_nodes(Axis, Axis, Axis), self['azm'], self['alt'], self['rot'])
        self._DS = tuple(self.filter_nodes(Data))
        for box in chain(system, self._DS):
            box.compact(system, -self['height'])
        self._origin = system.to(0, 0, 0)
        self._CS = system
        self._keys = Plot_keys(self._DS)

    def which(self, x, u, r):
        if (r > 1 or r < 0):
            x1, x2, *_ = self._frames.at(u)
            if x <= x2:
                if not self._planeaxes or (u <= self._graph_bottom_u and (x - x1)/(x2 - x1) > _internal_div):
                    if self._keys:
                        _, cell = self._keys.which(u)
                    else:
                        return ()
                else:
                    cell = self._CS[u <= self._graph_top_u]
                body = search_cell((), self, cell)
                return body + cell.which(x, u, r - len(body))
        return ()

    def _layout_axes(self, frames, overlay, planes):
        block_top_u = frames.read_u()
        if len(self._CS) == 2 and self._CS[0].content and self._CS[1].content:
            X, Y = self._CS
            Y.layout(Subcell(frames, -_internal_div, _internal_div), u=block_top_u, overlay=overlay)
            frames.space(self['graph_top'])
            u, x1, x2, y, c, pn = frames.fit(self['height'])
            frames.space(self['graph_bottom'])
            self._graph_bottom_u = frames.read_u()
            X.layout(frames, u=self._graph_bottom_u, overlay=overlay)
            block_bottom_u = frames.read_u()
            planes += [Y, X]
            self._planeaxes = True
            
        else:
            u, x1, x2, y, c, pn = frames.fit(self['height'])
            block_bottom_u = u
            self._planeaxes = False
        self._graph_top_u = u - self['height']
        return x1, x2 - x1, y, c, pn, block_top_u, block_bottom_u
    
    def _layout_block(self, frames, BSTYLE, overlay):
        self._frames = frames

        monos = []
        planes = []
        paint_functions = []
        paint_annot_functions = []
        
        x1, width, y, c, pn, block_top_u, block_bottom_u = self._layout_axes(frames, overlay + self['cl_axes'], planes)
        
        u = self._keys.layout_keys(frames, overlay + self['cl_key'], planes, paint_functions, block_top_u, block_bottom_u, self['key_shift'], self['key_bottom'])
        
        PARENTLINE = {'l': 0, 'c': c, 'page': pn, 'leading': BSTYLE['leading'], 'BLOCK': self}
        
        for E in chain(self._CS, self._DS):
            mono, paint, paint_annot = E.inflate(width, x1, y, PARENTLINE, BSTYLE)
            monos.extend(mono)
            paint_functions.extend((pn, (F, x1, y, Z)) for Z, F in paint)
            #paint_annot_functions.extend((pn, (F, x1, y)) for F in paint_annot)
        paint_functions.sort(key=lambda k: k[1][3])
        
        if all(A.floating for A in self._CS):
            perp_x, perp_y = map(sum, zip( * (A.lettervector for A in self._CS) ))
            mag = sqrt(perp_x**2 + perp_y**2)
            O_label = cast_mono_line(PARENTLINE, 'O', BSTYLE['__runinfo__'], self._CS[0]['cl_variable'])
            O_label.nail_to(x1 + self._origin[0]*width + perp_x,
                            y + self._origin[1]*-self['height'] + perp_y, align=round(perp_x/mag))
            monos.append(O_label)
        
        planes_set = set(planes)
        return u, monos, [], planes, paint_functions, [], lambda O: O in planes_set, self._keys.get_color()

members = [Plot, Axis, LogAxis]
members.extend(chain.from_iterable(D.members for D in (slope, histogram, scatterplot, f, surface)))
