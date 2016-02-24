import cairo

from model.cat import cast_mono_line, calculate_vmetrics
from elements.elements import Inline_SE_element
from model.olivia import Inline

_namespace = 'mi'

class Math_italic(Inline_SE_element):
    namespace = _namespace
    tags = {}
    DNA = {'mi': {}}
    
    ADNA = {_namespace: [('char', '', 'str')]}
    documentation = [(0, _namespace)]
    
    def _load(self, A):
        self._tree = A
        ch, = self._get_attributes(_namespace)
        if ch:
            self.char = ch
        else:
            self.char = '􏿿'
    
    def cast_inline(self, x, y, leading, PP, F, FSTYLE):
        F_mi, = self._modstyles(F, 'mi')
        
        C = cast_mono_line(list(self.char), 13, PP, F_mi)
        C['x'] = x
        C['y'] = y + FSTYLE['shift']
        
        ink = cairo.ScaledFont(C['fstyle']['font'], cairo.Matrix(yy=C['fstyle']['fontsize'], xx=C['fstyle']['fontsize']), cairo.Matrix(), cairo.FontOptions())
        rise = -ink.text_extents(self.char[-1])[1]
        icorrection = rise * 0.19438030913771848 # tan(13°)
        
        charwidth = C['advance'] + icorrection
        ascent, descent = calculate_vmetrics(C)

        return _MInline(C, charwidth, ascent, descent)

    def __len__(self):
        return 11

class _MInline(Inline):
    
    def deposit_glyphs(self, repository, x, y):
        self._LINES.deposit(repository, x, y)
