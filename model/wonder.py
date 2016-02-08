_fail = '\033[91m'
_endc = '\033[0m'
_bold = '\033[1m'

def check_spelling(word):
    if word[-2:] in ('’s', '\'s'):
        word = word[:-2]
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

additional_words_file = 'libraries/hunspell/add.txt'

if hunspell is not None:
    struck = hunspell.HunSpell('libraries/hunspell/en_US.dic', 'libraries/hunspell/en_US.aff')
    with open(additional_words_file) as A:
        for word in A.read().splitlines():
            struck.add(word.strip())
else:
    check_spelling = lambda W: True

_prose = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789&@#$\'’-')
# these characters get read as word-breaks in speech
_breaking_prose = set(('</p>', '<br/>', '—', '–', '/', '(', ')', '\\', '|', '=', '+', '_', ' '))

# NOT the same as prose breaks because of '.', ':', etc. *Does not include ''' or '’' because these are found word-internal and when used as quotes, encapsulate single characters*
_breaking_chars = set((' ', '</p>', '<p>', '<br/>', '—', '–', '-', ':', '.', ',', ';', '/', '!', '?', '(', ')', '[', ']', '{', '}', '\\', '|', '=', '+', '_', '"', '“', '”' ))

def words(text, startindex=0, spell=False):

    T = list(map(str, text))

    if spell:
        word_count = 0
        misspelled_indices = []
        
        i = 0
        for j in (j for j, e in enumerate(T) if e in _breaking_prose):
            if j - i:
                selection = T[i:j]
                
                if any(e in _prose for e in selection):
                    word_count += 1
                    
                    iprevious = 0
                    for ii in (ii for ii, e in enumerate(selection + [' ']) if e in _breaking_chars):
                        if ii - iprevious:
                            W = ''.join([v for v in selection[iprevious:ii] if len(v) == 1])
                            if len(W) > 1 and not check_spelling(W):
                                misspelled_indices.append((startindex + i + iprevious, startindex + i + ii, W))
                        
                        iprevious = ii + 1
                
            i = j + 1

        return word_count, misspelled_indices
    
    else:
        word_count = 0
        previous = 0
        for i in (i for i, e in enumerate(T) if type(e) is str and e in _breaking_prose):
            if i - previous:
                if any(e in _prose for e in T[previous:i]):
                    word_count += 1
                
            previous = i + 1

        return word_count
