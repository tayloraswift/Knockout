from cairo import ImageSurface, SVGSurface, Context, FORMAT_ARGB32
from urllib.error import URLError

from elements.elements import Inline_SE_element
from model.olivia import Inline
from IO.svg import render_SVG

_namespace = 'image'

class Image(Inline_SE_element):
    namespace = _namespace
    tags = {}
    DNA = {}
    
    ADNA = {_namespace: [('src', '', 'str'), ('width', 89, 'int')]}
    documentation = [(0, _namespace)]
    
    def _load(self, A):
        self._tree = A
        
        self.src, self.width = self._get_attributes(_namespace)
        
        self._surface_cache = None
        if self.src[-4:] == '.svg':
            try:
                self._CSVG = render_SVG(self.src)
                self.h = int(self._CSVG.h)
                self.k = int(self._CSVG.k)
                self.render_image = self.paint_SVG
            except URLError:
                self.h = 89
                self.k = 0
                self.render_image = self.paint_Error
        else:
            self.render_image = self.paint_PNG
            self._surface_cache = ImageSurface.create_from_png(self.src)
            self.h = int(self._surface_cache.get_width())
            self.k = int(self._surface_cache.get_height())
            
        self.factor = self.width / self.h

    def paint_SVG(self, cr, render=False):
        cr.scale(self.factor, self.factor)
        if render:
            self._CSVG.paint_SVG(cr)
            return
        elif self._surface_cache is None:
            SC = ImageSurface(FORMAT_ARGB32, self.h, self.k)
            sccr = Context(SC)
            self._CSVG.paint_SVG(sccr)
            self._surface_cache = SC

        cr.set_source_surface(self._surface_cache)
        cr.paint()
    
    def paint_PNG(self, cr, render):
        cr.scale(self.factor, self.factor)
        cr.set_source_surface(self._surface_cache)
        cr.paint()
    
    def paint_Error(self, cr, render):
        cr.set_source_rgba(1, 0, 0.1, 0.7)
        cr.rectangle(0, 0, 2 + self.width*0.1, 2)
        cr.rectangle(0, 2, 2, self.v*0.1)
        
        cr.rectangle(0, self.v, 2 + self.width*0.1, -2)
        cr.rectangle(0, self.v, 2, -self.v*0.1)

        cr.rectangle(self.width, self.v, -2 - self.width*0.1, -2)
        cr.rectangle(self.width, self.v, -2, -self.v*0.1)

        cr.rectangle(self.width, 0, -2 - self.width*0.1, 2)
        cr.rectangle(self.width, 0, -2, self.v*0.1)
        
        cr.show_text('Image not found')
        cr.fill()
    
    def cast_inline(self, x, y, leading, PP, F, FSTYLE):
        glyphwidth = self.width
        self.v = leading
        return _MInline(glyphwidth, leading, self.k * self.factor - leading, self.render_image)

    def __len__(self):
        return 7

class _MInline(Inline):
    def __init__(self, width, A, D, draw):
        Inline.__init__(self, None, width, A, D)
        self._draw = draw
    
    def deposit_glyphs(self, repository, x, y):
        repository['_images'].append((self._draw, x, y - self.ascent))
