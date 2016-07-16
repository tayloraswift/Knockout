import cairo

from IO.tree import Knockout

from meredith.box import Box

interface_kt = Knockout()

class FontRendering(Box):
    DNA = [('hinting', 'int', 0), ('antialias', 'int', 0)]
    
    def after(self, A):
        self.fontoptions.set_hint_style(self['hinting'])
        self.fontoptions.set_antialias(self['antialias'])

FO = cairo.FontOptions()

fontsettings = FontRendering(interface_kt, {'hinting': FO.get_hint_style(), 'antialias': FO.get_antialias()})
fontsettings.fontoptions = FO
