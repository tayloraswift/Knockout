import enchant

def character(entity):
    if type(entity) is not str:
        entity = entity[0]
    return entity

struck = enchant.DictWithPWL("en_US","model/localdict.txt")

_prose = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789&@#$\'’-')
# these characters get read as word-breaks in speech
_breaking_prose = set(('</p>', '<br>', '—', '–', '/', '(', ')', '\\', '|', '=', '+', '_', ' '))

# NOT the same as prose breaks because of '.', ':', etc. *Does not include ''' or '’' because these are found word-internal and when used as quotes, encapsulate single characters*
_breaking_chars = set((' ', '</p>', '<p>', '<br>', '—', '–', '-', ':', '.', ',', ';', '/', '!', '?', '(', ')', '[', ']', '{', '}', '\\', '|', '=', '+', '_', '"', '“', '”' ))

def check_spelling(word):
    if word.isalpha():
        if word.islower():
            return struck.check(word)
        elif word.lower().capitalize() == word:
                return struck.check(word)
    else:
        if word[-2:] in ('’s', '\'s'):
            word = word[:-2]
            if word.islower():
                return struck.check(word)
            elif word.lower().capitalize() == word:
                return struck.check(word)
    return True

def words(text, startindex=0, spell=False):

    if spell:
        word_count = 0
        misspelled_indices = []
        
        previous = 0
        for i in (i for i, e in enumerate(text) if type(e) is str and e in _breaking_prose):
            if i - previous > 0:
                selection = text[previous:i]
                
                if any(type(e) is str and e in _prose for e in selection):
                    word_count += 1
                    
                    iprevious = 0
                    for ii in (ii for ii, e in enumerate(selection + [' ']) if type(e) is str and e in _breaking_chars):
                        if ii - iprevious > 0:
                            W = ''.join([v for v in selection[iprevious:ii] if len(v) == 1])
                            if len(W) > 1 and not check_spelling(W):
                                misspelled_indices.append((startindex + previous + iprevious, startindex + previous + ii, W))
                        
                        iprevious = ii + 1
                
            previous = i + 1

        return word_count, misspelled_indices
    
    else:
        word_count = 0
        previous = 0
        for i in (i for i, e in enumerate(text) if type(e) is str and e in _breaking_prose):
            if i - previous > 0:
                if any(True for e in text[previous:i] if type(e) is str and e in _prose):
                    word_count += 1
                
            previous = i + 1

        return word_count
