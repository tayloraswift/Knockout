from bulletholes.counter import TCounter as Counter
from style import styles

S= {'mi': {'mi': {('f', 'emphasis'): 1}},
    'mod:bounded': {'symbol': {('f', 'big'): 1},
                'bottom': {('f', 'small'): 1},
                'top': {('f', 'small'): 1}},
    'mod:root': {'index': {('f', 'small'): 1}},
    'table': {'table': {('p', 'tablecell'): 1},
                'thead': {('p', 'tablehead'): 1},
                'tleft': {('p', 'tableleft'): 1}},
    'mod:pie': {'slice': {('p', 'key'): 1}},
    
    '_graph': {'num': {('f', 'small'): 1},
                'dataset': {('p', 'key'): 1},
                'y': {('p', 'tablecell'): 1, ('p', 'tablehead'): 1},
                'x': {('p', 'tablecell'): 1, ('p', 'tablehead'): 1}}
        }

class MS_Library(dict):
    def __init__(self, inline, block):
        # save modules list
        self._modslist = inline + block
        self.turnover()
    
    def turnover(self):
        D = {}
        TAGS = {'f': styles.FTAGS, 'p': styles.PTAGS}
        for module in self._modslist:
            ns = module.namespace
            E = module.DNA.copy()
            if ns in S:
                E.update(S[ns])
            D[module] = {T: Counter(dict((TAGS[level][N], C) for (level, N), C in V.items())) for T, V in E.items()}
        dict.__init__(self, D)
