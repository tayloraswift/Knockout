from gi.repository import Gtk, Gdk, GObject
import cairo
import freetype
import _pickle as pickle

from text_t import character
import taylor
import ui
import tree
import kevin
import meredith
import errors
import pycairo_font

import gc



class MouseButtons:
    
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3
    
    
class Display(Gtk.Window):

    def __init__(self):
        super(Display, self).__init__()
        
        self.init_ui()
        
    def init_ui(self):    

        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.on_draw)
        self.darea.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_HINT_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
#        self.darea.set_events(Gdk.EventMask.BUTTON_RELEASE_MASK) 
        self.add(self.darea)
        
        # states
        self.down = False
        self.mode = 'text'
        
        self.uifont = pycairo_font.create_cairo_font_face_for_file('/home/kelvin/.fonts/NeueFrutiger45.otf')
        self.errorpanel = None
        
        self.darea.connect("button-press-event", self.on_button_press)
        self.darea.connect("button-release-event", self.on_button_release)
        self.darea.connect("motion_notify_event", self.motion_notify_event)
        self.connect("key-press-event", self.on_key_press)
        
        self.set_title("Lines")
        self.resize(1000, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()
        
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
#        self.clipboard_item = None
        
        self.x = 0
        self.y = 0
    
#    def format_for_clipboard(self, clipboard, selectiondata, info, data=None):
#        if selectiondata.get_target() == "UTF8_STRING":
#            self.clipboard.set_text(self.clipboard_item.text)
#       if selectiondata.get_target() == "Local":
#            data = pickle.dumps(self.clipboard_item)
#            self.clipboard.set_text(data)

    def on_draw(self, wid, cr):
#        print('draw')
        taylor.draw_text(cr)
        taylor.draw_annotations(cr)
        

        if self.mode == 'channels':

            taylor.draw_railings(cr, self.x, self.y)
            taylor.draw_channels(cr, self.x, self.y, highlight=True, radius=5)
        elif self.mode == 'text':
            taylor.draw_cursors(cr)
            taylor.draw_channels(cr, self.x, self.y)

        # DRAW UI
        h, k = self.get_size()
        cr.rectangle(100, 0, 
                2, 
                k)
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.fill()
        
        cr.set_font_size(14)
        cr.set_font_face(self.uifont)
        
        if self.errorpanel is not None:
            self.errorpanel.draw(cr, h)
        
        tree.controls.draw(cr)

        
    def transition_errorpanel(self):

        self.darea.queue_draw()
        self.errorpanel.increment()
        if self.errorpanel.phase >= 20:
            return False
        return True
    def on_button_press(self, w, e):
        
        if e.type == Gdk.EventType.BUTTON_PRESS \
            and e.button == MouseButtons.LEFT_BUTTON:
            self.mode = tree.take_event(e.x, e.y, 'press')

            self.darea.queue_draw()
            self.down = True
            
            
    def on_button_release(self, w, e):

        if e.type == Gdk.EventType.BUTTON_RELEASE \
            and e.button == MouseButtons.LEFT_BUTTON:
            self.down = False
            self.mode = tree.take_event(e.x, e.y, 'release')
            self.darea.queue_draw()


    def motion_notify_event(self, widget, event):
#        if event.is_hint:
#            state, self.x, self.y, f = event.window.get_pointer()

        self.x = event.x
        self.y = event.y
#            state = event.state

        if Gdk.ModifierType.BUTTON1_MASK and self.down:
            self.mode = tree.take_event(self.x, self.y, 'press_motion')
        else:
            self.mode = tree.take_event(self.x, self.y, 'motion')
        self.darea.queue_draw()

    
    def on_key_press(self, w, e):
        
        print (Gdk.keyval_name(e.keyval))

        name = Gdk.keyval_name(e.keyval)
        
        if e.state & Gdk.ModifierType.SHIFT_MASK and name == 'Return':
            self.mode = tree.take_event(0, 0, 'paragraph', key=True)
            
                
        elif e.state & Gdk.ModifierType.CONTROL_MASK:
            
            if name == 'v':
                meredith.mere.tracts[meredith.mere.t].insert(kevin.deserialize(self.clipboard.wait_for_text()))

            elif name in ['c', 'x'] and meredith.mere.tracts[meredith.mere.t].take_selection():
                self.clipboard.set_text(kevin.serialize(meredith.mere.tracts[meredith.mere.t].take_selection()), -1)

                if name == 'x':
                    meredith.mere.tracts[meredith.mere.t].delete( * meredith.mere.selection())
        
        
        elif name in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Caps_Lock', 'Escape', 'Tab', 'Alt_L', 'Alt_R', 'Super_L', 'Multi_key']:
            pass
        
        else:
            self.mode = tree.take_event(0, 0, name, key=True, value=e.keyval)
        self.darea.queue_draw()
        
        #draw errors
        if errors.styleerrors.new_error():
            
            if errors.styleerrors.first != ():
                self.errorpanel = ui.ErrorPanel(1)
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


