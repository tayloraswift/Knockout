from model.cat import cast_mono_line, calculate_vmetrics
from elements.elements import Inline_SE_element
from model.olivia import Inline

_namespace = 'pn'

class Page_number(Inline_SE_element):
    namespace = _namespace
    tags = {}
    DNA = {'pn': {}}
    
    ADNA = {_namespace: [('offset', '0', 'int')]}
    documentation = [(0, _namespace)]
    
    def _load(self, A):
        self._tree = A
        self._offset = self._get_attributes(_namespace)
    
    def _draw_annot(self, cr, O):
        cr.move_to(0, 0)
        cr.rel_line_to(2, 0)
        cr.rel_line_to(0, -2)
        
        cr.close_path()
        cr.set_source_rgba(0, 0.8, 1, 0.4)
        cr.fill()
    
    def cast_inline(self, LINE, x, y, PP, F, FSTYLE):
        F_pn, = self._modstyles(F, 'pn')
        C = cast_mono_line(LINE, list(str(LINE['page'])), 13, PP, F_pn)
        C['x'] = x
        C['y'] = y + FSTYLE['shift']
        self._cad = C['advance']
        
        ascent, descent = calculate_vmetrics(C)

        return _MInline(C, C['advance'], ascent, descent, self._draw_annot, x, y)

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
