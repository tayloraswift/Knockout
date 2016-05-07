import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk, GdkPixbuf
from gi.repository.GLib import Error as GLibError

def make_pixbuf(src, size=0):
    try:
        if size:
            return GdkPixbuf.Pixbuf.new_from_file_at_size(src, size, 198900)
        else:
            return GdkPixbuf.Pixbuf.new_from_file(src)
    except GLibError:
        raise SystemError

def paint_pixbuf(cr, pb):
    Gdk.cairo_set_source_pixbuf(cr, pb, 0, 0)
    cr.paint()
