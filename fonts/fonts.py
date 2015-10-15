from copy import deepcopy

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
    return paragraph_classes[p]['fontclasses'][1][f][1][attribute]

def f_set_attribute(attribute, p, f, value):
    # assumes root p and f
    paragraph_classes[p]['fontclasses'][1][f][1][attribute] = value

def f_read_f(p, f):
    return paragraph_classes[p]['fontclasses'][1][f]

def f_get_f(p, f):
    # assumes root p
    a = f_read_f(p, f)
    if a[0]:
        return f_get_f( * a[1])
    else:
        return a


def _create_p_class(fontclasses, leading, margin_bottom):
    return {'fontclasses': fontclasses, 'leading': leading, 'margin_bottom': margin_bottom}

def add_paragraph_class(name, clone):
    if name not in paragraph_classes:
        paragraph_classes[name] = deepcopy(paragraph_classes[clone])

def p_get_attribute(attribute, p):
    a = p_read_attribute(attribute, p)
    if a[0]:
        return p_get_attribute(attribute, a[1])
    else:
        return a

def p_read_attribute(attribute, p):
    return paragraph_classes[p][attribute]

def p_set_attribute(attribute, p, value):
    paragraph_classes[p][attribute] = value

paragraph_classes = {}


def get_fontclasses(p):
    return paragraph_classes[p]['fontclasses'][1]


def get_fontclass(p, f):
    return paragraph_classes[p]['fontclasses'][1][f]

def _get_root_p_fontclass(p):
    # returns pclass name

    c = paragraph_classes[p]['fontclasses']
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


