from cairo import ImageSurface, Context, FORMAT_ARGB32

from model.cat import cast_mono_line, calculate_vmetrics
from elements.elements import Inline_SE_element
from model.olivia import Inline
from edit.paperairplanes import interpret_int
from IO.svg import render_SVG

_namespace = 'image'

class RImage(Inline_SE_element):
    namespace = _namespace
    tags = {}
    DNA = {}
    
    def _load(self, A):
        self._tree = A
        
        self.src = A[0][1].get('src', '')
        self.width = interpret_int(A[0][1].get('width', 89))

        if self.src[-4:] == '.svg':
            self._CSVG = render_SVG(url=self.src)
            self.h = int(self._CSVG.context_width)
            self.k = int(self._CSVG.context_height)
            self.render_image = self.paint_SVG
            self._surface_cache = None
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
    
    def cast_inline(self, x, y, leading, PP, F, FSTYLE):
        glyphwidth = self.width

        return _MInline(glyphwidth, leading, self.k * self.factor - leading, self.render_image)

    def __len__(self):
        return 7

class _MInline(Inline):
    def __init__(self, width, A, D, draw):
        Inline.__init__(self, None, width, A, D)
        self._draw = draw
    
    def deposit_glyphs(self, repository, x, y):
        repository['_images'].append((self._draw, x, y - self.ascent))
