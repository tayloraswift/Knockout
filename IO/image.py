from cairo import ImageSurface, SVGSurface, Context, FORMAT_ARGB32
from urllib.error import URLError

import fonts

from IO.bitmap import make_pixbuf, paint_pixbuf

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
    cr.set_font_face(fonts.interfacefonts.ISTYLES[('strong',)]['font'])
    
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

class _Image_painter(object):
    def inflate(self, width, leading):
        self._leading = leading
        self._factor = width / self.h
        self.width = width
        self.height = self.k*self._factor
    
    def paint_Error(self, cr, render=False):
        _paint_fail_frame(cr, self.width, self._leading, self._msg)

def make_image_surface(h, k):
    return ImageSurface(FORMAT_ARGB32, h, k)

class SVG_image(_Image_painter):
    def __init__(self, ** kwargs ):
        self._factor = 1
        self._shift = kwargs.get('dx', 0), kwargs.get('dy', 0)
        if render_SVG is not None:
            try:
                self._CSVG = render_SVG( ** kwargs )
                self.h = int(self._CSVG.h * kwargs.get('hfactor', 1))
                self.k = int(self._CSVG.k * kwargs.get('kfactor', 1))
                self._surface_cache = self.generate_SC(self._CSVG)            
                self.paint = self.paint_SVG
                return
            except URLError:
                self._msg = 'SVG not found'
        else:
            self._msg = 'CairoSVG not available'
        self.h = 89 * kwargs.get('hfactor', 1)
        self.k = 0
        self.paint = self.paint_Error
    
    def generate_SC(self, CSVG):
        SC = make_image_surface(self.h, self.k)
        sccr = Context(SC)
        sccr.save()
        sccr.translate( * self._shift )
        CSVG.paint_SVG(sccr)
        sccr.restore()
        return SC

    def paint_SVG(self, cr, render=False):
        cr.save()
        cr.scale(self._factor, self._factor)
        if render:
            cr.translate( * self._shift )
            self._CSVG.paint_SVG(cr)
        else:
            cr.set_source_surface(self._surface_cache)
            cr.paint()
        cr.restore()

class Bitmap_image(_Image_painter):
    def __init__(self, url, resolution):
        self._factor = 1
        try:
            self._surface_cache = make_pixbuf(url, resolution)
            self.paint = self.paint_PNG
            self.h = int(self._surface_cache.get_width())
            self.k = int(self._surface_cache.get_height())
        except SystemError:
            self._msg = 'Image not found'
            self.h = 89
            self.k = 0
            self.paint = self.paint_Error

    def paint_PNG(self, cr, render=False):
        cr.save()
        cr.scale(self._factor, self._factor)
        paint_pixbuf(cr, self._surface_cache)
        cr.restore()
