import cairo

from model.cat import cast_mono_line, calculate_vmetrics
from elements.elements import Inline_element
from model.olivia import Inline

class Math_italic(Inline_element):
    nodename = 'mi'
    DNA = {'mi': {}}
    ADNA = [('char', '', 'str'), ('correct', 1, 'float')]
    documentation = [(0, nodename)]
    
    def _load(self):
        ch, self._cfactor = self.get_attributes()
        if ch:
            self.char = ch
        else:
            self.char = '􏿿'
    
    def _draw_annot(self, cr, O):
        cr.move_to(self._cad, 0)
        cr.rel_line_to(self._icorrection, 0)
        cr.rel_line_to(0, -self._rise)
        
        cr.close_path()
        cr.set_source_rgba(0, 0.8, 1, 0.4)
        cr.fill()
    
    def cast_inline(self, LINE, x, y, PP, F, FSTYLE):
        F_mi, = self.styles(F, 'mi')
        
        C = cast_mono_line(LINE, list(self.char), 13, PP, F_mi)
        C['x'] = x
        C['y'] = y + FSTYLE['shift']
        self._cad = C['advance']
        
        ink = cairo.ScaledFont(C['fstyle']['font'], cairo.Matrix(yy=C['fstyle']['fontsize'], xx=C['fstyle']['fontsize']), cairo.Matrix(), cairo.FontOptions())
        self._rise = -ink.text_extents(self.char[-1])[1]
        self._icorrection = self._rise * self._cfactor * 0.17632698070846498 # tan(10°)
        
        charwidth = self._cad + self._icorrection
        ascent, descent = calculate_vmetrics(C)

        return _MInline(C, charwidth, ascent, descent, self._draw_annot, x, y)

    def __len__(self):
        return 11

class _MInline(Inline):
    def __init__(self, lines, width, A, D, draw, x, y):
        Inline.__init__(self, lines, width, A, D)
        self._draw = draw
        self._x = x
        self._y = y
    
    def deposit_glyphs(self, repository, x, y):
        repository['_paint_annot'].append((self._draw, self._x + x, self._y + y))
        self._LINES.deposit(repository, x, y)

members = [Math_italic]
inline = True
