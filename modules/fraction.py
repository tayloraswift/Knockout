from model.cat import cast_mono_line, calculate_vmetrics
from elements.elements import Inline_element, Node
from model.olivia import Inline

_namespace = 'mod:frac'

class Numerator(Node):
    name = _namespace + ':n'
    textfacing = True

class Denominator(Node):
    name = _namespace + ':d'
    textfacing = True
    
class Fraction(Inline_element):
    name = _namespace
    DNA = {'numerator': {}, 'denominator': {}}
    documentation = [(0, name), (1, 'numerator'), (1, 'denominator')]
    
    def _load(self):
        self._numerator = next(e for e in self.content if type(e) is Numerator)
        self._denominator = next(e for e in self.content if type(e) is Denominator)

    def _draw_vinculum(self, cr):
        cr.set_source_rgba( * self._color)
        cr.rectangle(0, 0, self._fracwidth, 0.5)
        cr.fill()
        
    def cast_inline(self, LINE, x, y, PP, F, FSTYLE):
        self._color = FSTYLE['color']
        F_numerator, F_denominator, = self.styles(F, 'numerator', 'denominator')
        
        ascent, descent = FSTYLE.vmetrics()
        vy = int(FSTYLE['fontsize'] * 0.25)
        
        numerator = cast_mono_line(LINE, self._numerator.content, 13, PP, F_numerator)
        denominator = cast_mono_line(LINE, self._denominator.content, 13, PP, F_denominator)
        
        nascent, ndescent = calculate_vmetrics(numerator)
        nwidth = numerator['advance']
        dascent, ddescent = calculate_vmetrics(denominator)
        dwidth = denominator['advance']
        
        fracwidth = max(nwidth, dwidth) + LINE['leading']/2
        
        numerator['x'] = x + (fracwidth - nwidth)/2
        numerator['y'] = y - vy + ndescent
        
        denominator['x'] = x + (fracwidth - dwidth)/2
        denominator['y'] = y - vy + dascent
        
        fascent = vy + nascent - ndescent
        fdescent = vy - dascent + ddescent
        self._fracwidth = fracwidth
        return _MInline([numerator, denominator], fracwidth, fascent, fdescent, self._draw_vinculum, x, y - vy)

    def __len__(self):
        return 11

class _MInline(Inline):
    def __init__(self, lines, width, A, D, vinculum, x, y):
        Inline.__init__(self, lines, width, A, D)
        self._draw_vinculum = vinculum
        self._x = x
        self._vy = y
    
    def deposit_glyphs(self, repository, x, y):
        for line in self._LINES:
            line.deposit(repository, x, y)
        repository['_paint'].append((self._draw_vinculum, x + self._x, y + self._vy))

members = [Fraction, Numerator, Denominator]
inline = True
