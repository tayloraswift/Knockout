from bisect import bisect

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject

from state import noticeboard, constants
from IO import un

from keyboard import compose

from meredith.settings import fontsettings

from interface import menu, splash

from IO import sierra

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
    def make_splash(self, recent):
        SPLASH = Gtk.DrawingArea()
        recent.set_reload_func(self.reload)
        splash_object = splash.Splash(recent, SPLASH.queue_draw)
        SPLASH.connect("draw", lambda w, cr: (cr.set_font_options(self._FO), splash_object.draw(cr)))
        SPLASH.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
        
        def press_splash(w, e):
            splash_object.press(e.x, e.y)
            self.overlay.remove(SPLASH)
        
        SPLASH.connect("button-press-event" , press_splash)
        SPLASH.connect("motion_notify_event", lambda w, e: splash_object.hover(e.x, e.y))
        self.overlay.add_overlay(SPLASH)

    def __init__(self):
        super(Display, self).__init__()
        
        self.SCREEN = Gtk.DrawingArea()
        self.SCREEN.connect("draw", self.DRAW_SCREEN)
        self.SCREEN.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.SCROLL_MASK)
        
        self.BECKY = Gtk.DrawingArea()
        self.BECKY.connect("draw", self.DRAW_BECKY)

        self.KLOSSY = Gtk.DrawingArea()
        self.KLOSSY.connect("draw", self.DRAW_KLOSSY)
        
        box = Gtk.Box()
        
        box.pack_start(self.BECKY, True, True, 0)
        box.pack_start(self.KLOSSY, False, False, 0)    
        
        self.overlay = overlay = Gtk.Overlay()
        overlay.add_overlay(box)
        overlay.add_overlay(self.SCREEN)
        self.add(overlay)
        
        self._compositor = compose.Compositor()
        
        self.SCREEN.connect("button-press-event"    , self._press_sort)
        self.SCREEN.connect("button-release-event"  , self._release_sort)
        self.SCREEN.connect("scroll-event"          , self._scroll_sort)
        self.SCREEN.connect("motion_notify_event"   , self._motion_sort)
        self.connect("key-press-event", self.on_key_press)
        self.connect("check-resize", self.on_resize)
        
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", self.quit)
        
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self._FO = fontsettings.fontoptions
        
        self.resize(1300, 800)
        
        self._periodic = GObject.timeout_add(2000, self._on_periodic)
    
    def _on_periodic(self):
        self._KT.PCURSOR.run_stats(spell=True)
        self.BECKY.queue_draw()
        self.KLOSSY.queue_draw()
        self.SCREEN.queue_draw()
        self.set_title(self._KT.filedata.filename + ' – Knockout')
        return True

    def set_regions(self, panes):
        self.panes      = panes
        self._KT        = panes.KT
        self._REGIONS   = panes.panes
        self._active_pane = False
        self.on_resize(None)
        self._internal_resize(panes.critical_width())
    
    def reload(self, name):
        self.set_regions(sierra.load(name))
        self._on_periodic()

    def DRAW_BECKY(self, w, cr):
        cr.set_font_options(self._FO)
        self._REGIONS[0].render(cr)

    def DRAW_KLOSSY(self, w, cr):
        cr.set_font_options(self._FO)
        self._REGIONS[1].render(cr)
        
    def DRAW_SCREEN(self, w, cr):
        self._compositor.draw(cr)
        menu.menu.render(cr)
    
    def on_resize(self, w):
        self.panes.resize( * self.get_size() )
    
    def _internal_resize(self, w):
        self.KLOSSY.set_size_request(w, 0)
        self.BECKY.queue_draw()
        self.KLOSSY.queue_draw()
        
    def _press_sort(self, w, e):
        if strike_menu(0, e):
            menu.menu.destroy()
            if self.panes.pane(e.x):
                self._active_pane = True
                return
            else:
                self._active_pane = False
            x, y = self.panes.set_active_region(e.x, e.y)
            
            if e.type == Gdk.EventType._2BUTTON_PRESS:
                if e.button == 1:
                    self.panes.active.dpress()
            
            elif e.type == Gdk.EventType.BUTTON_PRESS:
                if e.button == 1:
                    if e.state & Gdk.ModifierType.CONTROL_MASK:
                        char = 'ctrl'
                    else:
                        char = None
                    self.panes.active.press(x, y, char)
                
                elif e.button == 2:
                    self.panes.active.press_mid(x, y)
                
                elif e.button == 3:
                    self.panes.active.press_right(x, y)
        
        self.BECKY.queue_draw()
        self.KLOSSY.queue_draw()
        self.SCREEN.queue_draw()
        
    def _motion_sort(self, w, e):
        if strike_menu(1, e):
            if e.state & Gdk.ModifierType.BUTTON1_MASK:
                if self._active_pane:
                    self._internal_resize(self.panes.pane_resize(e.x))
                else:
                    self.panes.active.press_motion( * self.panes.convert(e.x, e.y, self.panes.A) )

            elif e.state & Gdk.ModifierType.BUTTON2_MASK:
                self.panes.active.drag( * self.panes.convert(e.x, e.y, self.panes.A) )
                
            else:
                x, y = self.panes.set_active_hover_region(e.x, e.y)
                self.panes.hover.hover(x, y)

        if noticeboard.redraw_overlay.should_refresh():
            self.SCREEN.queue_draw()
        if noticeboard.redraw_klossy.should_refresh():
            self.KLOSSY.queue_draw()
        if noticeboard.redraw_becky.should_refresh():
            self.BECKY.queue_draw()
        
    def _release_sort(self, w, e):
        self._active_pane = False
        if e.button == 1:
            x, y = self.panes.convert(e.x, e.y, self.panes.A)
            self.panes.active.release(x, y)
        
        elif e.button == 2:
            self.panes.active.drag(-1, -1)
            
        self.BECKY.queue_draw()
        self.KLOSSY.queue_draw()
        self.SCREEN.queue_draw()
        
    def _scroll_sort(self, w, e):
        if strike_menu(2, e):
            x, y = self.panes.convert(e.x, e.y, self.panes.H)
            
            if e.state & Gdk.ModifierType.CONTROL_MASK:
                char = 'ctrl'
            else:
                char = None

            # direction of scrolling stored as sign
            if e.direction == 1:
                self.panes.hover.scroll(x, y, char)
            elif e.direction == 0:
                self.panes.hover.scroll(x,-y, char)
        
        if noticeboard.redraw_overlay.should_refresh():
            self.SCREEN.queue_draw()
        if noticeboard.redraw_klossy.should_refresh():
            self.KLOSSY.queue_draw()
        if noticeboard.redraw_becky.should_refresh():
            self.BECKY.queue_draw()

    def on_key_press(self, w, e):

        name = Gdk.keyval_name(e.keyval)
        
        if e.state & Gdk.ModifierType.SHIFT_MASK and name == 'Return':
            self.panes.active.key_input('paragraph', None)
        
        elif e.state & Gdk.ModifierType.CONTROL_MASK:
            if e.state & Gdk.ModifierType.LOCK_MASK and name not in {'Shift_L', 'Shift_R'}:
                self.panes.active.key_input('Ctrl Lock', chr(Gdk.keyval_to_unicode(e.keyval)))
            
            elif name == 'z':
                un.history.back()
            elif name == 'y':
                un.history.forward()
            
            elif name == 'v':
                self.panes.active.key_input('Paste', self.clipboard.wait_for_text())

            elif name in {'c', 'x'}:
                if name == 'c':
                    cp = self.panes.active.key_input('Copy', None)
                else:
                    cp = self.panes.active.key_input('Cut', None)
                    
                if cp is not None: # must be preprocessed into string
                    self.clipboard.set_text(cp, -1)
            
            elif name == 'a':
                self.panes.active.key_input('All', None)

            elif name not in {'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R'}:
                self.panes.active.key_input('Ctrl ' + name, chr(Gdk.keyval_to_unicode(e.keyval)))
        
        elif name in _special_keys:
            if name in _dead_keys:
                self._compositor.compose(name)
                self.SCREEN.queue_draw()
        
        elif self._compositor:
            self._compositor.key_input(name, chr(Gdk.keyval_to_unicode(e.keyval)), self.panes.active.key_input)
            self.SCREEN.queue_draw()
        
        else:
            self.panes.active.key_input(name, chr(Gdk.keyval_to_unicode(e.keyval)))
        
        self.SCREEN.queue_draw()
        self.KLOSSY.queue_draw()
        self.BECKY.queue_draw()
        
    def quit(self, w, e):
        GObject.source_remove(self._periodic)
        Gtk.main_quit()
