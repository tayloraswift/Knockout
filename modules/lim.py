from model.cat import cast_mono_line, calculate_vmetrics
from elements.node import Inline_element, Node
from model.olivia import Inline
    
class Limit(Inline_element):
    name = 'mod:lim'
    textfacing = True
    DNA = {'limit': {}}
    ADNA = []
    documentation = []
    
    def _load(self):
        pass
        
    def cast_inline(self, LINE, x, y, PP, F, FSTYLE):
        F_bottom, = self.styles(F, 'limit')

        limit = cast_mono_line(LINE, self.content, 13, PP, F_bottom)
        lim = cast_mono_line(LINE, 'lim', 13, PP, F)
        
        lim['x'] = x
        lim['y'] = y
        
        limit_asc, limit_desc = calculate_vmetrics(limit)
        lim_asc, lim_desc = calculate_vmetrics(lim)
        limit['x'] = x + (lim['advance'] - limit['advance'])*0.5
        limit['y'] = y + limit_asc
               
        width = lim['advance']
        
        ascent = lim_asc
        descent = limit_desc
        
        return Inline([lim, limit], width, ascent, descent)
        
    def __len__(self):
        return 7

members = [Limit]
inline = True
