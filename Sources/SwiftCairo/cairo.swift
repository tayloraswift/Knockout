import Cairo
import Taylor
import Geometry//.Size

private 
let pixel_format    = CAIRO_FORMAT_RGB24

public 
func make_cairo_canvases(_ pixels:inout [PixelChannel8], _ size:Size)
-> (surface:Cairo_surface, cr:Cairo_context) {
    let surface = Cairo_surface(cairo_image_surface_create_for_data(
                      &pixels, 
                      pixel_format, 
                      size.h, 
                      size.k,
                      cairo_format_stride_for_width(pixel_format, size.h)))
    
    return (surface, surface.create())
}

public 
class Cairo_surface
{
    private
    let surface:OpaquePointer
    
    init(_ csurface:OpaquePointer)
    {
        surface = csurface
    }
    
    public final
    func create() -> Cairo_context 
    {
        return Cairo_context(cairo_create(surface))
    }
    
    deinit
    {
        cairo_surface_destroy(surface)
    }
}

public
class Cairo_context
{
    private
    let cr:OpaquePointer
    
    init(_ ccr:OpaquePointer)
    {
        cr = ccr
    }
    
    public final 
    func move_to(_ x:Double, _ y:Double)
    {
        cairo_move_to(cr, x, y)
    }
    
    public final
    func arc(x:Double, y:Double, r:Double, start:Double = 0, end:Double = 2*π)
    {
        cairo_arc(cr, x, y, r, start, end)
    }
    
    public final 
    func set_source_rgb(_ r:Double, _ g:Double, _ b:Double)
    {
        cairo_set_source_rgb(cr, r, g, b)
    }
    
    public final 
    func set_source_rgba(_ r:Double, _ g:Double, _ b:Double, _ a:Double = 1)
    {
        cairo_set_source_rgba(cr, r, g, b, a)
    }
    
    public final 
    func fill()
    {
        cairo_fill(cr)
    }
    
    public final 
    func paint()
    {
        cairo_paint(cr)
    }
    
    public final 
    func select_font_face(fontname:String, slant:cairo_font_slant_t, weight:cairo_font_weight_t)
    {
        cairo_select_font_face(cr, fontname, slant, weight)
    }
    
    public final 
    func set_font_size(_ size:Double)
    {
        cairo_set_font_size(cr, size)
    }
    
    public final 
    func show_text(_ text:String)
    {
        cairo_show_text(cr, text)
    }
    
    deinit
    {
        cairo_destroy(cr)
    }
}
