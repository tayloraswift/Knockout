from model.cat import cast_mono_line
from IO.xml import print_attrs
from elements.elements import Mod_element
from edit.paperairplanes import interpret_int

namespace = 'mod:bounded'
tags = {namespace + ':' + T for T in ('symbol', 'bottom', 'top')}

class Bounded(Mod_element):
    def _load(self, L):
        self._tree = L
        symbol = next(E for tag, E in L[1] if tag[0] == namespace + ':symbol')
        a = next(E for tag, E in L[1] if tag[0] == namespace + ':bottom')
        b = next(E for tag, E in L[1] if tag[0] == namespace + ':top')
        
        align = interpret_int(L[0][1].get('align', 1))
        if align:
            self.cast_inline = self._cast_inline_inline
        else:
            self.cast_inline = self._cast_inline_display
        
        self._INLINE = [symbol, a, b]
    
    def represent(self, indent):
        lines = [[indent, print_attrs( * self._tree[0])]]
        for tag, E in self._tree[1]:
            content = self._SER(E, indent + 2)
            content[0] = [indent + 1, print_attrs( * tag) + content[0][1]]
            content[-1][1] += '</' + tag[0] + '>'
            
            lines.extend(content)
        lines.append([indent, '</' + namespace + '>'])
        return lines
    
    def _cast_inline_inline(self, x, y, leading, PP, F, FSTYLE):
        self._color = FSTYLE['color']
        fontsize = FSTYLE['fontsize']

        symbol = cast_mono_line(self._INLINE[0], 13, PP, F)
        symbol['x'] = x
        symbol['y'] = y
        symbol['hyphen'] = None
        
        a = cast_mono_line(self._INLINE[1], 13, PP, F)
        b = cast_mono_line(self._INLINE[2], 13, PP, F)

        a['x'] = x + symbol['advance'] 
        a['y'] = y + fontsize * 0.6
        a['hyphen'] = None
        b['x'] = x + symbol['advance'] + fontsize*0.2
        b['y'] = y - fontsize * 0.6
        b['hyphen'] = None
        
        width = max(a['advance'] + a['x'], b['advance'] + b['x']) - symbol['x']
        
        return _MInline([symbol, a, b], width, leading)

    def _cast_inline_display(self, x, y, leading, PP, F, FSTYLE):
        self._color = FSTYLE['color']
        fontsize = FSTYLE['fontsize']

        symbol = cast_mono_line(self._INLINE[0], 13, PP, F)
        
        a = cast_mono_line(self._INLINE[1], 13, PP, F)
        b = cast_mono_line(self._INLINE[2], 13, PP, F)
        
        width = max(a['advance'], b['advance'], symbol['advance'])

        symbol['x'] = x + (width - symbol['advance']) / 2
        symbol['y'] = y
        symbol['hyphen'] = None

        a['x'] = x + (width - a['advance']) / 2
        a['y'] = y + fontsize
        a['hyphen'] = None
        b['x'] = x + (width - b['advance']) / 2
        b['y'] = y - fontsize
        b['hyphen'] = None
        
        return _MInline([symbol, a, b], width, leading)
        
    def __len__(self):
        return 9

class _MInline(object):
    def __init__(self, lines, width, height):
        self._LINES = lines
        self.width = width
        self.height = height
    
    def deposit_glyphs(self, repository, x, y):
        for line in self._LINES:
            line.deposit(repository, x, y)
