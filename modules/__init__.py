from itertools import chain
from . import table, pie, fraction, bounded, root, mi, image, pagenumber, plot

MODS = [table, pie, fraction, bounded, root, mi, image, pagenumber, plot]

modules = {nodetype.nodename: nodetype for nodetype in chain.from_iterable(module.members for module in MODS)}

inlinetags = set(nodetype.nodename for nodetype in chain.from_iterable(module.members for module in MODS if module.inline))
blocktags = set(nodetype.nodename for nodetype in chain.from_iterable(module.members for module in MODS if not module.inline))
textfacing = set(nodetype.nodename for nodetype in chain.from_iterable(module.members for module in MODS) if nodetype.textfacing)
