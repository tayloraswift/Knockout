import text_t as comp
import bisect

ui_font = comp.TypeClass('/home/kelvin/.fonts/NeueFrutiger45.otf', 13.5)

class Blank_Space(object):
    def __init__(self, default, x, y, callback):
        # must be list
        self._text = default + [None]
        self.x = x
        self.y = y
        
        self._i = len(self._text) - 1
        self._j = self._i
        
        self._active = False
        
        self._callback = callback
        
        self._stamp_glyphs()

    def _entry(self):
        return ''.join(self._text[:-1])
        
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
    
    
    def type_box(self, name, char):
        
        if name in ['BackSpace', 'Delete']:
            # delete selection
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                del self._text[self._i : self._j]
                self._j = self._i
                
            elif name == 'BackSpace':
                if self._i > 0:
                    del self._text[self._i - 1]
                    self._i -= 1
                    self._j -= 1
            else:
                if self._i < len(self._text) - 2:
                    del self._text[self._i]

        elif name == 'Left':
            if self._i > 0:
                self._i -= 1
                self._j = self._i
        elif name == 'Right':
            if self._i < len(self._text) - 1:
                self._i += 1
                self._j = self._i
        elif name == 'Home':
            self._i = 0
            self._j = 0
        elif name == 'End':
            self._i = len(self._text) - 1
            self._j = len(self._text) - 1
        
        elif char is not None:
            # delete selection
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                del self._text[self._i : self._j]
                self._j = self._i
            self._text[self._i:self._i] = [char]
            self._i += 1
            self._j += 1
        
        self._stamp_glyphs()
    
#    def replace_text(self, text):
#        self._text = text + [None]
#        self._stamp_glyphs()
    
#    def insert(self, segment):
#        self._text[self._i:self._j] = segment
#        self._stamp_glyphs()

    
    def _target(self, x):
        return bisect.bisect([g[1] for g in self._glyphs[:-2]], x)

    
    def focus(self, x):
        self._active = True
        self._i = self._target(x)
        self._j = self._i
    
    def focus_drag(self, x):
        self._j = self._target(x)
    
    def defocus(self):
        self._active = False
        # dump entry
        self._callback(self._entry())

    
    def draw(self, cr):
        
        if self._active:
            # print cursors
            cr.set_source_rgb(1, 0.2, 0.6)
            cr.rectangle(round(self._glyphs[self._i][1] - 1), 
                        self.y - round(ui_font.fontsize), 
                        2, 
                        round(ui_font.fontsize))
            cr.rectangle(round(self._glyphs[self._j][1] - 1), 
                        self.y - round(ui_font.fontsize), 
                        2, 
                        round(ui_font.fontsize))
            cr.fill()
            
            # print highlight
            if self._i != self._j:
                cr.set_source_rgba(0, 0, 0, 0.1)
                # find leftmost
                if self._i <= self._j:
                    root = self._glyphs[self._i][1]
                else:
                    root = self._glyphs[self._j][1]
                cr.rectangle(root, 
                        self.y - round(ui_font.fontsize),
                        abs(self._glyphs[self._i][1] - self._glyphs[self._j][1]),
                        round(ui_font.fontsize))
                cr.fill()
                
        cr.set_font_size(ui_font.fontsize)
        cr.set_font_face(ui_font.font)
        if self._active:
            cr.set_source_rgba(0, 0, 0, 1)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        cr.rectangle(self.x, self.y + 5, 250, 1)
        cr.fill()
        # don't print the cap glyph
        cr.show_glyphs(self._glyphs[:-2])
            
