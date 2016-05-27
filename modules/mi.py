import cairo

from layout.line import cast_mono_line, calculate_vmetrics
from meredith.box import Inline

class Math_italic(Inline):
    name = 'mi'
    textfacing = True
    DNA = [('correct', 'float', 1), ('mathvariant', 'texttc', 'emphasis')]
    
    def _load(self):
        if self.content:
            self.char = self.content
        else:
            self.char = ['?']
    
    def _draw_annot(self, cr, O):
        cr.move_to(self._cad, 0)
        cr.rel_line_to(self._icorrection, 0)
        cr.rel_line_to(0, -self._rise)
        
        cr.close_path()
        cr.set_source_rgba(0, 0.8, 1, 0.4)
        cr.fill()
    
    def _cast_inline(self, LINE, x, y, PP, F, FSTYLE):
        C = cast_mono_line(LINE, self.char, 13, PP, F + self['mathvariant'])
        C['x'] = x
        C['y'] = y + FSTYLE['shift']
        self._cad = C['advance']
        
        ink = cairo.ScaledFont(C['fstyle']['font'], cairo.Matrix(yy=C['fstyle']['fontsize'], xx=C['fstyle']['fontsize']), cairo.Matrix(), cairo.FontOptions())
        self._rise = -ink.text_extents(self.char[-1])[1]
        self._icorrection = self._rise * self['correct'] * 0.17632698070846498 # tan(10°)
        
        charwidth = self._cad + self._icorrection
        ascent, descent = calculate_vmetrics(C)

        return [C], charwidth, ascent, descent, None, (self._draw_annot, x, y)

members = [Math_italic]
