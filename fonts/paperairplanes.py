import itertools

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
                    coefficient = interpret_int(g[:g.find('K')])
                K += coefficient*sgn
            else:
                constant = interpret_float(g)
                C += constant*sgn
    
    if K < 0:
        SIGN = -1
        K = abs(K)
    else:
        SIGN = 1

    return C, SIGN, K

def interpret_int(n):
    if '.' in n:
        v = int(round(interpret_float(n)))
    else:
        i = '0123456789'
        integer = ''.join(c for c in n if c in i)
        if integer:
            v = int(integer)
        else:
            v = 0
    return v
    
def interpret_float(f):
    i = '0123456789'
    if '.' not in f:
        v = interpret_int(f)
    else:
        point = f.find('.')
        integer = ''.join(c for c in f[:point] if c in i)
        sawtooth = ''.join(c for c in f[point:] if c in i)
        if integer or sawtooth:
            v = float(integer + '.' + sawtooth)
        else:
            v = 0
    return v
    
def interpret_rgba(C):
    hx = '0123456789abcdef'
    numeric = '0123456789., '
    flo = '0123456789.'
    i = '0123456789'
    RGBA = [0, 0, 0, 1]
    # rgba
    if all(c in numeric for c in C):
        for pos, channel in enumerate(C.split(',')[:4]):
            RGBA[pos] = interpret_float(channel)
    # hex
    else:
        colorstring = ''.join(c for c in C if c in hx)
        colorstring = colorstring + '000000ffx'[len(colorstring):]
        for pos in range(4):
            RGBA[pos] = int(colorstring[pos*2 : pos*2 + 2], 16) / 255
    return tuple(RGBA)
