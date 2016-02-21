from model.cat import cast_mono_line, calculate_vmetrics
from IO.xml import print_attrs
from elements.elements import Inline_element

_namespace = 'mod:fraction'

class Fraction(Inline_element):
    namespace = _namespace
    tags = {_namespace + ':' + T for T in ('numerator', 'denominator')}
    DNA = {'numerator': {},
            'denominator': {}}
    
    def _load(self, L):
        self._tree = L
        
        numerator = next(E for tag, E in L[1] if tag[0] == self.namespace + ':numerator')
        denominator = next(E for tag, E in L[1] if tag[0] == self.namespace + ':denominator')
        
        self._INLINE = [numerator, denominator]
    
    def represent(self, indent):
        lines = [[indent, print_attrs( * self._tree[0])]]
        for tag, E in self._tree[1]:
            content = self._SER(E, indent + 2)
            content[0] = [indent + 1, print_attrs( * tag) + content[0][1]]
            content[-1][1] += '</' + tag[0] + '>'
            
            lines.extend(content)
        lines.append([indent, '</' + self.namespace + '>'])
        return lines

    def _draw_vinculum(self, cr, x, y):
        cr.set_source_rgba( * self._color)
        cr.rectangle(x + self._vx, y + self._vinc_y, self._fracwidth, 0.5)
        cr.fill()
        
    def cast_inline(self, x, y, leading, PP, F, FSTYLE):
        self._color = FSTYLE['color']
        F_numerator, F_denominator = self._modstyles(F, 'numerator', 'denominator')
        
        ascent, descent = FSTYLE.vmetrics()
        vy = FSTYLE['fontsize'] * 0.25
        
        numerator = cast_mono_line(self._INLINE[0], 13, PP, F_numerator)
        denominator = cast_mono_line(self._INLINE[1], 13, PP, F_denominator)
        
        nascent, ndescent = calculate_vmetrics(numerator)
        nwidth = numerator['advance']
        dascent, ddescent = calculate_vmetrics(denominator)
        dwidth = denominator['advance']
        
        fracwidth = max(nwidth, dwidth) + leading/2
        
        numerator['x'] = x + (fracwidth - nwidth)/2
        numerator['y'] = y - vy + ndescent
        numerator['hyphen'] = None
        denominator['x'] = x + (fracwidth - dwidth)/2
        denominator['y'] = y - vy + dascent
        denominator['hyphen'] = None
        
        fascent = vy + nascent - ndescent
        fdescent = vy - dascent + ddescent
        self._fracwidth = fracwidth
        self._vinc_y = y - vy
        self._vx = x
        return _MInline([numerator, denominator], self._draw_vinculum, fracwidth, fascent, fdescent)

    def __len__(self):
        return 11

class _MInline(object):
    def __init__(self, lines, vinculum, width, A, D):
        self._LINES = lines
        self._draw_vinculum = vinculum
        self.width = width
        self.ascent = A
        self.descent = D
    
    def deposit_glyphs(self, repository, x, y):
        for line in self._LINES:
            line.deposit(repository, x, y)
        repository['_paint'].append(lambda cr: self._draw_vinculum(cr, x, y))
