from bisect import bisect

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject

from state import noticeboard, constants
from IO import do
from edit import cursor
from keyboard import compose
from meredith.smoothing import fontsettings
from interface import karlie, taylor, menu

_dead_keys = set(('dead_tilde', 'dead_acute', 'dead_grave', 'dead_circumflex', 'dead_abovering', 'dead_macron', 'dead_breve', 'dead_abovedot', 'dead_diaeresis', 'dead_doubleacute', 'dead_caron', 'dead_cedilla', 'dead_ogonek', 'dead_iota', 'Multi_key'))
_special_keys = compose.compose_keys | _dead_keys

def strike_menu(event, e):
    if menu.menu.menu():
        if event == 2: # scroll
            if menu.menu.in_bounds(e.x, abs(e.y)):
                menu.menu.scroll(e.direction)
                menu.menu.test_change()
                return False
            
        elif menu.menu.in_bounds(e.x, e.y):
            if event == 1: # motion
                menu.menu.hover(e.y)
                menu.menu.test_change()
            
            elif event == 0: # press
                menu.menu.press(e.y)
            return False
    return True

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
        
        self._REGIONS = [taylor.becky, karlie.klossy]
        self._active = self._REGIONS[0]
        self._active_hover = self._REGIONS[0]
        self._active_pane = None
        self._R = 0
        
        overlay = Gtk.Overlay()
        overlay.add_overlay(box)
        overlay.add_overlay(self.SCREEN)
        self.add(overlay)

        self.errorpanel = None
        
        self._compositor = compose.Compositor()
        
        self.SCREEN.connect("button-press-event", self._press_sort)
        self.SCREEN.connect("button-release-event", self._release_sort)
        self.SCREEN.connect("scroll-event", self._scroll_sort)
        self.SCREEN.connect("motion_notify_event", self._motion_sort)
        self.connect("key-press-event", self.on_key_press)
        self.connect("check-resize", self.on_resize)
        
        self.set_title(constants.filename)

        self.resize(self._h, self._k)
        
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", self.quit)
        self.show_all()
        
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self._FO = fontsettings.fontoptions
        
        self._periodic = GObject.timeout_add(2000, self._on_periodic)
        self._on_periodic()
    
    def _on_periodic(self):
        cursor.fcursor.run_stats(spell=True)
        self.BECKY.queue_draw()
        self.KLOSSY.queue_draw()
        self.SCREEN.queue_draw()
        return True

    def DRAW_BECKY(self, w, cr):
        cr.set_font_options(self._FO)
        cr.set_source_rgb(1, 1, 1)
        cr.paint()
        taylor.becky.render(cr, self._h, self._k)

        if self.errorpanel is not None:
            self.errorpanel.draw(cr, constants.UI[1])

    def DRAW_KLOSSY(self, w, cr):
        cr.set_font_options(self._FO)
        karlie.klossy.render(cr, self._h, self._k)
        
    def on_draw(self, w, cr):
        self._compositor.draw(cr)
        menu.menu.render(cr)
    
    def on_resize(self, w):
        h_old = self._h
        self._h, self._k = self.get_size()
        constants.UI[-1] +=  self._h - h_old
        
        constants.window.resize(self._h, self._k)
        taylor.becky.resize(self._k)
    
    def _internal_resize(self):
        taylor.becky.resize(self._k)
        karlie.klossy.resize()
        self.KLOSSY.set_size_request(karlie.klossy.width, 0)
        self.BECKY.queue_draw()
        self.KLOSSY.queue_draw()

    def _pane(self, x):
        # check for borders
        R = self._R
        UI = constants.UI
        if not R:
            B = ((R + 1, UI[R + 1]),)
        elif R < len(UI) - 1:
            B = ((R, UI[R]), (R + 1, UI[R + 1]))
        else:
            B = ((R, UI[R]),)
        for r, border in B:
            if -10 < x - border < 10:
                self._active_pane = r
                return True
        return False

    def _set_active_hover_region(self, x, y):
        r = bisect(constants.UI, x) - 1
        O = self._REGIONS[r]
        if self._active_hover is not O:
            self._active_hover.hover(-1, -1)
            self._active_hover = O
            self._R = r
        return x - constants.UI[r], y

    def _set_active_region(self, x, y):
        r = bisect(constants.UI, x) - 1
        O = self._REGIONS[r]
        if self._active is not O:
            if isinstance(O, karlie._Properties_panel):
                O.press(-1, -1, None)
            self._active = O
        if self._active_hover is not O:
            self._active_hover.hover(-1, -1)
            self._active_hover = O
        self._R = r
        return x - constants.UI[r], y
    
    def _convert(self, x, y):
        return x - constants.UI[self._R], y
        
    def _press_sort(self, w, e):
        if strike_menu(0, e):
            menu.menu.destroy()
            if self._pane(e.x):
                return
            x, y = self._set_active_region(e.x, e.y)
            
            if e.type == Gdk.EventType._2BUTTON_PRESS:
                if e.button == 1:
                    self._active.dpress()
            
            elif e.type == Gdk.EventType.BUTTON_PRESS:
                if e.button == 1:
                    if e.state & Gdk.ModifierType.CONTROL_MASK:
                        char = 'ctrl'
                    else:
                        char = None
                    self._active.press(x, y, char)
                
                elif e.button == 2:
                    self._active.press_mid(x, y)
                
                elif e.button == 3:
                    self._active.press_right(x, y)
        
        self.BECKY.queue_draw()
        self.KLOSSY.queue_draw()
        self.SCREEN.queue_draw()
        
    def _motion_sort(self, w, e):
        if strike_menu(1, e):
            if e.state & Gdk.ModifierType.BUTTON1_MASK:
                if self._active_pane is None:
                    self._active.press_motion( * self._convert(e.x, e.y))
                else:
                    limits = constants.UI + [self._h]
                    ap = self._active_pane
                    constants.UI[ap] = min(limits[ap + 1] - 175, max(limits[ap - 1] + 175, int(e.x)))
                    self._internal_resize()

            elif e.state & Gdk.ModifierType.BUTTON2_MASK:
                self._active.drag( * self._convert(e.x, e.y))
                
            else:
                self._active_hover.hover( * self._set_active_hover_region(e.x, e.y))

        if noticeboard.redraw_overlay.should_refresh():
            self.SCREEN.queue_draw()
        if noticeboard.redraw_klossy.should_refresh():
            self.KLOSSY.queue_draw()
        if noticeboard.redraw_becky.should_refresh():
            self.BECKY.queue_draw()
        
    def _release_sort(self, w, e):
        self._active_pane = None
        if e.button == 1:
            x, y = self._convert(e.x, e.y)
            self._active.release(x, y)
        
        elif e.button == 2:
            self._active.drag(-1, -1)
            
        self.BECKY.queue_draw()
        self.KLOSSY.queue_draw()
        self.SCREEN.queue_draw()
        
    def _scroll_sort(self, w, e):
        if strike_menu(2, e):
            x, y = self._convert(e.x, e.y)
            
            if e.state & Gdk.ModifierType.CONTROL_MASK:
                char = 'ctrl'
            else:
                char = None

            # direction of scrolling stored as sign
            if e.direction == 1:
                self._active_hover.scroll(x, y, char)
            elif e.direction == 0:
                self._active_hover.scroll(x, -y, char)
        
        if noticeboard.redraw_overlay.should_refresh():
            self.SCREEN.queue_draw()
        if noticeboard.redraw_klossy.should_refresh():
            self.KLOSSY.queue_draw()
        if noticeboard.redraw_becky.should_refresh():
            self.BECKY.queue_draw()

    def on_key_press(self, w, e):

        name = Gdk.keyval_name(e.keyval)
        
        if e.state & Gdk.ModifierType.SHIFT_MASK and name == 'Return':
            self._active.key_input('paragraph', None)
        
        elif e.state & Gdk.ModifierType.CONTROL_MASK:
            if e.state & Gdk.ModifierType.LOCK_MASK and name not in {'Shift_L', 'Shift_R'}:
                self._active.key_input('Ctrl Lock', chr(Gdk.keyval_to_unicode(e.keyval)))
            
            elif name == 'z':
                do.undo()
            elif name == 'y':
                do.redo()
            
            elif name == 'v':
                self._active.key_input('Paste', self.clipboard.wait_for_text())

            elif name in {'c', 'x'}:
                if name == 'c':
                    cp = self._active.key_input('Copy', None)
                else:
                    cp = self._active.key_input('Cut', None)
                    
                if cp is not None: # must be preprocessed into string
                    self.clipboard.set_text(cp, -1)
            
            elif name == 'a':
                self._active.key_input('All', None)

            elif name not in {'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R'}:
                self._active.key_input('Ctrl ' + name, chr(Gdk.keyval_to_unicode(e.keyval)))
        
        elif name in _special_keys:
            if name in _dead_keys:
                self._compositor.compose(name)
                self.SCREEN.queue_draw()
        
        elif self._compositor:
            self._compositor.key_input(name, chr(Gdk.keyval_to_unicode(e.keyval)), self._active.key_input)
            self.SCREEN.queue_draw()
        
        else:
            self._active.key_input(name, chr(Gdk.keyval_to_unicode(e.keyval)))
        
        self.SCREEN.queue_draw()
        self.KLOSSY.queue_draw()
        self.BECKY.queue_draw()
        
    def quit(self, w, e):
        GObject.source_remove(self._periodic)
        Gtk.main_quit()
        
def main():
    app = Display()
    Gtk.main()
