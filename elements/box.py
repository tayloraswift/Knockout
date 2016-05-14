from itertools import chain

from elements.datatypes import literal, reformat, standard

from elements.datablocks import Texttags_D, Blocktags_D

class Null(object):
    name = '_nullbox'
    textfacing = False

class Box(dict):
    name = '_box'
    textfacing = False
    
    DNA = []
    
    def __init__(self, attrs, content=None):
        self.content = content
        self.attrs = {}
        dict.__init__(self, self._load_attributes(attrs))
    
    def _load_attributes(self, attrs):
        for A, TYPE, * default in self.DNA:
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

    def assign(self, A, S):
        try:
            TYPE, * default = next(td for a, * td in self.DNA if a == A)
        except StopIteration:
            print('Invalid attribute: ' + A)
            return

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

    def deassign(self, A):
        del self.attrs[A]
        del self[A]
    
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
