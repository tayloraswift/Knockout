import itertools
# PARAGRAPH STYLES

def read_binomial(C, SIGN, K):
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

def pack_binomial(value):
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
    
    return C, SIGN, K


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

def tags_and_subtags(p):
    TT = []
    for tag in fonts.TAGS[fonts.paragraph_classes[p]['tags']][1:]:
        if tag['subtags']:
            subtags = list(tag['subtags'].keys())
            subtags.remove('_ACTIVE')
            TT += subtags
        else:
            TT.append(tag['name'])

    return TT

# Q

def tags_push_subtag_name(name, p):
    li = fonts.TAGS[ fonts.paragraph_classes[p]['tags'] ]
    ST = li [li[0] + 1]['subtags']
    ST[name] = ST.pop(ST['_ACTIVE'])
    ST['_ACTIVE'] = name

# PEGS

def pegs_push_tag(tag, G):
    fonts.PEGS[G] [tag] = fonts.PEGS[G].pop(fonts.PEGS[G]['_ACTIVE'])
    fonts.PEGS[G]['_ACTIVE'] = tag

