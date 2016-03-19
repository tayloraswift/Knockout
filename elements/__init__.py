from itertools import chain
from elements import elements
from model import olivia
import modules

_MODS = [elements, olivia] + modules.use

modules = {nodetype.name: nodetype for nodetype in chain.from_iterable(module.members for module in _MODS)}

inlinetags = set(nodetype.name for nodetype in chain.from_iterable(module.members for module in _MODS if module.inline))
blocktags = set(nodetype.name for nodetype in chain.from_iterable(module.members for module in _MODS if not module.inline))
textfacing = set(nodetype.name for nodetype in chain.from_iterable(module.members for module in _MODS) if nodetype.textfacing)
