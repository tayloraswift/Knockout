from itertools import chain

from IO import un

from olivia import literal, reformat, standard

from meredith.datablocks import Texttags_D, Blocktags_D

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
        un.history.save()
    
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

class _Tags(Box):
    name = '_abstract_taglist'

    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        self.__class__.dblibrary.update_datablocks(self)

class _Tag(Box):
    name = '_abstract_tag'
    DNA = [('name', 'str', '_undef')]
    
    def __hash__(self):
        return id(self)

class Texttags(_Tags):
    name = 'texttags'
    dblibrary = Texttags_D

class Texttag(_Tag):
    name = 'texttag'

class Blocktags(_Tags):
    name = 'blocktags'
    
    dblibrary = Blocktags_D

class Blocktag(_Tag):
    name = 'blocktag'

members = (Null, Texttags, Texttag, Blocktags, Blocktag)
