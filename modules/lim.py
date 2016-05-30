from layout.line import cast_mono_line, calculate_vmetrics
from meredith.box import Inline
    
class Limit(Inline):
    name = 'mod:lim'
    textfacing = True
    
    DNA = [('cl_limit', 'texttc', 'small')]
    
    def _load(self):
        pass
        
    def _cast_inline(self, LINE, x, y, PP, F, FSTYLE):
        limit = cast_mono_line(LINE, self.content, 13, PP, F + self['cl_limit'])
        lim = cast_mono_line(LINE, 'lim', 13, PP, F)
        
        width = max(lim['advance'], limit['advance'])
        
        lim['x'] = x + (width - lim['advance'])*0.5
        lim['y'] = y
        
        limit_asc, limit_desc = calculate_vmetrics(limit)
        lim_asc, lim_desc = calculate_vmetrics(lim)
        limit['x'] = x + (width - limit['advance'])*0.5
        limit['y'] = y - lim_desc + limit_asc
        
        return [lim, limit], width, lim_asc, limit_desc

members = [Limit]
