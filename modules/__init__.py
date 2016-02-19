from itertools import chain
from . import table, pie, fraction, bounded

INLINE = (fraction, fraction.Fraction), (bounded, bounded.Bounded)
BLOCK = (table, table.Table), (pie, pie.PieChart)

def _load_module(mods):
    M = {}
    for mod, mobj in mods:
        M[mod.namespace] = mobj, mod.tags
    return M

modules = _load_module(INLINE + BLOCK)
moduletags = set(modules) | set(chain.from_iterable(v[1] for v in modules.values()))
inlinetags = {'p'}.union( * (I[0].tags for I in INLINE))
blocktags = set(B[0].namespace for B in BLOCK)

