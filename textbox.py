import text_t as comp
import bisect

ui_font = comp.TypeClass('/home/kelvin/.fonts/NeueFrutiger45.otf', 13.5)

class Blank_Space(object):
    def __init__(self, default, x, y):
        # must be list
        self._text = default + [None]
        self.x = x
        self.y = y
        
        self._i = len(self._text) - 1
        self._j = self._i
        
        self._stamp_glyphs()
    
    def _stamp_glyphs(self):
        self._glyphs = []
        x = self.x
        for character in self._text:
            try:
                self._glyphs.append((ui_font.character_index(character), x, self.y))
                x += ui_font.glyph_width(character)
            except TypeError:
                self._glyphs.append((None, x, self.y))
#                x += ui_font.fontsize
        
#        return self._glyphs
    
    def translate(self, dx):
        self.x += dx
        self._glyphs[:] = [(g[0], g[1] + dx, g[2]) for g in self._glyphs]
        
    def replace_text(self, text):
        self._text = text + [None]
        self._stamp_glyphs()
    
    def insert(self, segment):
        self._text[self._i:self._j] = segment
        self._stamp_glyphs()
    
    def _target(self, x):
        return bisect.bisect([g[1] for g in self._glyphs], x)
    
    def press(self, x):
        self._i = self._target(x)
        self._j = self._i
    
    def move(self, x):
        self._j = self._target(x)
    
    def draw(self, cr, active=False):
        cr.set_font_size(ui_font.fontsize)
        cr.set_font_face(ui_font.font)
        if active:
            cr.set_source_rgba(0, 0, 0, 0.8)
        else:
            cr.set_source_rgba(0, 0, 0, 1)
        # don't print the cap glyph
        cr.show_glyphs(self._glyphs[:-1])
        if active:
            # print cursors
            cr.set_source_rgb(1, 0.2, 0.6)
            cr.rectangle(round(self._glyphs[self._i][1] - 1), 
                        self.y - ui_font.fontsize, 
                        2, 
                        ui_font.fontsize)
            cr.rectangle(round(self._glyphs[self._j][1] - 1), 
                        self.y - ui_font.fontsize, 
                        2, 
                        ui_font.fontsize)
            cr.fill()
            
    def entry(self):
        return ''.join(self._text[:-1])
