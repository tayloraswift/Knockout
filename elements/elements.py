from style.styles import DB_Parastyle
from IO.xml import print_attrs, print_styles
from state.exceptions import IO_Error
from edit.paperairplanes import interpret_int, interpret_float, interpret_float_tuple, interpret_enumeration, interpret_rgba, interpret_bool, interpret_haylor, interpret_tsquared, function_x

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

class _Fontpost(object):
    def __init__(self, F):
        self.F = F

    def __eq__(self, other):
        return type(other) is self.__class__ and other.F is self.F

class OpenFontpost(_Fontpost):
    def __str__(self):
        return '<f>'

    def __repr__(self):
        if self.F.name in textstyles:
            return '<' + textstyles[self.F.name] + '>'
        else:
            return '<f class="' + self.F.name + '">'

    def __len__(self):
        return 3

class CloseFontpost(_Fontpost):
    def __str__(self):
        return '</f>'

    def __repr__(self):
        if self.F.name in textstyles:
            return '</' + textstyles[self.F.name] + '>'
        else:
            return '</f class="' + self.F.name + '">'

    def __len__(self):
        return 4

class Mod_element(object):
    namespace = '_undef'
    tags = {}

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
                'fx': function_x}
    
    def __init__(self, L, deserialize, ser):
        self._DESR = deserialize
        self._SER = ser
        self._load(L)
    
    def transfer(self, B):
        try:
            E = self._DESR(B, fragment = True)
        except (IO_Error, IndexError):
            return False
        
        # locate rebuilt object
        try:
            O = next(e for e in E if type(e) is self.__class__)._tree #yes, we are building an entirely new object and taking its image
        except StopIteration:
            return False
        self._load(O)
        return True

    def _modstyles(self, X, * tags, cls=None):
        if cls is None:
            cls = self.__class__
        modstyles = self.MSL[cls]
        if X is None:
            return (modstyles[tag].copy() for tag in tags)
        else:
            return (X + modstyles[tag] for tag in tags)
    
    def _get_attributes(self, tag, tree=None):
        if tree is None:
            tree = self._tree[0][1]
        inload = self._inload
        return (inload[TYPE](tree[k]) if k in tree else inload[TYPE](v) for k, v, TYPE in self.ADNA[tag])
    
    def get_documentation(self):
        ADNA = self.ADNA
        return [(indent, key, ADNA.get(key, [])) for indent, key in self.__class__.documentation]

    def __len__(self):
        return 1989

class Block_element(Mod_element):
    namespace = '_undef_block'
    
    def represent(self, indent):
        name, attrs = self._tree[0][:2]
        attrs.update(print_styles(self.PP))
        lines = [[indent, '<' + print_attrs(name, attrs) + '>']]
        for tag, E in self._tree[1]:
            lines.append([indent + 1, '<' + print_attrs( * tag ) + '>'])
            lines += self._SER(E, indent + 2)
            lines.append([indent + 1, '</' + tag[0] + '>'])
        lines.append([indent, '</' + self.namespace + '>'])
        return lines
        
class Inline_element(Mod_element):
    namespace = '_undef_inline'

    def represent(self, indent):
        lines = [[indent, '<' + print_attrs( * self._tree[0] ) + '>']]
        for tag, E in self._tree[1]:
            content = self._SER(E, indent + 2)
            content[0] = [indent + 1, '<' + print_attrs( * tag ) + '>' + content[0][1]]
            content[-1][1] += '</' + tag[0] + '>'
            
            lines += content
        lines.append([indent, '</' + self.namespace + '>'])
        return lines

class Inline_SE_element(Inline_element):
    def represent(self, indent):
        return [[indent, '<' + print_attrs( * self._tree[0] ) + '/>']]
