from itertools import chain

from edit.paperairplanes import literal, reformat, standard
from IO.xml import print_attrs, print_styles




            
class Node(dict):
    name = '_node'
    is_root = False
    textfacing = False

    DNA = {}
    ADNA = []
    documentation = []

    def __init__(self, attrs, content=None, PP=None):
        self.attrs = attrs
        self.content = content
        self.PP = PP
        dict.__init__(self, self._attributes())

    def _attributes(self):
        attrs = self.attrs
        inload = datatypes
        return ((k, inload[TYPE](attrs[k])) if k in attrs else (k, inload[TYPE](v)) for k, v, TYPE in self.ADNA)
    
    def get_documentation(self):
        ADNA = self.ADNA
        return [(indent, key, ADNA.get(key, [])) for indent, key in self.__class__.documentation]

    @classmethod
    def styles(cls, X, * tags):
        modstyles = Node.MSL[cls]
        if X is None:
            return (modstyles[tag].copy() for tag in tags)
        else:
            return (X + modstyles[tag] for tag in tags)

    def find_nodes(self, * classes):
        nodes = [e for e in self.content if isinstance(e, Node)]
        for cls in classes:
            try:
                i = next(i for i, e in enumerate(nodes) if isinstance(e, cls))
                yield nodes.pop(i)
            except StopIteration:
                yield None

    def filter_nodes(self, cls, inherit=False):
        if inherit:
            return (e for e in self.content if isinstance(e, cls))
        else:
            return (e for e in self.content if type(e) is cls)

    def print_A(self):
        return print_attrs(self.name, self.attrs)
    
    def __repr__(self):
        return ''.join(chain('<', repr(self.name), '> {', repr(self.attrs), '} {', repr(self.PP), '} ', repr(self.content)))

class Mod_element(Node):
    name = '_undef'
    is_root = True
    
    def __init__(self, * args, ** kwargs):
        Node.__init__(self, * args, ** kwargs)
        self._load()
    
    def _load(self):
        pass

    def __len__(self):
        return 1989

class Block_element(Mod_element):
    name = '_undef_block'

    def print_A(self):
        if self.PP is not None:
            attrs = self.attrs.copy()
            attrs.update(print_styles(self.PP))
        else:
            attrs = node.attrs
        return print_attrs(self.name, attrs)
    
class Inline_element(Mod_element):
    name = '_undef_inline'

