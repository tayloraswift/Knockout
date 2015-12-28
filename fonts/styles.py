import itertools

from fonts import fonts
from freetype import ft_errors

class I_TREES(dict):
    def update_tables(self):
        for P in self.values():
            P.update_table()

class Subtag(object):
    def __init__(self, name):
        self.name = name

class Tag(object):
    def __init__(self, tag):
        self.name = tag['name']
        self.collapse = tag['collapse']
        self.exclusive = tag['exclusive']

        self.active = tag['_active']
        self.elements = {s: Subtag(s) for s in tag['subtags']}
    
    def polaroid(self):
        return {'name': self.name,
                'collapse': self.collapse,
                'exclusive': self.exclusive,
                '_active': self.active,
                'subtags': list(self.elements.keys())
                }

class W_TAGLIST(object):
    def __init__(self):
        pass
    
    def populate(self, taglist):
        a = taglist.pop(0)
        self.ordered = [Tag(t) for t in taglist]
        self.active = self.ordered[a]
        self.elements = {t.name: t for t in self.ordered}
        self.elements.update(dict(itertools.chain.from_iterable(t.elements.items() for t in self.ordered)))

# Peg() is just a 2-element list

class DB_Pegs(object):
    def __init__(self, pegs, name):
        self.name = name
        a = pegs[1].pop('_ACTIVE')
        self.elements = pegs[1] #dict
        self.active = self.elements[a]
        if pegs[0]:
            self.applies_to = set(pegs[0])
        else:
            self.applies_to = None
    
    def polaroid(self):
        D = self.elements.copy()
        D['_ACTIVE'] = next(k for k, v in self.elements.items() if v == self.active)
        if self.applies_to:
            C = ''.join(self.applies_to)
        else:
            C = ''
        return (C, D)

class _DB(object):
    def __init__(self, name, library):
        self.name = name
        self._LIBRARY = library

    def rename(self, name):
        # rename on parent
        if name not in self._LIBRARY:
            self._LIBRARY[name] = self._LIBRARY.pop(self.name)
            self.name = name
    
    def next_name(self, name=None):
        if name is None:
            name = self.name
        if len(name) > 3 and name[-4] == '.' and len([c for c in name[-3:] if c in '1234567890']) == 3:
                serialnumber = int(name[-3:])
                while True:
                    serialnumber += 1
                    name = name[:-3] + str(serialnumber).zfill(3)

                    if name not in self._LIBRARY:
                        break
        else:
            name = name + '.001'
        
        return name
    
    def copy(self, name=None):
        if name is None:
            name = self.name
        CC = type(self)(self.polaroid(), name)
        return CC

class _DB_with_inherit(_DB):
    def __init__(self, xdict, I, B, name, library):
        _DB.__init__(self, name, library)
        self._xdict = xdict
        self._i_attributes = I
        self._b_attributes = tuple(b[0] for b in B)

        # link datablocks
        for b, L in B:
            setattr(self, b, L[xdict[b]])

    def _link_inheritance(self, value):
        # inherit
        if value[0]:
            return (True, self._LIBRARY[value[1]])
        else:
            return value

    def link_inheritable(self):
        for A in self._i_attributes:
            setattr(self, A, self._link_inheritance(self._xdict[A]))
        del self._xdict

    def get_i_attribute(self, A):
        V = getattr(self, A)
        if V[0]:
            return V[1].get_i_attribute(A)
        else:
            return V[1]
 
    def read_inherit_name(self, A):
        V = getattr(self, A)
        if V[0]:
            return V[1].name
        else:
            return 'None'

    def polaroid(self):
        E = ((A, getattr(self, A)) for A in self._i_attributes)
        D = {A : (True, V[1].name) if V[0] else V for A, V in E}
        for b in self._b_attributes:
            D[b] = getattr(self, b).name
        return D

    def copy(self, name=None):
        if name is None:
            name = self.name
        CC = type(self)(self.polaroid(), name)
        CC.link_inheritable()
        CC.update_table()
        return CC

class DB_Fontstyle(_DB_with_inherit):
    def __init__(self, fdict, name):
        _DB_with_inherit.__init__(self, 
                xdict = fdict, 
                I = ('path', 'fontsize', 'tracking', 'color'),
                B = (('pegs', PEGS),),
                name = name,
                library = FONTSTYLES)
    
    def update_table(self):
        # update flattened image of attributes for fast access
        for A in self._i_attributes:
            setattr(self, 'u_' + A, self.get_i_attribute(A))

        # set up fonts
        try:
            self.u_fontmetrics = fonts.Memo_font(self.u_path)
            self.u_font = fonts.get_cairo_font(self.u_path)
            self.u_path_valid = True
        except ft_errors.FT_Exception:
            path = F_UNDEFINED.u_path
            self.u_fontmetrics = fonts.Memo_font(path)
            self.u_font = fonts.get_cairo_font(path)
            self.u_path_valid = False

class DB_Map(_DB):
    def __init__(self, mdict, name):
        _DB.__init__(self, name, library = MAPS)
        self.active = mdict.pop('_ACTIVE')
        # link fontstyle datablocks
        self.elements = {k: FONTSTYLES[v] if v is not None else None for k, v in mdict.items()}
    
    def add_slot(self):
        k = ('{New}',)
        self.elements[k] = None
        self.active = k
    
    def delete_slot(self, key=None):
        if key is None or self.active == key:
            del self.elements[self.active]
            if self.elements:
                keys = list(sorted(self.elements.keys()))
                if self.active == keys[0]:
                    self.active = keys[-1]
                else:
                    self.active = keys[0]
            else:
                self.active = None
        else:
            del self.elements[key]
        PARASTYLES.update_tables()

    def polaroid(self):
        D = {k: v.name if v is not None else None for k, v in self.elements.items()}
        D['_ACTIVE'] = self.active
        return D

class DB_Parastyle(_DB_with_inherit):
    def __init__(self, pdict, name):
        _DB_with_inherit.__init__(self, 
                xdict=pdict, 
                I = ('leading', 'indent', 'indent_range', 'margin_bottom', 'margin_top', 'margin_left', 'margin_right', 'hyphenate'),
                B = (('fontclasses', MAPS),),
                name = name,
                library = PARASTYLES)
        
    def update_table(self):
        # update flattened image of attributes for fast access
        for A in self._i_attributes:
            setattr(self, 'u_' + A, self.get_i_attribute(A))

        _tags = TAGLIST.ordered
        # Resolve subtag permutations
        fmap = {K: F if F is not None else F_UNDEFINED for K, F in self.fontclasses.elements.items()} # Map dict
        for tag in (t for t in _tags if t.elements): #only take ones with subtags
            subtags = list(tag.elements.keys())
            for FF in list(fmap.keys()):
                if tag.name in FF:
                    EL = list(FF)
                    EL.remove(tag.name)
                    
                    fmap.update({tuple(sorted( EL + [st] )) : fmap[FF] for st in subtags})

        self.u_stylemap = fmap
        
        # Resolve collapsible tags
        _CPS = [t.elements for t in _tags if t.collapse]
        self.u_collapsible = (set(itertools.chain.from_iterable(_CPS)), _CPS)


def TREES(DB_TYPE, tree):
    return {name: DB_TYPE(v, name) for name, v in tree.items()}

#   PARASTYLE <
#       ...
#       MAP <
#           elements {
#               FONTSTYLE <
#                   ...
#                   PEGS <>
#               >
#           }
#       >
#
#   >

TAGLIST = W_TAGLIST()
PEGS = {}
FONTSTYLES = I_TREES()
MAPS = {}
PARASTYLES = I_TREES()

def faith(woods):
                                     
    TAGLIST.populate(woods['TAGLIST'])
    PEGS.update(TREES(DB_Pegs, woods['PEGS']))
    FONTSTYLES.update(TREES(DB_Fontstyle, woods['FONTSTYLES']))
    MAPS.update(TREES(DB_Map, woods['MAPS']))
    PARASTYLES.update(TREES(DB_Parastyle, woods['PARASTYLES']))

    # link heritable
    for P in PARASTYLES.values():
        P.link_inheritable()
    PARASTYLES.update_tables()

    # set up emergency undefined classes
    global F_UNDEFINED
    F_UNDEFINED = DB_Fontstyle({'fontsize': (False, 13),
                 'path': (False, 'fonts/FreeMono.ttf'),
                 'pegs': 'Standard pegs',
                 'tracking': (False, 0),
                 'color': (False, (1, 0.15, 0.2, 1))}, '_undefined')
    F_UNDEFINED.link_inheritable()
    F_UNDEFINED.update_table()

    for F in FONTSTYLES.values():
        F.link_inheritable()
    FONTSTYLES.update_tables()

