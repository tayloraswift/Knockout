from fonts import hb

lang_properties =  {'numeric': (False, hb.script_t.LATIN),
                    'english': (False, hb.script_t.LATIN),
                    'spanish': (False, hb.script_t.LATIN),
                    'arabic' : (True , hb.script_t.ARABIC),
                    'hebrew' : (True , hb.script_t.HEBREW),}

def interpret_locale(S):
    if S in lang_properties:
        return S
    else:
        return None

def generate_runinfo(language):
    return ( * lang_properties[language], language)
