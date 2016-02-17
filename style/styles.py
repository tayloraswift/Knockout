from itertools import chain
from libraries.freetype import ft_errors

from bulletholes.counter import TCounter as Counter

from style import fonts
from state import constants

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

class Layer(dict):
    def __init__(self, DNA):
        dict.__init__(self, DNA)
        self.Z = {A: None for A in DNA}
        self.members = []
    
    def overlay(self, D, B):
        for A, V in D.items():
            self[A] = V
            self.Z[A] = B

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

class P_Library(_Active_list):
    def __init__(self):
        self.template = DB_Parastyle()
        
        self._projections = {}
        self._font_projections = {}
        
        self.update_f = self._font_projections.clear
    
    def populate(self, active_i, D):
        _Active_list.__init__(self, active_i, (cast_parastyle(P.copy(), {PTAGS[T]: V for T, V in count.items()}) for P, count in D))
    
    def project_p(self, PP):
        P = PP.P
        EP = PP.EP
        H = hash(frozenset(P.items()))
        if EP:
            H += 13 * id(PP)
        
        try:
            return self._projections[H]
        except KeyError:
            # iterate through stack
            projection = Layer(P_DNA)
            effective = (b for b in self if b.tags <= P)
            if EP:
                effective = chain(effective, [EP])
            for B in effective:
                projection.overlay(B.attributes, B)
                projection.members.append(B)
            
            self._projections[H] = projection
            return projection
    
    def project_f(self, PP, F):
        P = PP.P
        EP = PP.EP
        H = 22 * hash(frozenset(P.items())) + hash(frozenset(F.items())) # we must give paragraph a different factor if a style has the same name as a fontstyle
        if EP:
            H += 13 * id(PP)
        
        try:
            return self._font_projections[H]
        except KeyError:
            # add tag groups
            F = F.concat(Counter(chain.from_iterable((FTAGS[G] for G in T.groups) for T, n in F.items() if n)))
            # iterate through stack
            projection = Layer(F_DNA)
            effective = (b for b in self if b.tags <= P)
            if EP:
                effective = chain(effective, [EP])
            for B in effective:
                for C in (c for c in B.layerable if c.tags <= F and c.F is not None):
                    projection.overlay(C.F.attributes, C)
                    projection.members.append(C)

            # set up fonts
            try:
                projection['fontmetrics'] = fonts.Memo_font(projection['path'])
                projection['font'] = fonts.get_cairo_font(projection['path'])
            except ft_errors.FT_Exception:
                path = F_DNA['path']
                projection['color'] = F_DNA['color']
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

class DB_Fontstyle(_DB):
    def __init__(self, fdict={}, name='New fontclass'):
        _DB.__init__(self, name, library=FONTSTYLES)
        self.attributes = fdict.copy()
        
#        ('path', 'fontsize', 'tracking', 'color')
    def polaroid(self):
        return self.attributes.copy()

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

def cast_parastyle(pdict, count):
    if 'fontclasses' in pdict:
        i, E = pdict.pop('fontclasses')
        layerable = _F_layers(i, (_F_container(FONTSTYLES[F], Counter({FTAGS[T]:V for T, V in tags.items()})) for F, tags in E))
    else:
        layerable = _F_layers()
    return DB_Parastyle(pdict, layerable, Counter(count))

class DB_Parastyle(object):
    def __init__(self, A=None, layerable=None, count=None):
        if count is None:
            self.tags = Counter()
        else:
            self.tags = count
        if layerable is None:
            self.layerable = _F_layers()
        else:
            self.layerable = layerable
        if A is None:
            self.attributes = {}
        else:
            self.attributes = A
        
#        ('leading', 'indent', 'indent_range', 'margin_bottom', 'margin_top', 'margin_left', 'margin_right', 'hyphenate')
    def polaroid(self):
        pdict = self.attributes.copy()
        if self.layerable:
            pdict['fontclasses'] = self.layerable.polaroid()
        return pdict, {T.name: V for T, V in self.tags.items()}

    def copy(self):
        return DB_Parastyle(self.attributes.copy(), self.layerable.copy(), self.tags.copy())
    
    def __bool__(self):
        return bool(self.layerable) or bool(self.attributes)
    
    def __eq__(self, other):
        if not self and not other:
            return True
        else:
            return id(self) == id(other)
          

class Tag(_DB):
    def __init__(self, library, name, groups, is_group = False):
        _DB.__init__(self, name, library)
        self.groups = groups
        self.is_group = is_group
    def polaroid(self):
        return (self.name, self.groups)
    

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
    
    def add_slot(self):
        if self.active is not None:
            current = self.active.name
        else:
            current = 'New tag.000'
        name = _new_name(current, self)
        self[name] = Tag(self, name, [])
    
    def delete_slot(self, key):
        del self[key]

P_DNA = {}
F_DNA = {}

FTAGS = T_Library()
PTAGS = T_Library()

FONTSTYLES = {}
PARASTYLES = P_Library()

ISTYLES = {}

# interface styles
def _create_interface():
    font_projections = {}
    FD = TREES(DB_Fontstyle, constants.interface_fstyles)
    P = [_F_container(FD[F], Counter(tags)) for F, tags in constants.interface_pstyle]
    ui_styles = ((), ('title',), ('strong',), ('label',))
    for U in ui_styles:
        F = Counter(U)
        # iterate through stack
        projection = F_DNA.copy()

        for C in (c.F for c in P if c.tags <= F):
            projection.update(C.attributes)

        # set up fonts
        try:
            projection['fontmetrics'] = fonts.Memo_font(projection['path'])
            projection['font'] = fonts.get_cairo_font(projection['path'])
        except ft_errors.FT_Exception:
            path = F_UNDEFINED.u_path
            projection['fontmetrics'] = fonts.Memo_font(path)
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
    F_DNA.update({'fontsize': 13,
            'path': 'style/Ubuntu-R.ttf',
            'tracking': 0,
            'shift': 0,
            'capitals': False,
            'color': (1, 0.15, 0.2, 1)})
    
    P_DNA.update({'hyphenate': False,
            'indent': (0, 0, 0),
            'indent_range': {0},
            'leading': 22,
            'margin_bottom': 0,
            'margin_left': 0,
            'margin_right': 0,
            'margin_top': 0,
            'align': 1})

    ISTYLES.update(_create_interface())
