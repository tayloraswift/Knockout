from itertools import chain
from libraries.freetype import ft_errors

from bulletholes.counter import TCounter as Counter

from style import fonts
from state import constants

class _DB(object):
    def __init__(self, name, library):
        self._LIBRARY = library
        self.name = _new_name(name, self._LIBRARY)

    def rename(self, name):
        name = _new_name(name, self._LIBRARY)
        self._LIBRARY[name] = self._LIBRARY.pop(self.name)
        self.name = name

    def clone(self):
        name = _new_name(self.name, self._LIBRARY)
        self._LIBRARY[name] = self._copy(name)
        return self._LIBRARY[name]

    def _copy(self, name):
        return type(self)(self.polaroid(), name)

class Tag(_DB):
    def __init__(self, library, name, groups, is_group = False):
        _DB.__init__(self, name, library)
        self.groups = groups
        self.is_group = is_group
    def polaroid(self):
        return (self.name, self.groups)
    
    def __str__(self):
        return self.name

class T_Library(dict):
    def __init__(self, * args, ** kwargs):
        dict.__init__(self, * args, ** kwargs)
        self.active = None

    def populate(self, L):
        self.clear()
        D = {T[0]: Tag(self, * T) for T in L}
        groups = set(chain.from_iterable(G for T, G in L))
        D.update({G: Tag(self, G, [G], True) for G in groups})
        self.update(D)
    
    def __missing__(self, name):
        print('Warning: a new style tag \'' + name + '\' has been introduced')
        self[name] = Tag(self, name, [])
        return self[name]
    
    def add_slot(self):
        if self.active is not None:
            current = self.active.name
        else:
            current = 'New tag.000'
        name = _new_name(current, self)
        self[name] = Tag(self, name, [])
    
    def delete_slot(self, key):
        del self[key]


FTAGS = T_Library()
PTAGS = T_Library()

from edit.paperairplanes import datatypes, formatable

def _new_name(name, namelist):
    if name in namelist:
        if not (len(name) > 3 and name[-4] == '.' and len([c for c in name[-3:] if c in '1234567890']) == 3):
            name = name + '.001'
        
        serialnumber = int(name[-3:])
        while True:
            if name not in namelist:
                break
            serialnumber += 1
            name = name[:-3] + str(serialnumber).zfill(3)
    return name

class _Layer(dict):
    def __init__(self, DNA):
        dict.__init__(self, DNA)
        self.Z = {A: DNA for A in DNA}
        self.members = []
    
    def overlay(self, B):
        for A, V in B.items():
            self[A] = V
            self.Z[A] = B

class _FLayer(_Layer):
    def vmetrics(self):
        ascent, descent = self['fontmetrics'].vmetrics
        return ascent * self['fontsize'] + self['shift'], descent * self['fontsize'] + self['shift']

class _Active_list(list):
    def __init__(self, active, * args, ** kwargs):
        list.__init__(self, * args, ** kwargs)
        if active is not None:
            active = self[active]
        self.active = active

    def polaroid(self):
        if self.active is None or self.active not in self:
            i = None
        else:
            i = self.index(self.active)
        return i, [P.polaroid() for P in self]

class P_Library(_Active_list):
    def __init__(self):
        self.template = Paragraph_style()
        
        self._projections = {}
        self._font_projections = {}
        
        self.update_f = self._font_projections.clear
    
    def populate(self, active_i, D):
        _Active_list.__init__(self, active_i, (cast_parastyle(P.copy(), count) for P, count in D))
    
    def project_p(self, PP):
        if PP.I_ is None:
            P = PP.P
        else:
            P = PP.P + PP.I_
        EP = PP.EP
        H = hash(frozenset(P.items()))
        if EP:
            H += 13 * id(PP)
        
        try:
            return self._projections[H]
        except KeyError:
            # iterate through stack
            projection = _Layer(Paragraph_style.DNA)
            effective = (b for b in self if b.tags <= P)
            if EP:
                effective = chain(effective, [EP])
            for B in effective:
                projection.overlay(B)
                projection.members.append(B)
            
            self._projections[H] = projection
            return projection
    
    def project_f(self, PP, F):
        if PP.I_ is None:
            P = PP.P
        else:
            P = PP.P + PP.I_
        EP = PP.EP
        H = 22 * hash(frozenset(P.items())) + hash(frozenset(F.items())) # we must give paragraph a different factor if a style has the same name as a fontstyle
        if EP:
            H += 13 * id(PP)
        
        try:
            return self._font_projections[H]
        except KeyError:
            # add tag groups
            F = F + Counter(chain.from_iterable((FTAGS[G] for G in T.groups) for T, n in F.items() if n))
            # iterate through stack
            projection = _FLayer(DB_Fontstyle.DNA)
            effective = (b for b in self if b.tags <= P)
            if EP:
                effective = chain(effective, [EP])
            for B in effective:
                for C in (c for c in B.content if c.tags <= F and c.F is not None):
                    projection.overlay(C.F)
                    projection.members.append(C.F)

            # set up fonts
            try:
                projection['fontmetrics'] = fonts.Memo_font(projection['path'])
                projection['font'] = fonts.get_cairo_font(projection['path'])
            except ft_errors.FT_Exception:
                path = DB_Fontstyle.DNA['path']
                projection['color'] = DB_Fontstyle.DNA['color']
                projection['fontmetrics'] = fonts.Memo_font(path)
                projection['font'] = fonts.get_cairo_font(path)
            
            projection['hash'] = H
            
            self._font_projections[H] = projection
            return projection
    
    def update_p(self):
        self._projections.clear()
        self._font_projections.clear()

    def polaroid(self):
        if self.active is None or self.active not in self:
            i = None
        else:
            i = self.index(self.active)
        return i, [P.polaroid() for P in self]

class _DNA(dict):
    def __init__(self, DNA, attrs):
        dict.__init__(self, DNA)
        self.attrs = attrs

class _Harry(dict):
    literal = {'bool', 'int', 'float', 'str', 'float tuple'}
    
    def _attributes(self):
        DNA = self.ADNA
        literal = self.literal
        inload = datatypes
        for A, V in self.attrs.items():
            default, TYPE = DNA[A]
            if TYPE in literal:
                yield A, V
            else:
                yield A, inload[TYPE](V)
    
    @classmethod
    def default(cls):
        literal = cls.literal
        inload = datatypes
        cls.DNA = _DNA(((A, V) if TYPE in literal else (A, inload[TYPE](V)) for A, (V, TYPE) in cls.ADNA.items()), {A: V for A, (V, TYPE) in cls.ADNA.items()})
    
    def assign(self, A, value):
        TYPE = self.ADNA[A][1]
        data = datatypes[TYPE](value)
        if TYPE in self.literal:
            self.attrs[A] = data
        elif TYPE in formatable:
            self.attrs[A] = formatable[TYPE](data)
        else:
            self.attrs[A] = value
        
        self[A] = data

    def remove_entry(self, A):
        del self.attrs[A]
        del self[A]

    def reduce(self):
        return dict(self)
    
class DB_Fontstyle(_DB, _Harry):
    ADNA = {'fontsize':     (13     , 'float'),
            'path':         ('style/Ubuntu-R.ttf', 'str'),
            'tracking':     (0      , 'float'),
            'shift':        (0      , 'float'),
            'capitals':     (False  , 'bool'),
            'color':        ('1, 0.15, 0.2, 1', 'rgba')}
    
    def __init__(self, attrs=None, name='New fontclass'):
        _DB.__init__(self, name, library=FONTSTYLES)
        if attrs is None:
            self.attrs = {}
        else:
            self.attrs = attrs
        dict.__init__(self, self._attributes())
    
    def polaroid(self):
        return self.attrs.copy()

class _F_container(object):
    def __init__(self, F=None, count=Counter()):
        self.F = F
        self.tags = count
    
    def copy(self):
        return type(self)(self.F, self.tags.copy())
    
    def polaroid(self):
        if self.F is not None:
            N = self.F.name
        else:
            N = None
        return N, {T.name: V for T, V in self.tags.items()}

class _F_layers(_Active_list):
    def __init__(self, active_i=None, E=()):
        _Active_list.__init__(self, active_i, E)
        self.template = _F_container()
    
    def copy(self):
        try:
            i = self.index(self.active)
        except ValueError:
            i = None
        return _F_layers(i, (c.copy() for c in self))

def cast_parastyle(attrs, count={}):
    if 'fontclasses' in attrs:
        i, E = attrs.pop('fontclasses')
        content = _F_layers(i, (_F_container(FONTSTYLES.get(F, None), Counter({FTAGS[T]:V for T, V in tags.items()})) for F, tags in E))
    else:
        content = _F_layers()
    return Paragraph_style(attrs, content, Counter({PTAGS[T]: V for T, V in count.items()}))

class Paragraph_style(_Harry):
    ADNA = {'hyphenate':      (False      , 'bool'),
                'indent':       ('0'        , 'binomial'),
                'indent_range': ('0'        , 'int set'),
                'leading':      (22         , 'float'),
                'margin_bottom':(0          , 'float'),
                'margin_left':  (0          , 'float'),
                'margin_right': (0          , 'float'),
                'margin_top':   (0          , 'float'),
                'align':        (0          , 'float'),
                'align_to':     (''         , 'str'),
                
                'incr_place_value': (13      , 'int'),
                'incr_assign':  ('n + 1'    , 'fn'),
                'show_count':   ('None'   , 'farray')}
    
    def __init__(self, attrs=None, content=None, count=None):
        if count is None:
            self.tags = Counter()
        else:
            self.tags = count
        if content is None:
            self.content = _F_layers()
        else:
            self.content = content
        if attrs is None:
            self.attrs = {}
        else:
            self.attrs = attrs
        dict.__init__(self, self._attributes())
    
    def polaroid(self):
        attrs = self.attrs.copy()
        if self.content:
            attrs['fontclasses'] = self.content.polaroid()
        return attrs, {T.name: V for T, V in self.tags.items()}

    def copy(self):
#        return Paragraph_style(self.attrs.copy(), self.content.copy(), self.tags.copy()) we don't want the user to accidently create duplicate styles
        return Paragraph_style(count=self.tags.copy())
    
    def __bool__(self):
        return bool(self.content) or bool(self.attrs)
    
    def __eq__(self, other):
        if not self and not other:
            return True
        else:
            return id(self) == id(other)

FONTSTYLES = {}
PARASTYLES = P_Library()

ISTYLES = {}

# interface styles
def _create_interface():
    font_projections = {}
    FD = TREES(DB_Fontstyle, constants.interface_fstyles)
    P = [_F_container(FD[F], Counter(tags)) for F, tags in constants.interface_pstyle]
    ui_styles = ((), ('title',), ('strong',), ('label',), ('mono',))
    for U in ui_styles:
        F = Counter(U)
        # iterate through stack
        projection = DB_Fontstyle.DNA.copy()

        for C in (c.F for c in P if c.tags <= F):
            projection.update(C.attrs)

        # set up fonts
        try:
            projection['fontmetrics'] = fonts.Memo_I_font(projection['path'])
            projection['font'] = fonts.get_cairo_font(projection['path'])
        except ft_errors.FT_Exception:
            path = F_UNDEFINED.u_path
            projection['fontmetrics'] = fonts.Memo_I_font(path)
            projection['font'] = fonts.get_cairo_font(path)
        
        font_projections[U] = projection
    return font_projections

def TREES(DB_TYPE, tree):
    return {name: DB_TYPE(v, name) for name, v in tree.items()}

def faith(woods):
    FTAGS.populate(woods['FTAGLIST'])
    PTAGS.populate(woods['PTAGLIST'])
    FONTSTYLES.clear()
    PARASTYLES.clear()

    FONTSTYLES.update(TREES(DB_Fontstyle, woods['FONTSTYLES']))
    
    PARASTYLES.populate( * woods['PARASTYLES'])

def daydream():
    # set up emergency undefined classes
    DB_Fontstyle.default()
    Paragraph_style.default()

    ISTYLES.update(_create_interface())
