from gi.repository import Gdk, GdkPixbuf

def make_pixbuf(src):
    return GdkPixbuf.Pixbuf.new_from_file(src)

def paint_pixbuf(cr, pb):
    Gdk.cairo_set_source_pixbuf(cr, pb, 0, 0)
    cr.paint()
