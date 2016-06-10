from itertools import chain

from fonts import nonbreaking_spaces, breaking_spaces

_fail = '\033[91m'
_endc = '\033[0m'
_bold = '\033[1m'

def fold_possesive(word):
    if word[-2:] in ('’s', '\'s'):
        return word[:-2]
    else:
        return word

def check_spelling(word):
    if word.isalpha() and not word.isupper():
        return struck.spell(word.encode('latin-1', 'ignore'))
    return True

try:
    from libraries.hunspell import hunspell
except ImportError:
    try:
        import hunspell
    except ImportError:
        hunspell = None
        print(_bold + _fail + 'ERROR: The hunspell spellchecker can’t be found. Spellcheck has been disabled.' + _endc + _fail + ' \n\tTry ' + _bold + 'pip3 install hunspell' + _endc + _fail + ' (requires python-dev and libhunspell-dev)\n\tMake sure pip installs hunspell for python3.5, not python3.4!' + _endc)

additional_words_file = 'data/spellcheck/add.txt'

if hunspell is not None:
    struck = hunspell.HunSpell('libraries/hunspell/en_US.dic', 'libraries/hunspell/en_US.aff')
    with open(additional_words_file) as A:
        for word in A.read().splitlines():
            struck.add(word.strip())
else:
    check_spelling = lambda W: True


alphabet = set(c for c in (chr(n) for n in range(2**16)) if c.isalpha())

prose = alphabet | set('0123456789&@#$\'’-')
# these characters get read as word-breaks in speech
_breaking_prose = set(chain(('<br/>', '—', '–', '/', '(', ')', '\\', '|', '=', '+', '_', ' '), breaking_spaces, nonbreaking_spaces))

# NOT the same as prose breaks because of '.', ':', etc. *Does not include ''' or '’' because these are found word-internal and when used as quotes, encapsulate single characters*
breaking_chars = set(chain((' ', '<fo/>', '<fc/>', '<br/>', '—', '–', '-', ':', '.', ',', ';', '/', '!', '?', '(', ')', '[', ']', '{', '}', '\\', '|', '=', '+', '_', '"', '“', '”', '<', '>' ),
                            breaking_spaces, nonbreaking_spaces))

def words(text, spell=False):
    T = list(map(str, text))

    BP = _breaking_prose
    P = prose
    if spell:
        cs = check_spelling
        fp = fold_possesive
        BC = breaking_chars
        
        word_count = 0
        misspelled_indices = []
        
        i = 0
        for j in chain((j for j, e in enumerate(T) if e in BP), (len(T),)):
            if j - i:
                selection = T[i:j]
                
                if any(e in P for e in selection):
                    word_count += 1
                    
                    iprevious = 0
                    for ii in chain((ii for ii, e in enumerate(selection) if e in BC), (len(selection),)):
                        if ii - iprevious:
                            W = ''.join(v for v in selection[iprevious:ii] if len(v) == 1)
                            if len(W) > 1 and not cs(fp(W)):
                                misspelled_indices.append((i + iprevious, i + ii, fp(W)))
                        
                        iprevious = ii + 1
                
            i = j + 1

        return word_count, misspelled_indices
    
    else:
        word_count = 0
        i = 0
        for j in chain((j for j, e in enumerate(T) if e in BP), (len(text),)):
            if j - i:
                if any(e in P for e in T[i:j]):
                    word_count += 1
                
            i = j + 1

        return word_count
