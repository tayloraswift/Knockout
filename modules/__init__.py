from itertools import chain
from . import table, pie, fraction, bounded, root, mi, image, pagenumber, histogram, scatterplot, _graph

INLINE = (fraction.Fraction, bounded.Bounded, root.Root, mi.Math_italic, pagenumber.Page_number, image.Image)
BLOCK = (table.Table, pie.PieChart, histogram.Histogram, scatterplot.Scatterplot, _graph.Cartesian)

def _load_module(mods):
    M = {}
    for mcl in mods:
        M[mcl.namespace] = mcl
    return M

modules = _load_module(INLINE + BLOCK)
moduletags = set(modules) | set(chain.from_iterable(v.tags for v in modules.values()))
inlinecontainers = {'p'}.union( * (I.tags for I in INLINE))
inlinetags = set(I.namespace for I in INLINE)
blocktags = set(B.namespace for B in BLOCK)

