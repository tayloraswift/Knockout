from gi.repository import Gtk, Gdk, GObject
import cairo

from state import noticeboard
from state import constants

from model import kevin, meredith
from model import errors
from model import do

from typing import compose

from interface import karlie
from interface import taylor
from interface import menu

import tree

_dead_keys = set(('dead_tilde', 'dead_acute', 'dead_grave', 'dead_circumflex', 'dead_abovering', 'dead_macron', 'dead_breve', 'dead_abovedot', 'dead_diaeresis', 'dead_doubleacute', 'dead_caron', 'dead_cedilla', 'dead_ogonek', 'dead_iota', 'Multi_key'))
_special_keys = set(('Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Caps_Lock', 'Escape', 'Tab', 'Alt_L', 'Alt_R', 'Super_L')) | _dead_keys

class MouseButtons:
    
    LEFT_BUTTON = 1
    MIDDLE_BUTTON = 2
    RIGHT_BUTTON = 3
    
class Display(Gtk.Window):

    def __init__(self):
        super(Display, self).__init__()
        
        self.init_ui()
        
    def init_ui(self):    
        self._h = constants.window.get_h()
        self._k = constants.window.get_k()
        
        self.SCREEN = Gtk.DrawingArea()
        self.SCREEN.connect("draw", self.on_draw)
        self.SCREEN.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.SCROLL_MASK)
        
        self.BECKY = Gtk.DrawingArea()
        self.BECKY.connect("draw", self.DRAW_BECKY)

        self.KLOSSY = Gtk.DrawingArea()
        self.KLOSSY.connect("draw", self.DRAW_KLOSSY)
        self.KLOSSY.set_size_request(self._h - constants.UI[1], 0)
        
        box = Gtk.Box()
        
        box.pack_start(self.BECKY, True, True, 0)
        box.pack_start(self.KLOSSY, False, False, 0)    
        
        overlay = Gtk.Overlay()
        overlay.add_overlay(box)
        overlay.add_overlay(self.SCREEN)

        self.add(overlay)

        self.errorpanel = None
        
        self._compose = False
        
        self.SCREEN.connect("button-press-event", self.on_button_press)
        self.SCREEN.connect("button-release-event", self.on_button_release)
        self.SCREEN.connect("scroll-event", self.on_scroll)
        self.SCREEN.connect("motion_notify_event", self.motion_notify_event)
        self.connect("key-press-event", self.on_key_press)
        self.connect("check-resize", self.on_resize)
        
        self.set_title(constants.filename)

        self.resize(self._h, self._k)
        
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", self.quit)
        self.show_all()
        
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self._HINTS = constants.HINTS

        self._c_ = 0
        
        self._periodic = GObject.timeout_add(2000, self._on_periodic)
    
    def _on_periodic(self):
        meredith.mipsy.stats(spell=True)
        self.BECKY.queue_draw()
        self.KLOSSY.queue_draw()
        self.SCREEN.queue_draw()
        return True

    def DRAW_BECKY(self, w, cr):
        cr.set_font_options(self._HINTS)
        taylor.becky.render(cr, self._h, self._k)

        if self.errorpanel is not None:
            self.errorpanel.draw(cr, constants.UI[1])

        print('BECKY: ' + str(self._c_))
        self._c_ += 1

    def DRAW_KLOSSY(self, w, cr):
        cr.set_font_options(self._HINTS)
        
        karlie.klossy.render(cr, self._h, self._k)

        print('KLOSSY: ' + str(self._c_))
        self._c_ += 1
        
    def on_draw(self, wid, cr):
        menu.menu.render(cr)

    def _draw_errors(self):
        if errors.styleerrors.new_error():
            
            if errors.styleerrors.first != ():
                self.errorpanel = errors.ErrorPanel(1)
                self.errorpanel.update_message('Undefined class', ', '.join(errors.styleerrors.first[0]), ', '.join([str(e + 1) for e in errors.styleerrors.first[1]]))
                GObject.timeout_add(4, self.transition_errorpanel)
            else:
                self.errorpanel = None
    
    def transition_errorpanel(self):

        self.BECKY.queue_draw()

        self.errorpanel.increment()
        if self.errorpanel.phase >= 20:
            return False
        return True
    
    def on_resize(self, w):
        h_old = self._h
        self._h, self._k = self.get_size()
        constants.UI[1] += self._h - h_old
        
        constants.window.resize(self._h, self._k)
    
        taylor.becky.resize(self._h, self._k)
        
    def on_button_press(self, w, e):

        if e.type == Gdk.EventType._2BUTTON_PRESS:
            if e.button == MouseButtons.LEFT_BUTTON:
                print('double')
                tree.take_event(e.x, e.y, 'press2' )
        
        elif e.type == Gdk.EventType.BUTTON_PRESS:
            if e.button == MouseButtons.LEFT_BUTTON:
                if e.state & Gdk.ModifierType.CONTROL_MASK:
                    mod = 'ctrl'
                else:
                    mod = None
                tree.take_event(e.x, e.y, 'press', char=mod )
            
            elif e.button == MouseButtons.MIDDLE_BUTTON:
                tree.take_event(e.x, e.y, 'press_mid' )
            
            elif e.button == MouseButtons.RIGHT_BUTTON:
                tree.take_event(e.x, e.y, 'press_right' )
            
        self.BECKY.queue_draw()
        self.KLOSSY.queue_draw()
        self.SCREEN.queue_draw()
            
    def on_button_release(self, w, e):
        if e.button == MouseButtons.LEFT_BUTTON:

            tree.take_event(e.x, e.y, 'release' )
        
        elif e.button == MouseButtons.MIDDLE_BUTTON:
            tree.take_event(-1, -1, 'drag' )
            
        self.BECKY.queue_draw()
        self.KLOSSY.queue_draw()
        self.SCREEN.queue_draw()
        
        self._draw_errors()

    def motion_notify_event(self, widget, event):

        if event.state & Gdk.ModifierType.BUTTON1_MASK:
            tree.take_event(event.x, event.y, 'press_motion' )

        elif event.state & Gdk.ModifierType.BUTTON2_MASK:
            tree.take_event(event.x, event.y, 'drag' )
            
        else:
            tree.take_event(event.x, event.y, 'motion' )

        if noticeboard.redraw_overlay.should_refresh():
            self.SCREEN.queue_draw()
        if noticeboard.redraw_klossy.should_refresh():
            self.KLOSSY.queue_draw()
        if noticeboard.redraw_becky.should_refresh():
            self.BECKY.queue_draw()
            
    def on_scroll(self, w, e):
        if e.state & Gdk.ModifierType.CONTROL_MASK:
            mod = 'ctrl'
        else:
            mod = None

        # direction of scrolling stored as sign
        if e.direction == 1:
            tree.take_event(e.x, e.y, 'scroll', char=mod )
        elif e.direction == 0:
            tree.take_event(e.x, -e.y, 'scroll', char=mod )
        
        if noticeboard.redraw_overlay.should_refresh():
            self.SCREEN.queue_draw()
        if noticeboard.redraw_klossy.should_refresh():
            self.KLOSSY.queue_draw()
        if noticeboard.redraw_becky.should_refresh():
            self.BECKY.queue_draw()

        
    def on_key_press(self, w, e):

        name = Gdk.keyval_name(e.keyval)
        
        if e.state & Gdk.ModifierType.SHIFT_MASK and name == 'Return':
            tree.take_event(0, 0, 'paragraph', key=True)
                
        elif e.state & Gdk.ModifierType.CONTROL_MASK:
            
            if name == 'z':
                do.undo()
            elif name == 'y':
                do.redo()
            
            elif name == 'v':
                tree.take_event(0, 0, 'Paste', key=True, char = kevin.deserialize(self.clipboard.wait_for_text()) )

            elif name in ['c', 'x']:
                if name == 'c':
                    cp = tree.take_event(0, 0, 'Copy', key=True)
                else:
                    cp = tree.take_event(0, 0, 'Cut', key=True)
                    
                if cp is not None:
                    self.clipboard.set_text(kevin.serialize(cp), -1)
            
            elif name == 'a':
                tree.take_event(0, 0, 'All', key=True)

            elif name == 'i':
                tree.take_event(0, 0, 'Ctrl_I', key=True)
            
            elif name == 'b':
                tree.take_event(0, 0, 'Ctrl_B', key=True)

            elif name == 'I':
                tree.take_event(0, 0, 'Ctrl_Shift_I', key=True)
            
            elif name == 'B':
                tree.take_event(0, 0, 'Ctrl_Shift_B', key=True)
        
        elif name in _special_keys:

            if name in _dead_keys:
                self._compose = True
                # build compositor
                self._compositor = compose.Composition(name)
        
        elif self._compose:
            composite = self._compositor.key_input(name, chr(Gdk.keyval_to_unicode(e.keyval)))
            if composite:
                # destroy compositor
                del self._compositor
                self._compose = False
                tree.take_event(0, 0, composite[0], key=True, char = composite[1])
                
        else:
            tree.take_event(0, 0, name, key=True, char = chr(Gdk.keyval_to_unicode(e.keyval)) )
        
        self.BECKY.queue_draw()
        self.KLOSSY.queue_draw()
        self.SCREEN.queue_draw()
        
        self._draw_errors()

    def quit(self, w, e):
        GObject.source_remove(self._periodic)
        Gtk.main_quit()
        
def main():
    
    app = Display()
    Gtk.main()



