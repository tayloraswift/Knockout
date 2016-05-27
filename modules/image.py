from cairo import ImageSurface, SVGSurface, Context, FORMAT_ARGB32
from urllib.error import URLError

from meredith.box import Inline
from IO.bitmap import make_pixbuf, paint_pixbuf

from fonts.interfacefonts import ISTYLES

_fail = '\033[91m'
_endc = '\033[0m'
_bold = '\033[1m'

# cairo svg may not have all needed libraries
try:
    from IO.svg import render_SVG
except ImportError as message:
    print(_fail + _bold + 'ERROR: ' + _endc + _fail + str(message) + ', SVG image display has been disabled.' + _endc)
    render_SVG = None

def _paint_fail_frame(cr, h, k, msg):
    cr.set_font_size(10)
    cr.set_font_face(ISTYLES[('strong',)]['font'])
    
    cr.set_source_rgba(1, 0, 0.1, 0.7)
    cr.rectangle(0, 0, 2 + h*0.1, 2)
    cr.rectangle(0, 2, 2, k*0.1)
    
    cr.rectangle(0, k, 2 + h*0.1, -2)
    cr.rectangle(0, k, 2, -k*0.1)

    cr.rectangle(h, k, -2 - h*0.1, -2)
    cr.rectangle(h, k, -2, -k*0.1)

    cr.rectangle(h, 0, -2 - h*0.1, 2)
    cr.rectangle(h, 0, -2, k*0.1)
    
    cr.move_to(6, 13)
    cr.show_text(msg)
    cr.fill()
        
class Image(Inline):
    name = 'image'
    DNA = [('src', 'str', ''), ('width', 'int', 89), ('resolution', 'int', 0)]
    
    def _load(self):
        self.width = self['width']
        
        self._surface_cache = None
        A, B = self._load_image_file(self['src'])
        if A:
            self.render_image = B
        else:
            self.h = 89
            self.k = 0
            self._msg = B
            self.render_image = self.paint_Error
            
        self.factor = self.width / self.h

    def _load_image_file(self, src):
        success = False
        if src[-4:] == '.svg':
            if render_SVG is not None:
                try:
                    self._CSVG = render_SVG(src)
                    self.h = int(self._CSVG.h)
                    self.k = int(self._CSVG.k)
                    renderfunc = self.paint_SVG
                    success = True
                except URLError:
                    renderfunc = 'SVG not found'
            else:
                renderfunc = 'CairoSVG not available'
        else:
            try:
                self._surface_cache = make_pixbuf(src, self['resolution'])
                renderfunc = self.paint_PNG
                self.h = int(self._surface_cache.get_width())
                self.k = int(self._surface_cache.get_height())
                success = True
            except SystemError:
                renderfunc = 'Image not found'
        return success, renderfunc
        
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
    
    def paint_PNG(self, cr, render=False):
        cr.scale(self.factor, self.factor)
        paint_pixbuf(cr, self._surface_cache)
    
    def paint_Error(self, cr, render=False):
        _paint_fail_frame(cr, self.width, self.v, self._msg)
    
    def _cast_inline(self, LINE, x, y, PP, F, FSTYLE):
        self.v = LINE['leading']
        self._I = (self.render_image, x, y - LINE['leading'])
        return [], self.width, LINE['leading'], self.k * self.factor - LINE['leading']

    def deposit_glyphs(self, repository, x, y):
        repository['_images'].append((self._I[0], self._I[1] + x, self._I[2] + y))

members = [Image]
