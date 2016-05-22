from itertools import chain

STYLING = {}

textstyles = []
for name, attrs in STYLING['FONTSTYLES'].items():
    attrs['name'] = name
    textstyles.append('<textstyle ' + ' '.join(''.join((k, '="', str(v), '"')) for k, v in attrs.items()) + '/>')

TS = '<textstyles>\n    ' + '\n    '.join(textstyles) + '\n</textstyles>'

def counter2string(C):
    return '^'.join(chain.from_iterable((T for i in range(V)) if V > 0 else 
            ('~' + T for i in range(abs(V))) for T, V in sorted(C.items(), key=lambda k: k[0])))

blockstyles = []

for attrs, cls in STYLING['PARASTYLES'][1]:
    if 'fontclasses' in attrs:
        members = attrs.pop('fontclasses')[1]
    else:
        members = None
    attrs['class'] = counter2string(cls)
    BS = '<blockstyle ' + ' '.join(''.join((k, '="', str(v), '"')) for k, v in attrs.items())
    
    if members is None:
        blockstyles.append(BS + '/>')
    else:
        blockstyles.append(BS + '>')
        for N, C in members:
            blockstyles.append('<memberstyle class="' + counter2string(C) + '" textstyle="' + N + '"/>')
        blockstyles.append('</blockstyle>')

BS = '<blockstyles>\n    ' + '\n    '.join(blockstyles) + '\n</blockstyles>'

print(TS)
print(BS)
