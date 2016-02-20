from bulletholes.counter import TCounter as Counter
from style import styles

S= {'mod:bounded': {'symbol': {'big': 1},
                'bottom': {'small': 1},
                'top': {'small': 1}}
        }

class MS_Library(dict):
    def __init__(self, modules):
        D = {}
        for module in modules:
            ns = module.namespace
            E = module.DNA.copy()
            if ns in S:
                E.update(S[ns])
            D[module] = {T: Counter({styles.FTAGS[N]: C for N, C in V.items()}) for T, V in E.items()}
        dict.__init__(self, D)
        
