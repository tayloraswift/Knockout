from layout.line import cast_mono_line, calculate_vmetrics
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

    def _mono(self, LINE, PP, F):
        F_small = F + self['cl_bound']
        symbol = cast_mono_line(LINE, self._symbol.content, 13, PP, F + self['cl_symbol'])
        a = cast_mono_line(LINE, self._a.content, 13, PP, F_small)
        b = cast_mono_line(LINE, self._b.content, 13, PP, F_small)
        return symbol, a, b
        
    def _cast_inline_inline(self, LINE, x, y, PP, F, FSTYLE):
        symbol, a, b = self._mono(LINE, PP, F)
        
        symbol['x'] = x
        symbol['y'] = y
        
        symbol_asc, symbol_desc = calculate_vmetrics(symbol)
        symbol_fontsize = symbol['fstyle']['fontsize']
        symbol_asc -= symbol_fontsize * 0.1
        a_asc, a_desc = calculate_vmetrics(a)
        b_asc, b_desc = calculate_vmetrics(b)
        
        a['x'] = x + symbol['advance']
        a['y'] = y - symbol_desc
        
        b['x'] = x + symbol['advance'] + symbol_fontsize*0.1
        b['y'] = y - symbol_asc - b['fstyle']['fontsize']*0.1 + b['fstyle'].vmetrics()[0] #only align to unexpanded metrics
               
        width = max(a['advance'] + a['x'], b['advance'] + b['x']) - symbol['x']
        
        ascent = y - b['y'] + b_asc
        descent = y - a['y'] + a_desc
        
        return [symbol, a, b], width, ascent, descent

    def _cast_inline_display(self, LINE, x, y, PP, F, FSTYLE):
        symbol, a, b = self._mono(LINE, PP, F)
        
        width = max(a['advance'], b['advance'], symbol['advance'])

        symbol['x'] = x + (width - symbol['advance']) / 2
        symbol['y'] = y

        symbol_asc, symbol_desc = calculate_vmetrics(symbol)
        symbol_asc -= symbol['fstyle']['fontsize'] * 0.1
        a_asc, a_desc = calculate_vmetrics(a)
        b_asc, b_desc = calculate_vmetrics(b)
        
        a['x'] = x + (width - a['advance']) / 2
        a['y'] = y - symbol_desc + a_asc
        
        b['x'] = x + (width - b['advance']) / 2
        b['y'] = y - symbol_asc + b_desc
        
        ascent = symbol_asc - b_desc + b_asc
        descent = symbol_desc + a_desc - a_asc
        
        return [symbol, a, b], width, ascent, descent

members = [Bounded, Symbol, Bound]
