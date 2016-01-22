#          b
#    a + —————
#         cd
#———————————————————
#       f
#      ——— + h
#       g
# e + ————————— + j
#         i

class _Fraction(object):
    def __init__(self, top, bottom):
        self.top = top
        self.bottom = bottom

F = _Fraction( ['a', ' ', '+', _Fraction(['b'], ['c', 'd'])] , ['e', ' ', '+', _Fraction( [ _Fraction(['f'], ['g']), '+', ' ', 'h' ] , ['i'] ), 'j' ] )

def internal_fractions(branch):
    return [e for e in branch if isinstance(e, _Fraction) ]

trees = {()}

def monsters(F, root):
    trees.remove(root)
    trees.update({root + (0,), root + (1,), root + (-1,)})
    top = internal_fractions(F.top)
    bottom = internal_fractions(F.bottom)
    if top:
        for R in top:
            monsters(R, root + (1,))

    if bottom:
        for R in bottom:
            monsters(R, root + (-1,))

monsters(F, ())
print (sorted(trees))
