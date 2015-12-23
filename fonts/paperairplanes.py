from fonts import fonts, fonttable

# PARAGRAPH STYLES

def p_push_attribute(value, attribute, p):
    fonts.p_set_attribute((False, value), attribute, p)

def f_push_attribute(value, attribute, f):
    fonts.TEXTURES[f][attribute] = (False, value)

def p_read_indent(A, p):
    C, SIGN, K = fonttable.p_table.get_paragraph(p)[A]

    if K:
        if abs(K) == 1:
            coefficient = ''
        else:
            coefficient = str(K)
        
        if SIGN == -1:
            SIGN = ' - '
        else:
            SIGN = ' + '
        
        if C:
            val = str(C) + SIGN + coefficient + 'K'
        else:
            if SIGN == ' + ':
                val = coefficient + 'K'
            else:
                val = SIGN[1] + coefficient + 'K'
    else:
        val = str(C)
    return val

def p_push_indent(value, A, p):
    K = 0
    C = 0
    sgn = 1
    for k, g in ( (k, ''.join(g)) for k, g in itertools.groupby(value, key=lambda v: True if v in ('+', '-') else False) ):
        if k:
            if g.count('-') % 2:
                sgn = -1
            else:
                sgn = 1
        else:
            if 'K' in g:
                if g[0] == 'K':
                    coefficient = 1
                else:
                    coefficient = int(float(g[:g.find('K')]))
                K += coefficient*sgn
            else:
                if '.' in g:
                    if g.count('.') > 1:
                        dot = g.find('.')
                        g = ''.join(g[:dot + 1]) + ''.join([d for d in g[dot + 1:] if d != '.'])
                    constant = float(g)
                else:
                    constant = int(g)
                C += constant*sgn
    
    if K < 0:
        SIGN = -1
        K = abs(K)
    else:
        SIGN = 1
    
    value = (C, SIGN, K)
    
    fonts.p_set_attribute((False, value), A, p)

def p_rename(OLD, NEW):
    for k, u in fonts.paragraph_classes.items():
        for attribute, v in u.items():

            # inherit flag
            if v[0]:
                if v[1] == OLD:
                    fonts.paragraph_classes[k][attribute] = (True, NEW)

    fonttable.p_table.clear()

def p_link_font_datablock(name, p):
    fonts.paragraph_classes[p]['fontclasses'][1] [ fonts.paragraph_classes[p]['fontclasses'][1]['_ACTIVE'] ] = name

def p_active_f(p):
    return fonts.paragraph_classes[p]['fontclasses'][1] [ fonts.paragraph_classes[p]['fontclasses'][1]['_ACTIVE'] ]

# TAGS
    
def tags_read_states(p):
    tags = set(fonts.paragraph_classes[p]['fontclasses'][1] ['_ACTIVE'])
    return [ (k['name'] in tags, k['name'] ) for k in fonts.TAGS[fonts.paragraph_classes[p]['tags']][1:] ]

def tags_push_states(states, p):
    tags = tuple(sorted(k['name'] for state, k in zip(states, fonts.TAGS[fonts.paragraph_classes[p]['tags']][1:]) if state))
    if tags in fonts.paragraph_classes[p]['fontclasses'][1]:
        tags = ('_occupied', ) + tags
    
    fc = fonts.paragraph_classes[p]['fontclasses'][1]
    fc[tags] = fc.pop(fc['_ACTIVE'])
    fc['_ACTIVE'] = tags

# FONT STYLES
def rename_f(old, new, P):
    for k, PC in fonts.paragraph_classes.items():
        if not PC['fontclasses'][0]:
            for l in PC['fontclasses'][1]:
                if PC['fontclasses'][1][l] == old:
                    fonts.paragraph_classes[k]['fontclasses'][1][l] = new
                else:
                    if PC['fontclasses'][1]['_ACTIVE'] == old:
                        fonts.paragraph_classes[k]['fontclasses'][1]['_ACTIVE'] = new

    for k, TX in fonts.TEXTURES.items():
        for l in TX:
            if TX[l][0]:
                if TX[l][1] == old:
                    fonts.TEXTURES[k][l] = (True, new)

