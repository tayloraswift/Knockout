from model.cat import cast_mono_line
from IO.xml import print_attrs
from elements.elements import Inline_element

namespace = 'mod:fraction'
tags = {namespace + ':' + T for T in ('numerator', 'denominator')}

def _fracbound(glyphs, fontsize):
    if glyphs:
        subfrac = [glyph[6].height for glyph in glyphs if glyph[0] == -89]
        if subfrac:
            height = max(subfrac)
        else:
            height = fontsize
    else:
        height = fontsize
    return height

class Fraction(Inline_element):
    def _load(self, L):
        self._tree = L
        
        numerator = next(E for tag, E in L[1] if tag[0] == namespace + ':numerator')
        denominator = next(E for tag, E in L[1] if tag[0] == namespace + ':denominator')
        
        self._INLINE = [numerator, denominator]
    
    def represent(self, indent):
        lines = [[indent, print_attrs( * self._tree[0])]]
        for tag, E in self._tree[1]:
            content = self._SER(E, indent + 2)
            content[0] = [indent + 1, print_attrs( * tag) + content[0][1]]
            content[-1][1] += '</' + tag[0] + '>'
            
            lines.extend(content)
        lines.append([indent, '</' + namespace + '>'])
        return lines

    def _draw_vinculum(self, cr, x, y):
        cr.set_source_rgba( * self._color)
        cr.rectangle(x + self._vx, int(y + self._vy), self._fracwidth, 0.5)
        cr.fill()
    
    def cast_inline(self, x, y, leading, PP, F, FSTYLE):
        self._color = FSTYLE['color']
        fontsize = FSTYLE['fontsize']
        vy = y - fontsize/4
        numerator = cast_mono_line(self._INLINE[0], 13, PP, F)
        denominator = cast_mono_line(self._INLINE[1], 13, PP, F)
        
        nheight = _fracbound(numerator['GLYPHS'], fontsize)
        nwidth = numerator['advance']
        dheight = _fracbound(denominator['GLYPHS'], fontsize)
        dwidth = denominator['advance']
        
        fracwidth = max(nwidth, dwidth) + leading/2
        fracheight = nheight + dheight
        
        numerator['x'] = x + (fracwidth - nwidth)/2
        numerator['y'] = vy - nheight/2
        numerator['hyphen'] = None
        denominator['x'] = x + (fracwidth - dwidth)/2
        denominator['y'] = vy + dheight
        denominator['hyphen'] = None
        
        self._fracwidth = fracwidth
        self._vy = vy
        self._vx = x
        return _MInline([numerator, denominator], self._draw_vinculum, fracwidth, fracheight)

    def __len__(self):
        return 11

class _MInline(object):
    def __init__(self, lines, vinculum, width, height):
        self._LINES = lines
        self._draw_vinculum = vinculum
        self.width = width
        self.height = height
    
    def deposit_glyphs(self, repository, x, y):
        for line in self._LINES:
            line.deposit(repository, x, y)
        repository['_paint'].append(lambda cr: self._draw_vinculum(cr, x, y))
