from bulletholes.counter import TCounter as Counter
from style import styles

S= {'mod:bounded': {'symbol': {'big': 1},
                'bottom': {'small': 1},
                'top': {'small': 1}},
    'mod:root': {'index': {'small': 1}},
    'table': {'table': {'tablecell': 1},
                'thead': {'tablehead': 1},
                'tleft': {'tableleft': 1}},
    'mod:pie': {'slice': {'h3': 1}},
        }

class MS_Library(dict):
    def __init__(self, inline, block):
        # save modules list
        self._inline = inline
        self._block = block
        self.turnover()
    
    def turnover(self):
        D = {}
        FTAGS = styles.FTAGS
        for module in self._inline:
            ns = module.namespace
            E = module.DNA.copy()
            if ns in S:
                E.update(S[ns])
            D[module] = {T: Counter(dict((FTAGS[N], C) for N, C in V.items())) for T, V in E.items()}
        
        PTAGS = styles.PTAGS
        for module in self._block:
            ns = module.namespace
            E = module.DNA.copy()
            if ns in S:
                E.update(S[ns])
            D[module] = {T: Counter(dict((PTAGS[N], C) for N, C in V.items())) for T, V in E.items()}
        dict.__init__(self, D)
