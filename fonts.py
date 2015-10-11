import copy
        
        
class TypeClass(object):
    def __init__(self, path, fontsize=(False, 13), tracking=(False, 0)):
    
        self._path = path
        
        self._fontsize = fontsize
        self._tracking = tracking
    

    def update_path(self, path):
        if not self._path[0]:
            self._path = (False, path)
    
    def update_size(self, size):
        if not self._fontsize[0]:
            self._fontsize = (False, size)
    
    def update_tracking(self, tracking):
        if not self._tracking[0]:
            self._tracking = (False, tracking)


def f_get_attribute(attribute, p, f):
    p, f = get_fontclass_root(p, f)
        
    # assumes root p and f
    a = f_read_attribute(attribute, p, f)
    if a[0]:
        return f_get_attribute(attribute, * a[1])
    else:
        return a

def f_read_attribute(attribute, p, f):
    # assumes root p and f
    attribute = '_' + attribute
    return getattr(paragraph_classes[p].fontclasses[1][f][1], attribute)

def f_set_attribute(attribute, p, f, value):
    # assumes root p and f
    attribute = '_' + attribute
    setattr(paragraph_classes[p].fontclasses[1][f][1], attribute, value)

def f_read_f(p, f):
    return paragraph_classes[p].fontclasses[1][f]

def f_get_f(p, f):
    # assumes root p
    a = f_read_f(p, f)
    if a[0]:
        return f_get_f( * a[1])
    else:
        return a

class ParagraphClass(object):
    def __init__(self, leading, margin_bottom):
        self.fontclasses = [False, {}]
        self._leading = leading
        self._margin_bottom = margin_bottom

            

    def update_leading(self, leading):
        if not self._leading[0]:
            self._leading = (False, leading)

    def update_margin(self, margin):
        if not self._margin_bottom[0]:
            self._margin_bottom = (False, margin)

    # only used for empty inheritance
    def update_fontclasses(self, fontclasses):
        self.fontclasses = fontclasses
            
    def replace_fontclass(self, names, fontclass):
        if not self.fontclasses[0]:
            self.fontclasses[1][names] = fontclass

def add_paragraph_class(name, clone):
    if name not in paragraph_classes:
        paragraph_classes[name] = copy.deepcopy(paragraph_classes[clone])


_interface_class = ParagraphClass((False, 16), (False, 5))
_interface_class.replace_fontclass( (), (False, TypeClass(path=(False, '/home/kelvin/.fonts/NeueFrutiger45.otf'), fontsize=(False, 13), tracking=(False, 0))) )
_interface_class.replace_fontclass( ('strong',), (False, TypeClass(path=(False, '/home/kelvin/.fonts/NeueFrutiger65.otf'), fontsize=(False, 13), tracking=(False, 1))) )
_interface_class.replace_fontclass( ('label',), (False, TypeClass(path=(False, '/home/kelvin/.fonts/NeueFrutiger45.otf'), fontsize=(False, 11), tracking=(False, 1))) )
_interface_class.replace_fontclass( ('title',), (False, TypeClass(path=(False, '/home/kelvin/.fonts/NeueFrutiger45.otf'), fontsize=(False, 18), tracking=(False, 4))) )

_h1_class = ParagraphClass((False, 28), (False, 10))
_h1_class.replace_fontclass( (), (False, TypeClass(path=(False, "/home/kelvin/.fonts/NeueFrutiger45.otf"), fontsize=(False, 18))) )
_h1_class.replace_fontclass( ('caption',), (False, TypeClass(path=(False, "/home/kelvin/.fonts/NeueFrutiger45.otf"), fontsize=(False, 15))) )
_h1_class.replace_fontclass( ('emphasis',), (False, TypeClass(path=(False, "/home/kelvin/.fonts/NeueFrutiger45Italic.otf"), fontsize=(False, 18))) )
_h1_class.replace_fontclass( ('strong',), (False, TypeClass(path=(False, "/home/kelvin/.fonts/NeueFrutiger65.otf"), fontsize=(False, 18))) )
_h1_class.replace_fontclass( ('emphasis', 'strong'), (False, TypeClass(path=(False, "/home/kelvin/.fonts/NeueFrutiger65Italic.otf"), fontsize=(False, 18))) )

_body_class = ParagraphClass((False, 20), (False, 5))
_body_class.replace_fontclass( (), (False, TypeClass(path=(False, "/home/kelvin/.fonts/Proforma-Book.otf"), fontsize=(False, 15))) )
_body_class.replace_fontclass( ('caption',), (False, TypeClass(path=(False, "/home/kelvin/.fonts/NeueFrutiger45.otf"), fontsize=(False, 13))) )
_body_class.replace_fontclass( ('emphasis',), (False, TypeClass(path=(False, "/home/kelvin/.fonts/Proforma-BookItalic.otf"), fontsize=(True, ('body', () ) ))) )
_body_class.replace_fontclass( ('strong',), (False, TypeClass(path=(False, "/home/kelvin/.fonts/Proforma-Bold.otf"), fontsize=(True, ('body', () ) ))) )
_body_class.replace_fontclass( ('emphasis', 'strong',), (False, TypeClass(path=(False, "/home/kelvin/.fonts/Proforma-BoldItalic.otf"), fontsize=(True, ('body', () ) ))) )

_q_class = ParagraphClass((True, 'body'), (False, 5))
_q_class.replace_fontclass( (), (True, ('body', ('emphasis',) )) )
_q_class.replace_fontclass( ('caption',), (False, TypeClass(path=(False, "/home/kelvin/.fonts/NeueFrutiger45.otf"), fontsize=(False, 13))) )
_q_class.replace_fontclass( ('emphasis',), (False, TypeClass(path=(False, "/home/kelvin/.fonts/Proforma-Book.otf"), fontsize=(False, 15))) )
_q_class.replace_fontclass( ('strong',), (False, TypeClass(path=(False, "/home/kelvin/.fonts/Proforma-BoldItalic.otf"), fontsize=(False, 15))) )
_q_class.replace_fontclass( ('emphasis', 'strong',), (False, TypeClass(path=(False, "/home/kelvin/.fonts/Proforma-Bold.otf"), fontsize=(False, 15))) )

paragraph_classes = {'_interface': _interface_class,
        'body': _body_class,
        'quotation': _q_class,
        'h1': _h1_class
        }

def get_leading(p):
    l = paragraph_classes[p]._leading
    if l[0]:
        return get_leading(l[1])
    else:
        return l[1]

def get_margin_bottom(p):
    m = paragraph_classes[p]._margin_bottom
    if m[0]:
        return get_margin_bottom(m[1])
    else:
        return m[1]

def get_fontclasses(p):
    return paragraph_classes[p].fontclasses[1]


def get_fontclass(p, f):
    return paragraph_classes[p].fontclasses[1][f]

def _get_root_p_fontclass(p):
    # returns pclass name
    c = paragraph_classes[p].fontclasses
    if not c[0]:
        return p
    else:
        return _get_root_p_fontclass(c[1])

def _trace_fontclass_to_root(p, f):
    # assumes p is root
    fontclass = get_fontclass(p, f)

    while True:
        if fontclass[0]:
            
            p = fontclass[1][0]
            f = fontclass[1][1]
            fontclass = get_fontclass(p, f)
        else:
            break

    return p, f
    
def get_fontclass_root(p, f):
    p = _get_root_p_fontclass(p)

    return _trace_fontclass_to_root(p, f)


