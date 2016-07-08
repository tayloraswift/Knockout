from urllib.error import URLError

import fonts

from IO.bitmap import make_pixbuf, paint_pixbuf
from IO.vectorcache import Vector_cache

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
    def inflate(self, leading):
        self._leading = leading
    
    def _set_dimensions(self, h, k, source_h, source_k, scale):
        self.width  = h
        factor = h/source_h
        if k is None:
            self.height = source_k*factor
        else:
            self.height = k
        if scale is None:
            scale = factor
        return scale
    
    def paint_Error(self, cr, render=False):
        _paint_fail_frame(cr, self.width, self._leading, self._msg)

class SVG_image(_Image_painter):
    def __init__(self, src=None, bytestring=None, h=89, k=None, dx=0, dy=0, scale=None):
        if render_SVG is not None:
            try:
                CSVG  = render_SVG(src, bytestring)
                scale = self._set_dimensions(h, k, CSVG.h, CSVG.k, scale)
                def paint_function(cr):
                    cr.scale(scale, scale)
                    cr.translate(dx, dy)
                    CSVG.paint_SVG(cr)
                
                self.paint = Vector_cache(paint_function, self.width, self.height).paint
                return
            except URLError:
                self._msg = 'SVG not found'
        else:
            self._msg = 'CairoSVG not available'
            
        self._set_dimensions(h, k, h, 0, None)
        self.paint = self.paint_Error

class Bitmap_image(_Image_painter):
    def __init__(self, src, h, resolution):
        try:
            self._img_cache = make_pixbuf(src, resolution)
            source_h        = self._img_cache.get_width()
            source_k        = self._img_cache.get_height()
            self.paint = self.paint_PNG
        except SystemError:
            self._msg = 'Image not found'
            source_h = 89
            source_k = 0
            self.paint = self.paint_Error
        self._factor = self._set_dimensions(h, None, source_h, source_k, None)
        
    def paint_PNG(self, cr, render=False):
        cr.save()
        cr.scale(self._factor, self._factor)
        paint_pixbuf(cr, self._img_cache)
        cr.restore()
