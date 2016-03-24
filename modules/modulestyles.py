from bulletholes.counter import TCounter as Counter
from style import styles

S= {'_global': {'_left': {('p', '_left'): 1},
                '_center': {('p', '_center'): 1},
                '_right': {('p', '_right'): 1}},
    
    'mi': {'mi': {('f', 'emphasis'): 1}},
    'mod:bounded': {'symbol': {('f', 'big'): 1},
                'bounds': {('f', 'small'): 1}},
    'mod:root': {'index': {('f', 'small'): 1}},
#    'mod:fraction': {'numerator': {('f', 'small'): 1}, 'denominator': {('f', 'small'): 1}},
    'table': {'table': {('p', 'tablecell'): 1},
                'thead': {('p', 'tablecell'): 1, ('p', 'h1'): 1},
                'tleft': {('p', 'tablecell'): 1, ('p', 'firstchild'): 1}},
    'mod:pie': {'slice': {('p', 'key'): 1}},
    
    'mod:plot': {'num': {('f', 'small'): 1},
                'key': {('p', 'key'): 1},
                'axis': {('p', 'tablecell'): 1, ('p', 'h1'): 1}}
        }

class MS_Library(dict):
    def __init__(self, modslist):
        # save modules list
        self._modslist = modslist
        self.turnover()
    
    def turnover(self):
        D = {}
        TAGS = {'f': styles.FTAGS, 'p': styles.PTAGS}
        for ns, module in self._modslist.items():
            E = module.DNA.copy()
            E.update(S['_global'])
            if ns in S:
                E.update(S[ns])
            D[module] = {T: Counter(dict((TAGS[level][N], C) for (level, N), C in V.items())) for T, V in E.items()}
        dict.__init__(self, D)
