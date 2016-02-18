from itertools import chain

def print_attrs(name, attrs): 
    if attrs:
        return '<' + name + ' ' + ' '.join(A + '="' + repr(V)[1:-1] + '"' for A, V in attrs.items()) + '>'  
    else:
        return '<' + name + '>'

def print_styles(PP):
    S = {}
    ptags = '&'.join(chain.from_iterable((P.name for i in range(V)) for P, V in PP.P.items()))
    if ptags != 'body':
        S['class'] = ptags
    if PP.EP:
        S['style'] = repr(PP.EP.polaroid()[0])
    return S
