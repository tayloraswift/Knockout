import enchant

# NOT the same as prose breaks because of '.', ':', '<f>', etc. *Does not include ''' or '’' because these are found word-internal and when used as quotes, encapsulate single characters*
_breaking_chars = set((' ', '</p>', '<p>', '<f>', '</f>', '<br>', '—', '–', '-', ':', '.', ',', ';', '/', '!', '?', '(', ')', '[', ']', '{', '}', '\\', '|', '=', '+', '_', '"', '“', '”' ))

def character(entity):
    if type(entity) is tuple:
        entity = entity[0]
    return entity

struck = enchant.DictWithPWL("en_US","model/localdict.txt")

_prose = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789&@#$\'’-')
# these characters get read as word-breaks in speech
_breaking_prose = set(('</p>', '<br>', '—', '–', '/', '(', ')', '\\', '|', '=', '+', '_', ' '))

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

def words(text, spell=False):

    if spell:
        word_count = 0
        misspelled_indices = []
        
        previous = 0
        for i in (i for i, e in enumerate(text) if e in _breaking_prose):
            if i - previous > 0:
                selection = text[previous:i]
                word = ''.join([e for e in selection if e in _prose])
                
                if word:
                    word_count += 1
                    if len(word) == len(selection):
                        start = previous
                        end = i
                    else:
                        start = previous + next(i for i, a in enumerate(selection) if a in _prose)
                        end = i - next(i for i, a in enumerate(reversed(selection)) if a in _prose)
                    
                    if '-' in word:
                        fragments = word.split('-')
                        if not check_spelling(fragments[0]):
                            misspelled_indices.append((start, end, fragments[0]))
                        if not check_spelling(fragments[1]):
                            misspelled_indices.append((start, end, fragments[1]))
                    else:
                        if not check_spelling(word):
                            misspelled_indices.append((start, end, word))
                
            previous = i + 1

        return word_count, misspelled_indices
    
    else:
        word_count = 0
        previous = 0
        for i in (i for i, e in enumerate(text) if e in _breaking_prose):
            if i - previous > 0:
                word_count += 1
            previous = i + 1

        return word_count

