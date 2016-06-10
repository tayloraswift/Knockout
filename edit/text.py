from fonts import spaces
from edit.wonder import prose
spaces_set = set(spaces) | {' '}

def lookahead(text, start, f):
    try:
        i = start + next(i for i, e in enumerate(text[start + 1:]) if f(str(e))) + 1
    except StopIteration:
        i = len(text)
    return i

def lookbehind(text, start, f):
    try:
        i = start - next(i for i, e in enumerate(reversed(text[:start])) if f(str(e))) - 1
    except StopIteration:
        i = -1
    return i
    
def expand_cursors_word(text, a):
    I = a
    J = a
    SP = spaces_set
    PR = prose
    try:
        # select block of spaces
        if str(text[a]) in SP:
            I = lookbehind(text, a, lambda c: c not in SP) + 1
            
            J = lookahead(text, a, lambda c: c not in SP)
        
        # select block of words
        elif str(text[a]) in PR:
            I = lookbehind(text, a, lambda c: c not in PR) + 1
            
            J = lookahead(text, a, lambda c: c not in PR)
        
        # select block of punctuation
        else:
            I = lookbehind(text, a, lambda c: c in PR or c in SP) + 1
            
            J = lookahead(text, a, lambda c: c in PR or c in SP)

    except (ValueError, IndexError):
        pass
    
    return I, J
