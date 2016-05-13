from edit.paperairplanes import literal, reformat, standard

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
                    yield v
                elif default:
                    yield literal[TYPE](default[0])
            elif TYPE in standard:
                if A in attrs:
                    self.attrs[A] = attrs[A]
                    yield standard[TYPE](attrs[A])
                elif default:
                    yield standard[TYPE](default[0])
            elif TYPE in reformat:
                up, down = reformat[TYPE]
                if A in attrs:
                    v = up(attrs[A])
                    self.attrs[A] = down(v)
                    yield v
                elif default:
                    yield up(default[0])

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

class Paragraph_block(Box):
    name = 'p'
    textfacing = True
    
    DNA  = [('class',           'paracounter',  'body'),
    
            ('hyphenate',       'bool'),
            ('indent',          'binomial'),
            ('indent_range',    'int set'),
            ('leading',         'float'),
            ('margin_bottom',   'float'),
            ('margin_left',     'float'),
            ('margin_right',    'float'),
            ('margin_top',      'float'),
            ('align',           'float'),
            ('align_to',        'str'),
            
            ('incr_place_value','int'),
            ('incr_assign',     'fn'),
            ('show_count',      'farray')]

class Block_style(Paragraph_block):
    name = 'blockstyle'
    textfacing = False
