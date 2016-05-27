from layout.line import cast_mono_line, calculate_vmetrics
from meredith.box import Box, Inline

_namespace = 'mod:frac'

class Numerator(Box):
    name = _namespace + ':n'
    textfacing = True

class Denominator(Box):
    name = _namespace + ':d'
    textfacing = True
    
class Fraction(Inline):
    name = _namespace
    
    DNA = [('cl_fraction', 'texttc', '')]
    
    def _load(self):
        self._numerator, self._denominator = self.find_nodes(Numerator, Denominator)

    def _draw_vinculum(self, cr):
        cr.set_source_rgba( * self._color)
        cr.rectangle(0, 0, self._fracwidth, 0.5)
        cr.fill()
        
    def _cast_inline(self, LINE, x, y, PP, F, FSTYLE):
        self._color = FSTYLE['color']
        if self['cl_fraction']:
            F_fraction = F + self['cl_fraction']
        else:
            F_fraction = F
        
        ascent, descent = FSTYLE.vmetrics()
        vy = int(FSTYLE['fontsize'] * 0.25)
        
        numerator = cast_mono_line(LINE, self._numerator.content, 13, PP, F_fraction)
        denominator = cast_mono_line(LINE, self._denominator.content, 13, PP, F_fraction)
        
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
        return [numerator, denominator], fracwidth, fascent, fdescent, (self._draw_vinculum, x, y - vy)

members = [Fraction, Numerator, Denominator]
