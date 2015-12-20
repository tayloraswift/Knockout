from copy import deepcopy

paragraph_classes = {}
TEXTURES = {}
TAGS = {}

def REPLACE(pc):
    global paragraph_classes
    paragraph_classes = pc

def GET():
    return paragraph_classes

def q_read(p):
    li = TAGS[ paragraph_classes[p]['tags'] ]
    return li [li[0] + 1]

def q_set(value, p):
    li = TAGS[ paragraph_classes[p]['tags'] ]
    old = li [li[0] + 1]
    li [li[0] + 1] = value

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


def f_hunt_attribute(attribute, name):
    a = TEXTURES[name] [attribute]
    if a[0]:
        return f_hunt_attribute(attribute, a[1])
    else:
        return a

def f_get_attribute(attribute, p, f):
    name = p_get_attribute('fontclasses', p)[1][f]
    return f_hunt_attribute(attribute, name)

def f_read_attribute(attribute, p, f):
    name = p_get_attribute('fontclasses', p)[1][f]
    return TEXTURES[name] [attribute]

def f_set_attribute(value, attribute, p, f):
    # assumes root p and f
    if attribute == '_all':
        paragraph_classes[p]['fontclasses'][1][f] = value
    else:
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


def get_fontclasses(p):
    return paragraph_classes[p]['fontclasses'][1]

def get_fontclass(p, f):
    return paragraph_classes[p]['fontclasses'][1][f]

def rename_p(old, new):
    for k in paragraph_classes:
        # travel through fontclasses
        if not paragraph_classes[k]['fontclasses'][0]:
            for f in paragraph_classes[k]['fontclasses'][1]:
            
                paragraph_classes[k]['fontclasses'][1][f] = list(paragraph_classes[k]['fontclasses'][1][f])
                
                # inherit flag
                if paragraph_classes[k]['fontclasses'][1][f][0]:
                    
                    paragraph_classes[k]['fontclasses'][1][f][1] = list(paragraph_classes[k]['fontclasses'][1][f][1])
                    
                    if paragraph_classes[k]['fontclasses'][1][f][1] [0] == old:
                        paragraph_classes[k]['fontclasses'][1][f][1] [0] = new
                    
                    paragraph_classes[k]['fontclasses'][1][f][1] = tuple(paragraph_classes[k]['fontclasses'][1][f][1])
                
                else:
                    paragraph_classes[k]['fontclasses'][1][f] = list(paragraph_classes[k]['fontclasses'][1][f])
                    
                    for a in paragraph_classes[k]['fontclasses'][1][f][1]:
                        paragraph_classes[k]['fontclasses'][1][f][1][a] = list(paragraph_classes[k]['fontclasses'][1][f][1][a])
                        # inherit flag
                        if paragraph_classes[k]['fontclasses'][1][f][1][a][0]:
                            
                            paragraph_classes[k]['fontclasses'][1][f][1][a][1] = list(paragraph_classes[k]['fontclasses'][1][f][1][a][1])

                            if paragraph_classes[k]['fontclasses'][1][f][1][a][1] [0] == old:
                                paragraph_classes[k]['fontclasses'][1][f][1][a][1] [0] = new
                            
                            paragraph_classes[k]['fontclasses'][1][f][1][a][1] = tuple(paragraph_classes[k]['fontclasses'][1][f][1][a][1])
                        
                        paragraph_classes[k]['fontclasses'][1][f][1][a] = tuple(paragraph_classes[k]['fontclasses'][1][f][1][a])
                    
                    paragraph_classes[k]['fontclasses'][1][f] = tuple(paragraph_classes[k]['fontclasses'][1][f])

                paragraph_classes[k]['fontclasses'][1][f] = tuple(paragraph_classes[k]['fontclasses'][1][f])
                    
            
        for l in paragraph_classes[k]:
            paragraph_classes[k][l] = list(paragraph_classes[k][l])
            # inherit flag
            if paragraph_classes[k][l][0]:
                if paragraph_classes[k][l][1] == old:
                    paragraph_classes[k][l][1] = new
            
            paragraph_classes[k][l] = tuple(paragraph_classes[k][l])
        
        if k == old:
            paragraph_classes[new] = paragraph_classes[k]
            del paragraph_classes[old]
