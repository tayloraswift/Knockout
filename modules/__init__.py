from itertools import chain
from . import table, pie, fraction, bounded, root, mi, image, pagenumber, plot
from elements import elements
from model import olivia

MODS = [elements, olivia] + [table, pie, fraction, bounded, root, mi, image, pagenumber, plot]

modules = {nodetype.name: nodetype for nodetype in chain.from_iterable(module.members for module in MODS)}

inlinetags = set(nodetype.name for nodetype in chain.from_iterable(module.members for module in MODS if module.inline))
blocktags = set(nodetype.name for nodetype in chain.from_iterable(module.members for module in MODS if not module.inline))
textfacing = set(nodetype.name for nodetype in chain.from_iterable(module.members for module in MODS) if nodetype.textfacing)
