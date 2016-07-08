from math import ceil
from cairo import ImageSurface, FORMAT_ARGB32, Context

class Vector_cache(dict):
    def __init__(self, paint_function, h, k, frameshift=(0, 0), radius=0):
        self._h  = abs(h)
        self._k  = abs(k)
        self._uh = self._h*(frameshift[0]+radius)
        self._uk = self._k*(frameshift[1]+radius)
        self._r  = radius
        self._paint_function = paint_function
        dict.__init__(self)
    
    def __missing__(self, zoom):
        zoomfac    = (1 + 2*self._r)*zoom
        self[zoom] = SVGC = ImageSurface(FORMAT_ARGB32, ceil(zoomfac*self._h), ceil(zoomfac*self._k))
        sccr = Context(SVGC)
        sccr.scale(zoom, zoom)
        sccr.translate(self._uh, self._uk)
        self._paint_function(sccr)
        return SVGC
    
    def paint(self, cr, zoom):
        if zoom:
            cr.save()
            inv_zoom = 1/zoom
            cr.scale(inv_zoom, inv_zoom)
            cr.translate(-self._uh*zoom, -self._uk*zoom)
            
            # performs grid snapping
            ax, ay = cr.user_to_device(0, 0)
            cr.translate( * cr.device_to_user(round(ax), round(ay)) )
            
            cr.set_source_surface(self[zoom])
            cr.paint()
            cr.restore()
        else:
            self._paint_function(cr)
