import cairo

from meredith.box import Box

class FontRendering(Box):
    DNA = [('hinting', 'int', 0), ('antialias', 'int', 0)]
    
    def after(self, A):
        self.fontoptions.set_hint_style(self['hinting'])
        self.fontoptions.set_antialias(self['antialias'])

FO = cairo.FontOptions()

fontsettings = FontRendering({'hinting': FO.get_hint_style(), 'antialias': FO.get_antialias()})
fontsettings.fontoptions = FO
