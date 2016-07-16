from itertools import chain
from random import randint

from IO.un import history

def random_serial():
    R = set()
    while True:
        r = randint(0, 1989000000)
        if r not in R:
            yield r

def new_name(name, namelist):
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

class Null(object):
    name = '_nullbox'
    textfacing = False
    inline     = False
    plane      = False
    planelevel = False
    
    content    = ()

class Box(dict):
    name = '_box'
    
    textfacing = False  # whether or not contents of this object are to be written on the same line          (contains inline boxes)
    inline     = False  # whether or not this object is to be written on the same line as the preceeding one (contained by a textfacing)
    
    plane      = False  # whether or not this object can function as a plane                                 (contains block objects)
    planelevel = False  # whether or not this object is directly contained by a plane                        (contained by a plane)
    
    DNA = []
    IMPLY = {}
    
    def __init__(self, KT, attrs, content=None):
        self._TTAGS_D, self._BTAGS_D, self._TSTYLES_D = KT.dicts
        self.__literal  = KT.mint.literal
        self.__reformat = KT.mint.reformat
        self.__standard = KT.mint.standard
        self.KT         = KT
        
        if content is None:
            self.content = []
        else:
            self.content = content
        self.attrs = {}
        self.clear()
        dict.__init__(self, self._load_attributes(attrs))
    
    def _load_attributes(self, attrs, DNA=None):
        if DNA is None:
            DNA = self.__class__.DNA
        
        literal  = self.__literal
        reformat = self.__reformat
        standard = self.__standard
        
        for A, TYPE, * default in DNA:
            if TYPE in literal:
                if A in attrs:
                    v = literal[TYPE](attrs[A])
                    self.attrs[A] = v
                    yield A, v
                
                elif default:
                    yield A, literal[TYPE](default[0])
            
            elif TYPE in standard or type(TYPE) is tuple:
                if A in attrs:
                    self.attrs[A] = attrs[A]
                    yield A, standard[TYPE](attrs[A])
                
                elif default:
                    yield A, standard[TYPE](default[0])
            
            elif TYPE in reformat:
                up, down = reformat[TYPE]
                if A in attrs:
                    v = up(attrs[A])
                    self.attrs[A] = down(v)
                    yield A, v
                
                elif default:
                    yield A, up(default[0])

    def before(self):
        history.save() # we need to perform the dot lookup
    
    def after(self, A):
        pass

    def assign(self, A, S):
        try:
            TYPE, * default = next(td for a, * td in self.__class__.DNA if a == A)
        except StopIteration:
            print('Invalid attribute: ' + A)
            return
        
        self.before()
        if TYPE in self.__literal:
            v = self.__literal[TYPE](S)
            self.attrs[A] = v
            self[A] = v
        
        elif TYPE in self.__standard or type(TYPE) is tuple:
            self.attrs[A] = S
            self[A] = self.__standard[TYPE](S)
        
        elif TYPE in self.__reformat:
            up, down = self.__reformat[TYPE]
            v = up(S)
            self.attrs[A] = down(v)
            self[A] = v
        else:
            return
        self.after(A)

    def deassign(self, A):
        if A in self:
            self.before()
            del self.attrs[A]
            del self[A]
            self.update(self._load_attributes(self.attrs, [next(k for k in self.__class__.DNA if A == k[0])]))
            self.after(A)

    def print_A(self):
        attrs = self.attrs
        imply = self.__class__.IMPLY
        if attrs:
            E = ' '.join(''.join((a[0], '="', str(attrs[a[0]]), '"')) for a in self.__class__.DNA if a[0] in attrs and (a[0] not in imply or imply[a[0]] != attrs[a[0]]))
            return self.name + ' ' + E
        return self.name
    
    def copy(self):
        if self.__class__.textfacing:
            content = type(self.content)(e if type(e) is str else e.copy() for e in self.content)
        else:
            content = [e.copy() for e in self.content]
        return self.__class__(self.KT, self.attrs, content)
    
    def __repr__(self):
        if self.content:
            return ''.join(chain((' <', self.name, '> ', repr(self.attrs), ' ', '['), (c if type(c) is str else repr(c) for c in self.content), ('] ',)))
        else:
            return ''.join((' <', self.name, '> ', repr(self.attrs), ' '))

    def __hash__(self):
        return id(self)
    
    def where(self, address):
        i, * address = address
        return self.content[i].where(address)
    

    ## FOR MODULES ##
    def find_nodes(self, * classes):
        boxes = [e for e in self.content if type(e) is not str]
        for cls in classes:
            try:
                yield boxes.pop(next(i for i, e in enumerate(boxes) if isinstance(e, cls)))
            except StopIteration:
                yield None


    def filter_nodes(self, cls):
        return (b for b in self.content if isinstance(b, cls))


_tagDNA = [('name', 'str', '_undef')]

class Texttag(Box):
    name = 'texttag'
    DNA  = _tagDNA
    
    def after(self, A):
        if A == 'name':
            self._TTAGS_D.update_datablocks(self.KT.TTAGS)

class Blocktag(Box):
    name = 'blocktag'
    DNA  = _tagDNA
    
    def after(self, A):
        if A == 'name':
            self._BTAGS_D.update_datablocks(self.KT.BTAGS)

class Datablocks(Box):
    def content_new(self, active=None, i=None):
        if active is None:
            name = self.__class__.defmembername
        else:
            name = active['name']
        O = self.__class__.contains(self.KT, {'name': new_name(name, self._dblibrary)})
        if i is None:
            self.content.append(O)
            self.sort_content()
        else:
            self.content.insert(i, O)
        self.after('__content__')
        return O

    def sort_content(self):
        self.content.sort(key=lambda O: O['name'])
    
    def after(self, A):
        if A == 'name' or A == '__content__':
            self._dblibrary.update_datablocks(self)

class Texttags(Datablocks):
    name = 'texttags'
    defmembername = 'Untitled tag'
    contains = Texttag
    
    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        self._dblibrary = self._TTAGS_D
        self._dblibrary.set_funcs(self)
    
class Blocktags(Datablocks):
    name = 'blocktags'
    defmembername = 'Untitled tag'
    contains = Blocktag

    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        self._dblibrary = self._BTAGS_D
        self._dblibrary.set_funcs(self)

## MODULE BASE CLASSES ##

class Inline(Box):
    inline = True

    def __init__(self, * args, ** kwargs):
        Box.__init__(self, * args, ** kwargs)
        self._load()
    
    def _load(self):
        raise NotImplementedError
    
    def layout_inline(self, * I ):
        self._cast( * self._cast_inline( * I ) )
    
    def _cast(self, lines, width, A, D, paint=None, paint_annot=None):
        self._LINES = lines
        self.width = width
        self.ascent = A
        self.descent = D
        self.__paint = paint
        self.__paint_annot = paint_annot
    
    def deposit_glyphs(self, repository, x, y):
        for line in self._LINES:
            line.deposit(repository, x, y)
        if self.__paint is not None:
            repository['_paint'].append((self.__paint[0], self.__paint[1] + x, self.__paint[2] + y, self.__paint[3]))
        if self.__paint_annot is not None:
            repository['_paint_annot'].append((self.__paint_annot[0], self.__paint_annot[1] + x, self.__paint_annot[2] + y))
  
members = (Null, Texttags, Texttag, Blocktags, Blocktag)
