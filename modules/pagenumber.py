from layout.otline import cast_mono_line
from meredith.box import Box, Inline

class Page_number(Inline):
    name = 'pn'
    DNA = [('offset', 'int', 0)]
    
    def _load(self):
        pass
    
    def _paint_annot(self, cr, O):
        cr.move_to(0, 0)
        cr.rel_line_to(2, 0)
        cr.rel_line_to(0, -2)
        
        cr.close_path()
        cr.set_source_rgba(0, 0.8, 1, 0.4)
        cr.fill()
    
    def _cast_inline(self, LINE, runinfo, F, FSTYLE):
        C = cast_mono_line(LINE, list(str(LINE['page'] + self['offset'])), runinfo, F)
        C['x'] = 0
        C['y'] = FSTYLE['shift']

        return [C], C['advance'], C['ascent'], C['descent'], None, (self._paint_annot, 0, 0)

members = [Page_number]
