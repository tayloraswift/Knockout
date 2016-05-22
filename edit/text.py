from edit.wonder import _breaking_chars

def lookahead(text, start, f):
    try:
        i = start + next(i for i, e in enumerate(text[start + 1:]) if f(e)) + 1
    except StopIteration:
        i = len(text)
    return i

def lookbehind(text, start, f):
    try:
        i = start - next(i for i, e in enumerate(reversed(text[:start])) if f(e)) - 1
    except StopIteration:
        i = -1
    return i
    
def expand_cursors_word(text, a):
    I = a
    J = a
    try:
        # select block of spaces
        if text[a] == ' ':
            I = lookbehind(text, a, lambda c: c != ' ') + 1
            
            J = lookahead(text, a, lambda c: c != ' ')
        
        # select block of words
        elif str(text[a]) not in _breaking_chars:
            I = lookbehind(text, a, lambda c: str(c) in _breaking_chars) + 1
            
            J = lookahead(text, a, lambda c: str(c) in _breaking_chars)
        
        # select block of punctuation
        else:
            I = lookbehind(text, a, lambda c: str(c) not in _breaking_chars or c == ' ') + 1
            
            J = lookahead(text, a, lambda c: str(c) not in _breaking_chars or c == ' ')

    except (ValueError, IndexError):
        pass
    
    return I, J
