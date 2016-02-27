import itertools
from edit.arithmetic import NumericStringParser, ParseException

nsp = NumericStringParser()

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

def pack_binomial(value, letter):
    value = ''.join(c for c in value if c in set('1234567890.-+' + letter))
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

def interpret_int(n, fail=0):
    if type(n) is int:
        return n
    elif type(n) is float:
        return int(n)
    else:
        try:
            return int(nsp.eval(n))
        except ParseException:
            return fail
    
def interpret_float(f, fail=0):
    if type(f) in {int, float}:
        return f

    else:
        try:
            v = nsp.eval(f)
            if v.is_integer():
                return int(v)
            else:
                return v
        except ParseException:
            return fail

def interpret_enumeration(e):
    if type(e) is set:
        return e
    else:
        return set(interpret_int(val) for val in e.split(',') if any(c in '0123456789' for c in val))

def interpret_float_tuple(value):
    L = (interpret_float(val, fail=None) for val in value.split(','))
    return (v for v in L if v is not None)

def interpret_haylor(value):
    if ',' in value:
        print('1 dimensional values take only one coordinate')
        return ()
    L = (interpret_float(val, fail=None) for val in value.split())
    return (v for v in L if v is not None)

def interpret_tsquared(value):
    L = (interpret_float_tuple(val, fail=None) for val in value.split())
    return (v for v in L if v is not None and len(v) == 2)

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

def interpret_bool(b):
    t = type(e)
    if t in {bool, int}:
        return e
    elif t is str:
        if e in {'True', '1'}:
            return True
        else:
            return interpret_int(e)
    else:
        return False
