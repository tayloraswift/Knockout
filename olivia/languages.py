directionality =   {'english': False,
                    'spanish': False,
                    'arabic' : True,
                    'hebrew' : True,}

def interpret_locale(S):
    if S in directionality:
        return S
    else:
        return None