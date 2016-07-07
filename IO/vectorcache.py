from cairo import SVGSurface, Context

class Vector_cache(dict):
    def __init__(self, paint_function, h, k):
        self._h = abs(int(h))
        self._k = abs(int(k))
        self._paint_function = paint_function
        dict.__init__(self)
    
    def __missing__(self, zoom):
        self[zoom] = SVGC = SVGSurface(None, 3*self._h*zoom, 3*self._k*zoom)
        sccr = Context(SVGC)
        sccr.scale(zoom, zoom)
        sccr.translate(self._h, 2*self._k)
        self._paint_function(sccr)
        return SVGC
    
    def paint(self, cr, zoom):
        if zoom:
            cr.save()
            inv_zoom = 1/zoom
            cr.scale(inv_zoom, inv_zoom)
            cr.translate(-self._h*zoom, -2*self._k*zoom)
            cr.set_source_surface(self[zoom])
            cr.paint()
            cr.restore()
        else:
            self._paint_function(cr)
