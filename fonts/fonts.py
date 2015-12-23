from copy import deepcopy

paragraph_classes = {}
TEXTURES = {}
TAGS = {}

def q_read(attribute, p):
    li = TAGS[ paragraph_classes[p]['tags'] ]
    return li [li[0] + 1][attribute]

def q_set(value, attribute, p):
    li = TAGS[ paragraph_classes[p]['tags'] ]
    li [li[0] + 1][attribute] = value

def p_get_attribute(attribute, p):
    try:
        a = p_read_attribute(attribute, p)
    except KeyError:
        return (False, 0)
    if a[0]:
        return p_get_attribute(attribute, a[1])
    else:
        return a

def p_read_attribute(attribute, p):
    try:
        return paragraph_classes[p][attribute]
    except KeyError:
        return (False, 0)

def p_set_attribute(value, attribute, p):
    paragraph_classes[p][attribute] = value

def add_paragraph_class(name, clone):
    if name not in paragraph_classes:
        paragraph_classes[name] = deepcopy(paragraph_classes[clone])


def f_get_attribute(attribute, f):
    a = TEXTURES[f] [attribute]
    if a[0]:
        return f_get_attribute(attribute, a[1])
    else:
        return a

def f_read_attribute(attribute, f):
    return TEXTURES[f] [attribute]
