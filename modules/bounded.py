from layout.otline import cast_mono_line
from meredith.box import Box, Inline

_namespace = 'mod:bounded'

class Symbol(Box):
    name = _namespace + ':sym'
    textfacing = True

class Bound(Box):
    name = _namespace + ':a'
    textfacing = True
    
class Bounded(Inline):
    name = _namespace
    
    DNA = [('align', 'int', 1), ('cl_symbol', 'texttc', 'big'), ('cl_bound', 'texttc', 'small')]
    
    def _load(self):
        self._symbol, self._a, self._b = self.find_nodes(Symbol, Bound, Bound)
        
        if self['align']:
            self._cast_inline = self._cast_inline_inline
        else:
            self._cast_inline = self._cast_inline_display

    def _mono(self, LINE, runinfo, F):
        F_small = F + self['cl_bound']
        symbol = cast_mono_line(LINE, self._symbol.content, runinfo, F + self['cl_symbol'])
        a = cast_mono_line(LINE, self._a.content, runinfo, F_small)
        b = cast_mono_line(LINE, self._b.content, runinfo, F_small)
        return symbol, a, b
        
    def _cast_inline_inline(self, LINE, runinfo, F, FSTYLE):
        symbol, a, b = self._mono(LINE, runinfo, F)
        
        symbol['x'] = 0
        symbol['y'] = 0
        
        symbol_fontsize = symbol['fstyle']['fontsize']
        symbol_asc = symbol['ascent'] - symbol_fontsize * 0.1
        
        a['x'] = symbol['advance']
        a['y'] = -symbol['descent']
        
        b['x'] = symbol['advance'] + symbol_fontsize*0.1
        b['y'] = -symbol_asc - b['fstyle']['fontsize']*0.1 + b['fstyle']['__fontmetrics__'][0] #only align to unexpanded metrics
               
        width = max(a['advance'] + a['x'], b['advance'] + b['x']) - symbol['x']
        
        ascent = -b['y'] + b['ascent']
        descent = -a['y'] + a['descent']
        
        return [symbol, a, b], width, ascent, descent

    def _cast_inline_display(self, LINE, runinfo, F, FSTYLE):
        symbol, a, b = self._mono(LINE, runinfo, F)
        
        width = max(a['advance'], b['advance'], symbol['advance'])

        symbol['x'] = (width - symbol['advance']) * 0.5
        symbol['y'] = 0

        symbol_asc = symbol['ascent'] - symbol['fstyle']['fontsize'] * 0.1
        
        a['x'] = (width - a['advance']) * 0.5
        a['y'] = -symbol['descent'] + a['ascent']
        
        b['x'] = (width - b['advance']) * 0.5
        b['y'] = -symbol_asc*0.9 + b['descent']
        
        ascent = symbol_asc - b['descent'] + b['ascent']
        descent = symbol['descent'] + a['descent'] - a['ascent']
        
        return [symbol, a, b], width, ascent, descent

members = [Bounded, Symbol, Bound]
