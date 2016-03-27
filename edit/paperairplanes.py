from itertools import groupby
from edit.arithmetic import NumericStringParser, ParseException

from style.styles import FTAGS

nsp = NumericStringParser()

def read_binomial(S):
    C, SIGN, K = S
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
    value = ''.join(c for c in value if c in set('1234567890.-+K'))
    K = 0
    C = 0
    sgn = 1
    for k, g in ( (k, ''.join(g)) for k, g in groupby(value, key=lambda v: True if v in ('+', '-') else False) ):
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

def interpret_haylor(value): # X X X X X : (X, X, X, X, X)
    if type(value) is tuple:
        return value
    else:
        if ',' in value:
            print('1 dimensional values take only one coordinate')
            return ()
        L = (interpret_float(val, fail=None) for val in value.split())
        return (v for v in L if v is not None)

def interpret_tsquared(value):
    if type(value) is tuple:
        return value
    else:
        return (tuple(interpret_float_tuple(val)) for val in value.split())

# for function plotter
from data.userfunctions import *
import parser

def f(expression, template):
    if not expression or expression == 'None':
        return None
    elif callable(expression):
        return expression
    else:
        code = parser.expr(expression).compile()
        return template(code)

def function_x(expression):
    return f(expression, lambda code: lambda x, y=0: eval(code))

def function_array(expression):
    return f(expression, lambda code: lambda A: eval(code))

def function_int(expression):
    return f(expression, lambda code: lambda n: eval(code))

def interpret_rgba(C):
    RGBA = [0, 0, 0, 1]
    if type(C) is tuple:
        for pos, value in enumerate(C[:4]):
            RGBA[pos] = value
    else:
        C = C.lower()
        hx = '0123456789abcdef'
        numeric = '0123456789., '
        flo = '0123456789.'
        i = '0123456789'
        # rgba
        if all(c in numeric for c in C):
            for pos, channel in enumerate(C.split(',')[:4]):
                RGBA[pos] = interpret_float(channel)
        # hex
        else:
            colorstring = ''.join(c for c in C if c in hx)
            colorstring = colorstring + '000000ff'[len(colorstring):]
            for pos in range(4):
                RGBA[pos] = int(colorstring[pos*2 : pos*2 + 2], 16) / 255
    return tuple(RGBA)

def interpret_bool(b):
    t = type(b)
    if t in {bool, int}:
        return b
    elif t is str:
        if b in {'True', '1'}:
            return True
        else:
            return interpret_int(b)
    else:
        return False

def fonttag(f):
    if type(f) is str:
        return FTAGS[f]
    else:
        return f

datatypes = {'null': lambda x: x,
            'int': interpret_int,
            'float': interpret_float,
            'binomial': pack_binomial,
            'float tuple': interpret_float_tuple, 
            'int set': interpret_enumeration,
            'rgba': interpret_rgba,
            'str': str,
            'bool': interpret_bool,
            '1D': interpret_haylor,
            'multi_D': interpret_tsquared,
            'fx': function_x,
            'farray': function_array,
            'fn': function_int,
            'ftag': fonttag}

formatable = {'binomial': read_binomial,
              'int set': lambda S: ', '.join(str(i) for i in sorted(S))}
