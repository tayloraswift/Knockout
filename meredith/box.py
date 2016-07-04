from itertools import chain
from random import randint

from olivia import literal, reformat, standard

from meredith import datablocks

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
    plane = False

class Box(dict):
    name = '_box'
    
    textfacing = False  # whether or not contents of this object are to be written on the same line          (contains inline boxes)
    inline = False      # whether or not this object is to be written on the same line as the preceeding one (contained by a textfacing)
    
    plane = False       # whether or not this object can function as a plane                                 (contains block objects)
    planelevel = False  # whether or not this object is directly contained by a plane                        (contained by a plane)
    
    DNA = []
    IMPLY = {}
    
    def __init__(self, attrs, content=None):
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
        for A, TYPE, * default in DNA:
            if TYPE in literal:
                if A in attrs:
                    v = literal[TYPE](attrs[A])
                    self.attrs[A] = v
                    yield A, v
                
                elif default:
                    yield A, literal[TYPE](default[0])
            
            elif TYPE in standard:
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
        raise NotImplementedError
    
    def after(self, A):
        pass

    def assign(self, A, S):
        try:
            TYPE, * default = next(td for a, * td in self.__class__.DNA if a == A)
        except StopIteration:
            print('Invalid attribute: ' + A)
            return
        
        self.before()
        if TYPE in literal:
            v = literal[TYPE](S)
            self.attrs[A] = v
            self[A] = v
        
        elif TYPE in standard:
            self.attrs[A] = S
            self[A] = standard[TYPE](S)
        
        elif TYPE in reformat:
            up, down = reformat[TYPE]
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
        return self.__class__(self.attrs, content)
    
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

class Datablocks(Box):
    def content_new(self, active=None, i=None):
        if active is None:
            name = self.__class__.defmembername
        else:
            name = active['name']
        O = self.__class__.contains({'name': new_name(name, self.__class__.dblibrary)})
        if i is None:
            self.content.append(O)
            self.sort_content()
        else:
            self.content.insert(i, O)
        self.__class__.dblibrary.update_datablocks(self)
        self.after('__content__')
        return O

    def sort_content(self):
        self.content.sort(key=lambda O: O['name'])

class _Tags(Datablocks):
    name = '_abstract_taglist'
    
    defmembername = 'Untitled tag'
    
    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        self.__class__.dblibrary.ordered = self
        self.__class__.dblibrary.update_datablocks(self)

    def after(self, A):
        if A == 'name':
            self.__class__.dblibrary.update_datablocks(self)
    
class _Tag(Box):
    name = '_abstract_tag'
    DNA = [('name', 'str', '_undef')]

class Texttag(_Tag):
    name = 'texttag'

    def after(self, A):
        if A == 'name':
            datablocks.Texttags_D.update_datablocks(datablocks.TTAGS)

class Texttags(_Tags):
    name = 'texttags'
    dblibrary = datablocks.Texttags_D
    contains = Texttag

class Blocktag(_Tag):
    name = 'blocktag'

    def after(self, A):
        if A == 'name':
            datablocks.Blocktags_D.update_datablocks(datablocks.BTAGS)

class Blocktags(_Tags):
    name = 'blocktags'
    dblibrary = datablocks.Blocktags_D
    contains = Blocktag

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
            repository['_paint'].append((self.__paint[0], self.__paint[1] + x, self.__paint[2] + y))
        if self.__paint_annot is not None:
            repository['_paint_annot'].append((self.__paint_annot[0], self.__paint_annot[1] + x, self.__paint_annot[2] + y))
  
members = (Null, Texttags, Texttag, Blocktags, Blocktag)
