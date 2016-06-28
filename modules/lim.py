from layout.otline import cast_mono_line
from meredith.box import Inline
    
class Limit(Inline):
    name = 'mod:lim'
    textfacing = True
    
    DNA = [('cl_limit', 'texttc', 'small')]
    
    def _load(self):
        pass
        
    def _cast_inline(self, LINE, runinfo, F, FSTYLE):
        limit = cast_mono_line(LINE, self.content, runinfo, F + self['cl_limit'])
        lim = cast_mono_line(LINE, 'lim', runinfo, F)
        
        width = max(lim['advance'], limit['advance'])
        
        lim['x'] = (width - lim['advance'])*0.5
        lim['y'] = 0
        
        limit['x'] = (width - limit['advance'])*0.5
        limit['y'] = -lim['descent'] + limit['ascent']
        
        return [lim, limit], width, lim['ascent'], limit['descent']

members = [Limit]
