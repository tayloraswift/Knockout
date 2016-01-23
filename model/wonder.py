from hunspell import hunspell
from itertools import groupby

def character(entity):
    if type(entity) is not str:
        entity = entity[0]
    return entity

struck = hunspell.HunSpell('hunspell/en_US.dic', 'hunspell/en_US.aff')

_prose = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789&@#$\'’-')
# these characters get read as word-breaks in speech
_breaking_prose = set(('</p>', '<br>', '—', '–', '/', '(', ')', '\\', '|', '=', '+', '_', ' '))

# NOT the same as prose breaks because of '.', ':', etc. *Does not include ''' or '’' because these are found word-internal and when used as quotes, encapsulate single characters*
_breaking_chars = set((' ', '</p>', '<p>', '<br>', '—', '–', '-', ':', '.', ',', ';', '/', '!', '?', '(', ')', '[', ']', '{', '}', '\\', '|', '=', '+', '_', '"', '“', '”' ))

def check_spelling(word):
    if word[-2:] in ('’s', '\'s'):
        word = word[:-2]
    if word.isalpha() and not word.isupper():
        return struck.spell(word.encode('latin-1', 'ignore'))
    return True


def words(text, startindex=0, spell=False):

    T = [e if type(e) is str else e[0] for e in text]

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
