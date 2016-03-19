from itertools import chain
from style.styles import DB_Parastyle
from IO.xml import print_attrs, print_styles
from state.exceptions import IO_Error
from edit.paperairplanes import interpret_int, interpret_float, interpret_float_tuple, interpret_enumeration, interpret_rgba, interpret_bool, interpret_haylor, interpret_tsquared, function_x, fonttag

textstyles = {'emphasis': 'em', 'strong': 'strong', 'sup': 'sup', 'sub': 'sub'}

class Paragraph(object):
    def __init__(self, counts, element=None):
        self.P = counts
        if element is None:
            self.EP = DB_Parastyle()
        else:
            self.EP = element
        self.I_ = None
    
    def __str__(self):
        return '<p>'
    
    def __repr__(self):
        attrs = print_styles(self)
        return '<' + print_attrs('p', attrs) + '>'

    def __len__(self):
        return 3

class Node(dict):
    nodename = '_node'
    is_root = False
    textfacing = False

    DNA = {}
    ADNA = []
    documentation = []
    
    _inload = {'int': interpret_int,
                'float': interpret_float,
                'float tuple': interpret_float_tuple, 
                'int set': interpret_enumeration,
                'rgba': interpret_rgba,
                'str': str,
                'bool': interpret_bool,
                '1D': interpret_haylor,
                '2D': interpret_tsquared,
                'fx': function_x,
                'ftag': fonttag}

    def __init__(self, name, attrs, content, PP=None):
        self.name = name
        self.attrs = attrs
        self.content = content
        self.PP = PP
        dict.__init__(self, self._attributes())

    def _attributes(self):
        attrs = self.attrs
        inload = self._inload
        return ((k, inload[TYPE](attrs[k])) if k in attrs else (k, inload[TYPE](v)) for k, v, TYPE in self.ADNA)
    
    def get_documentation(self):
        ADNA = self.ADNA
        return [(indent, key, ADNA.get(key, [])) for indent, key in self.__class__.documentation]

    def styles(self, X, * tags):
        modstyles = Node.MSL[self.__class__]
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
    nodename = '_undef'
    is_root = True
    
    def __init__(self, * args, ** kwargs):
        Node.__init__(self, * args, ** kwargs)
        self._load()
    
    def _load(self):
        pass

    def __len__(self):
        return 1989

class Block_element(Mod_element):
    nodename = '_undef_block'

    def print_A(self):
        if self.PP is not None:
            attrs = self.attrs.copy()
            attrs.update(print_styles(self.PP))
        else:
            attrs = node.attrs
        return print_attrs(self.name, attrs)
    
class Inline_element(Mod_element):
    nodename = '_undef_inline'

class _Fontpost(Inline_element):
    textfacing = True
    ADNA = [('class', '_undefined_', 'ftag')]
    
    def _load(self):
        self.F = self['class']
        self.attrs['class'] = self.F

    def __eq__(self, other):
        return type(other) is self.__class__ and other.F is self.F

class OpenFontpost(_Fontpost):
    nodename = 'fo'
    def __str__(self):
        return '<fo/>'

    def __len__(self):
        return 5

class CloseFontpost(_Fontpost):
    nodename = 'fc'
    def __str__(self):
        return '<fc/>'

    def __len__(self):
        return 5
    
members = [OpenFontpost, CloseFontpost]
inline = True

        

