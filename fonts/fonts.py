paragraph_classes = {}

def REPLACE(pc):
    global paragraph_classes
    paragraph_classes = pc

def GET():
    return paragraph_classes

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


def f_read_f(p, f):
    return paragraph_classes[p]['fontclasses'][1][f]

def f_get_f(p, f):
    # assumes root p
    a = f_read_f(p, f)
    if a[0]:
        return f_get_f( * a[1])
    else:
        return a

def p_get_attribute(attribute, p):
    a = p_read_attribute(attribute, p)
    if a[0]:
        return p_get_attribute(attribute, a[1])
    else:
        return a

def p_read_attribute(attribute, p):
    return paragraph_classes[p][attribute]


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

    search = []
    while True:
        if fontclass[0]:
            if fontclass[1] not in search:
                search.append(fontclass[1])
                p = fontclass[1][0]
                f = fontclass[1][1]
                fontclass = get_fontclass(p, f)
            else:
                raise RuntimeError('FONT CLASS REFERENCE LOOP')
        else:
            break

    return p, f
    
def get_fontclass_root(p, f):
    p = _get_root_p_fontclass(p)

    return _trace_fontclass_to_root(p, f)


