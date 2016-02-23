from cairo import ImageSurface, Context, FORMAT_ARGB32

from style.styles import DB_Parastyle
from IO.xml import print_attrs, print_styles
from IO.svg import render_SVG
from state.exceptions import IO_Error

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

    def __init__(self, L, deserialize, ser):
        self._DESR = deserialize
        self._SER = ser
        self._load(L)
    
    def transfer(self, B):
        try:
            E = self._DESR(B, fragment = True)
        except IO_Error:
            return False
        self._load(next(e for e in E if type(e) is self.__class__)._tree) #yes, we are building an entirely new object and taking its image
        return True

    def _modstyles(self, X, * tags):
        modstyles = self.MSL[self.__class__]
        if X is None:
            return (modstyles[tag].copy() for tag in tags)
        else:
            return (X + modstyles[tag] for tag in tags)

class Block_element(Mod_element):
    namespace = '_undef_block'

class Inline_element(Mod_element):
    namespace = '_undef_inline'

    def represent(self, indent):
        lines = [[indent, '<' + print_attrs( * self._tree[0] ) + '>']]
        for tag, E in self._tree[1]:
            content = self._SER(E, indent + 2)
            content[0] = [indent + 1, '<' + print_attrs( * tag ) + '>' + content[0][1]]
            content[-1][1] += '</' + tag[0] + '>'
            
            lines.extend(content)
        lines.append([indent, '</' + self.namespace + '>'])
        return lines

class Inline_SE_element(Inline_element):
    def represent(self, indent):
        return [[indent, '<' + print_attrs( * self._tree[0] ) + '/>']]
