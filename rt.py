from gi.repository import Gtk, Gdk, GObject
import cairo

import sierra

sierra.load()

from state import noticeboard
from state import constants

from model import kevin
from model import errors

from interface import karlie
from interface import taylor
from interface import menu

import tree



class MouseButtons:
    
    LEFT_BUTTON = 1
    MIDDLE_BUTTON = 2
    RIGHT_BUTTON = 3
    
class Display(Gtk.Window):

    def __init__(self):
        super(Display, self).__init__()
        
        self.init_ui()
        
    def init_ui(self):    

        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.on_draw)
        self.darea.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.SCROLL_MASK)
#        self.darea.set_events(Gdk.EventMask.BUTTON_RELEASE_MASK) 
        self.add(self.darea)
        
        self.errorpanel = None
        
        self.darea.connect("button-press-event", self.on_button_press)
        self.darea.connect("button-release-event", self.on_button_release)
        self.darea.connect("scroll-event", self.on_scroll)
        self.darea.connect("motion_notify_event", self.motion_notify_event)
        self.connect("key-press-event", self.on_key_press)
        self.connect("check-resize", self.on_resize)
        
        self.set_title("Lines")
        self.resize(constants.windowwidth, constants.windowheight)
        
        self._h = constants.window.get_h()
        self._k = constants.window.get_k()
        
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()
        
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
#        self.clipboard_item = None

    
        self._c_ = 0
#    def format_for_clipboard(self, clipboard, selectiondata, info, data=None):
#        if selectiondata.get_target() == "UTF8_STRING":
#            self.clipboard.set_text(self.clipboard_item.text)
#       if selectiondata.get_target() == "Local":
#            data = pickle.dumps(self.clipboard_item)
#            self.clipboard.set_text(data)

    def on_draw(self, wid, cr):
        nohints = cairo.FontOptions()
        nohints.set_hint_style(cairo.HINT_STYLE_NONE)
        cr.set_font_options(nohints)

        taylor.becky.render(cr, self._h, self._k)

        karlie.klossy.render(cr, self._h, self._k)
        
        menu.menu.render(cr)

        if self.errorpanel is not None:
            self.errorpanel.draw(cr, self._h - constants.propertieswidth)

        print(self._c_)
        self._c_ += 1
        
    def transition_errorpanel(self):

        self.darea.queue_draw()
        self.errorpanel.increment()
        if self.errorpanel.phase >= 20:
            return False
        return True
    
    def on_resize(self, w):
        self._h, self._k = self.get_size()
        constants.window.resize(self._h, self._k)
        
        karlie.klossy.resize(self._h, self._k)
        taylor.becky.resize(self._h, self._k)
        
    def on_button_press(self, w, e):
        
        if e.type == Gdk.EventType.BUTTON_PRESS:
            if e.button == MouseButtons.LEFT_BUTTON:
                if e.state & Gdk.ModifierType.CONTROL_MASK:
                    mod = 'ctrl'
                else:
                    mod = None
                        
                tree.take_event(e.x, e.y, 'press', char=mod, geometry=self.get_size())
            
            elif e.button == MouseButtons.MIDDLE_BUTTON:
                tree.take_event(e.x, e.y, 'press_mid', geometry=self.get_size())
            
            self.darea.queue_draw()
            
            
    def on_button_release(self, w, e):

        if e.type == Gdk.EventType.BUTTON_RELEASE:
            if e.button == MouseButtons.LEFT_BUTTON:

                tree.take_event(e.x, e.y, 'release', geometry=self.get_size())
            
            elif e.button == MouseButtons.MIDDLE_BUTTON:
                tree.take_event(-1, -1, 'drag', geometry=self.get_size())
                
            self.darea.queue_draw()

    def motion_notify_event(self, widget, event):

        if event.state & Gdk.ModifierType.BUTTON1_MASK:
            tree.take_event(event.x, event.y, 'press_motion', geometry=self.get_size())

        elif event.state & Gdk.ModifierType.BUTTON2_MASK:
            tree.take_event(event.x, event.y, 'drag', geometry=self.get_size())
            noticeboard.refresh.push_change()
        else:
            tree.take_event(event.x, event.y, 'motion', geometry=self.get_size())

        if noticeboard.refresh.should_refresh():
            self.darea.queue_draw()

    def on_scroll(self, w, e):
        if e.state & Gdk.ModifierType.CONTROL_MASK:
            mod = 'ctrl'
        else:
            mod = None
        
        # direction of scrolling stored as sign
        tree.take_event(e.x, e.y*(2*e.direction - 1), 'scroll', char=mod, geometry=self.get_size())
        
        if noticeboard.refresh.should_refresh():
            self.darea.queue_draw()

        
    def on_key_press(self, w, e):
        
#        print (Gdk.keyval_name(e.keyval))

        name = Gdk.keyval_name(e.keyval)
        
        if e.state & Gdk.ModifierType.SHIFT_MASK and name == 'Return':
            tree.take_event(0, 0, 'paragraph', key=True)
            
                
        elif e.state & Gdk.ModifierType.CONTROL_MASK:
            
            if name == 'v':
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
        
        
        elif name in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Caps_Lock', 'Escape', 'Tab', 'Alt_L', 'Alt_R', 'Super_L', 'Multi_key']:
            pass
        
        else:
            tree.take_event(0, 0, name, key=True, char = chr(Gdk.keyval_to_unicode(e.keyval)) )
        self.darea.queue_draw()
        
        #draw errors
        if errors.styleerrors.new_error():
            
            if errors.styleerrors.first != ():
                self.errorpanel = errors.ErrorPanel(1)
                self.errorpanel.update_message('Undefined class', ', '.join(errors.styleerrors.first[0]), ', '.join([str(e + 1) for e in errors.styleerrors.first[1]]))
                GObject.timeout_add(4, self.transition_errorpanel)
            else:
                self.errorpanel = None
        
def main():
    
    app = Display()
    Gtk.main()
#    gc.collect()

    
        
if __name__ == "__main__":    
    main()


