from itertools import groupby, chain

from bulletholes.counter import TCounter as Counter

from meredith.datablocks import Texttags_D, Blocktags_D, Textstyles_D
import meredith

from olivia.frames import Frames
from olivia.poptarts import Sprinkles
from olivia.basictypes import interpret_bool, interpret_int, interpret_float

# attribute types #
# stored as literals            : bool, int, float, float tuple
# stored as reformatted string  : binomial, int set
# stored as string              : str, rgba, 1_D, multi_D, fx, fn, fA, ftag, ptags

def interpret_frame(S):
    frames = ((c for c in C.split(';') if c) for C in S.split('|') if C)
    F = Frames([[ [int(k) for k in P.split(',')] + ['False'] for P in R1.split()], 
            [ [int(k) for k in P.split(',')] + ['False'] for P in R2.split()], int(page)] for R1, R2, page in frames)
    return F

def interpret_grid(S):
    if not S:
        S = ';'
    xx, yy, *_ = (list(map(interpret_int, g.split(' '))) for g in S.split(';'))
    return Sprinkles(xx, yy)

# special named datatypes

class Tagcounter(Counter):
    def __repr__(self):
        return '^'.join(chain.from_iterable((T['name'] for i in range(V)) if V > 0 else 
                ('~' + T['name'] for i in range(abs(V))) for T, V in sorted(self.items(), key=lambda k: k[0]['name'])))

def _tagcounter(S, LIB):
    if type(S) is Tagcounter:
        return S.copy()
    elif S:
        C = Counter(T for T in S.split('^') if T[0] != '~')
        C -= Counter(T[1:] for T in S.split('^') if T[0] == '~')
        
        return Tagcounter({LIB[T]: V for T, V in C.items()})
    else:
        return Tagcounter()

def blocktagcounter(S):
    return _tagcounter(S, Blocktags_D)

def texttagcounter(S):
    return _tagcounter(S, Texttags_D)

def textstyle(S):
    if type(S) is meredith.styles.Textstyle:
        return S
    try:
        return Textstyles_D[S]
    except KeyError:
        return None

literal  = {'bool': interpret_bool,
            'int': interpret_int,
            'float': interpret_float,
            
            'frames': interpret_frame,
            'pagegrid': interpret_grid,
            
            'blocktc': blocktagcounter,
            'texttc': texttagcounter,
            'textstyle': textstyle}

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

def interpret_enumeration(e):
    if type(e) is set:
        return e
    else:
        return set(interpret_int(val) for val in e.split(',') if any(c in '0123456789' for c in val))

reformat = {'binomial': (pack_binomial, read_binomial),
            'int set': (interpret_enumeration, lambda S: ', '.join(str(i) for i in sorted(S)))}

def interpret_float_tuple(value):
    L = (interpret_float(val, fail=None) for val in value.split(','))
    return tuple(v for v in L if v is not None)

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

def interpret_haylor(value): # X X X X X : (X, X, X, X, X)
    if type(value) is tuple:
        return value
    else:
        if ',' in value:
            print('1 dimensional values take only one coordinate')
            return ()
        L = (interpret_float(val, fail=None) for val in value.split())
        return tuple(v for v in L if v is not None)

def interpret_tsquared(value):
    if type(value) is tuple:
        return value
    else:
        return tuple(tuple(interpret_float_tuple(val)) for val in value.split())

# for function plotter
from data.userfunctions import *
import parser

def _f(expression, template):
    if not expression or expression == 'None':
        return None
    elif callable(expression):
        return expression
    else:
        code = parser.expr(expression).compile()
        return template(code)

def function_x(expression):
    return _f(expression, lambda code: lambda x, y=0: eval(code))

def function_n(expression):
    return _f(expression, lambda code: lambda n: eval(code))

def function_array(expression):
    return _f(expression, lambda code: lambda A: eval(code))


standard = {'str': str,
            'float tuple': interpret_float_tuple,
            'rgba': interpret_rgba, 
            '1D': interpret_haylor,
            'multi_D': interpret_tsquared,
            'fx': function_x,
            'fn': function_n,
            'farray': function_array}
