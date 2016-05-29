from itertools import chain

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

_prose = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789&@#$\'’-')
# these characters get read as word-breaks in speech
_breaking_prose = set(('<br/>', '—', '–', '/', '(', ')', '\\', '|', '=', '+', '_', ' '))

# NOT the same as prose breaks because of '.', ':', etc. *Does not include ''' or '’' because these are found word-internal and when used as quotes, encapsulate single characters*
_breaking_chars = set((' ', '<fo/>', '<fc/>', '<br/>', '—', '–', '-', ':', '.', ',', ';', '/', '!', '?', '(', ')', '[', ']', '{', '}', '\\', '|', '=', '+', '_', '"', '“', '”', '<', '>' ))

def words(text, spell=False):
    T = list(map(str, text))

    BP = _breaking_prose
    if spell:
        cs = check_spelling
        fp = fold_possesive
        P = _prose
        BC = _breaking_chars
        
        word_count = 0
        misspelled_indices = []
        
        i = 0
        for j in chain((j for j, e in enumerate(T) if e in BP), (len(text),)):
            if j - i:
                selection = T[i:j]
                
                if any(e in P for e in selection):
                    word_count += 1
                    
                    iprevious = 0
                    for ii in (ii for ii, e in enumerate(selection + [' ']) if e in BC):
                        if ii - iprevious:
                            W = ''.join([v for v in selection[iprevious:ii] if len(v) == 1])
                            if len(W) > 1 and not cs(fp(W)):
                                misspelled_indices.append((i + iprevious, i + ii, fp(W)))
                        
                        iprevious = ii + 1
                
            i = j + 1

        return word_count, misspelled_indices
    
    else:
        word_count = 0
        previous = 0
        for i in chain((i for i, e in enumerate(T) if type(e) is str and e in BP), (len(text),)):
            if i - previous:
                if any(e in _prose for e in T[previous:i]):
                    word_count += 1
                
            previous = i + 1

        return word_count
