from gi.repository import Gdk, GdkPixbuf

def make_pixbuf(src, size=0):
    if size:
        return GdkPixbuf.Pixbuf.new_from_file_at_size(src, size, 198900)
    else:
        return GdkPixbuf.Pixbuf.new_from_file(src)

def paint_pixbuf(cr, pb):
    Gdk.cairo_set_source_pixbuf(cr, pb, 0, 0)
    cr.paint()
