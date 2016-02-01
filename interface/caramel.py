from math import pi
from itertools import chain

from state import constants
from state import noticeboard
from state.ctext import Tract

from interface import poptarts
accent = poptarts.accent

from model import meredith, penclick
from model import un


def _draw_broken_bar(cr, x1, y1, x2, color_rgba, top):
    
    cr.set_source_rgba( * color_rgba)
    width = x2 - x1

    cross = 6
    gap = 6
    cr.rectangle(x1 - cross - gap, y1, cross, 1)
    cr.rectangle(x1, y1 - cross*top - gap*(top*2 - 1), 1, cross)

    cr.rectangle(x2 + gap, y1, cross, 1)
    cr.rectangle(x2, y1 - cross*top - gap*(top*2 - 1), 1, cross)
    cr.fill()
    
    cr.set_line_width(1)
    cr.set_dash([2, 5], 0)
    cr.move_to(x1 + gap, y1 + 0.5)
    cr.line_to(x2 - gap, y1 + 0.5)
    cr.stroke()
    
    cr.set_dash([], 0)
        
class Channels_controls(object):
    def __init__(self):
        self._mode = 'outlines'
        
        self._grid_controls = poptarts.Sprinkles()
        
        self._selected_point = (None, None, None)
        self._selected_portal = None

        # these are stateful
        self._hover_point = (None, None, None)
        self._hover_portal = (None, None)
    
    def press(self, x, y, name):
        un.history.undo_save(3)
        
        self._grid_controls.clear_selection()
        c, r, i, portal = meredith.mipsy.channel_point_select(x, y)
        
        if c is None:
            if name != 'ctrl':
                Tract.tract.channels.clear_selection()
            
            if self._grid_controls.press(x, y):
                self._mode = 'grid'
                return True
            else:
                return False
            
        else:
            self._mode = 'outlines'
            #clear selection
            if name != 'ctrl' and not Tract.tract.channels.is_selected(c, r, i):
                Tract.tract.channels.clear_selection()
            
            # MAKE SELECTIONS
            if i is not None:
                Tract.tract.channels.make_selected(c, r, i, name)

            elif portal is not None:
                if portal[0] == 'entrance':
                    Tract.tract.channels.make_selected(c, 0, 0, name)
                    Tract.tract.channels.make_selected(c, 1, 0, name)
                    r = 0
                    i = 0
                elif portal[0] == 'portal':
                    Tract.tract.channels.make_selected(c, 0, -1, name)
                    Tract.tract.channels.make_selected(c, 1, -1, name)
                    r = 1
                    i = len(Tract.tract.channels.channels[c].railings[1]) - 1

            if i is not None:
                self._sel_locale = tuple(Tract.tract.channels.channels[c].railings[r][i][:2])
                self._release_locale = self._sel_locale
            
            self._selected_point = (meredith.mipsy.C(), r, i)
            self._selected_portal = portal

            return True
    
    def press_motion(self, x, y):
        if self._mode == 'outlines':
            c, r, i = self._selected_point
            
            if i is not None:
                # if portal is selected
                if self._selected_portal is not None:
                    
                    if self._selected_portal[0] == 'entrance':
                        xo, yo = Tract.tract.channels.channels[c].railings[0][0][:2]
                        Tract.tract.channels.translate_selection(x - self._selected_portal[1], y - self._selected_portal[2], xo, yo)

                    elif self._selected_portal[0] == 'portal':
                        xo, yo = Tract.tract.channels.channels[c].railings[1][-1][:2]
                        Tract.tract.channels.translate_selection(x - self._selected_portal[1], y - self._selected_portal[2], xo, yo)

                # if point is selected
                elif self._selected_point[2] is not None:
                    xo, yo = Tract.tract.channels.channels[c].railings[r][i][:2]
                    Tract.tract.channels.translate_selection(x, y, xo, yo)
                    
                if self._sel_locale != tuple(Tract.tract.channels.channels[c].railings[r][i][:2]):
                    self._sel_locale = tuple(Tract.tract.channels.channels[c].railings[r][i][:2])
                    noticeboard.redraw_becky.push_change()
        elif self._mode == 'grid':
            # translate grid lines
            self._grid_controls.move_grid(x, y)

    def release(self):
        self._grid_controls.release()
        # if point is selected
        c, r, i = self._selected_point
        if i is not None:
            Tract.tract.channels.channels[c].fix(0)
            Tract.tract.channels.channels[c].fix(1)
        
            if self._release_locale != tuple(Tract.tract.channels.channels[c].railings[r][i][:2]):
                self._release_locale = tuple(Tract.tract.channels.channels[c].railings[r][i][:2])
                Tract.tract.deep_recalculate()
            else:
                un.history.pop()
    
    def key_input(self, name):

        if name in ['BackSpace', 'Delete']:
            if self._mode == 'outlines':
                c, r, i = self._selected_point
                if self._selected_portal is not None or (c is not None and i is None):
                    un.history.undo_save(3)
                    
                    # delete channel
                    del Tract.tract.channels.channels[c]
                    # wipe out entire tract if it's the last one
                    if not Tract.tract.channels.channels:
                        meredith.mipsy.delete_tract()

                else:
                    un.history.undo_save(3)
                    if not Tract.tract.channels.delete_selection():
                        un.history.pop()
                
                Tract.tract.deep_recalculate()
            
            elif self._mode == 'grid':
                self._grid_controls.del_grid()
                
        elif name == 'All':
            Tract.tract.channels.expand_selection(self._selected_point[0])
            
    
    def hover(self, x, y, hovered=[None, None]):
        
        c, r, i = Tract.tract.channels.target_point(x, y, meredith.mipsy.hover_page_context, 20)
        portal = None
        if c is None:
            c = Tract.tract.channels.target_channel(x, y, meredith.mipsy.hover_page_context, 20)

        self._hover_point = (c, r, i)
        
        if r is None and c is not None:
            portal = Tract.tract.channels.channels[c].target_portal(x, y, radius=5)
            # select multiple points
            if portal is not None:
                self._hover_portal = (c, portal[0])
            else:
                self._hover_portal = (None, None)

        if self._hover_point != hovered[0]:
            noticeboard.redraw_becky.push_change()
            hovered[0] = self._hover_point
        elif self._hover_portal != hovered[1]:
            noticeboard.redraw_becky.push_change()
            hovered[1] = self._hover_portal

    def render(self, cr, Tx, Ty, show_rails=False):            
            
        if show_rails:
            for c, channel in enumerate(Tract.tract.channels.channels):
                page = channel.page
                
                color = (0.3, 0.3, 0.3, 0.5)
                if (c, 'entrance') == self._hover_portal:
                    color = (0.3, 0.3, 0.3, 1)
                # draw portals            
                _draw_broken_bar(cr,
                        round( Tx(channel.railings[0][0][0] , page) ), 
                        round( Ty(channel.railings[0][0][1] , page) ),
                        round( Tx(channel.railings[1][0][0] , page) ),
                        color,
                        top = 1
                        )
                if (c, 'portal') == self._hover_portal:
                    color = (1, 0, 0.1, 1)
                else:
                    color = (1, 0, 0.1, 0.5)
                _draw_broken_bar(cr,
                        round( Tx(channel.railings[0][-1][0] , page) ), 
                        round( Ty(channel.railings[1][-1][1] , page) ),
                        round( Tx(channel.railings[1][-1][0] , page) ),
                        color,
                        top = 0
                        )
                # draw railings
                if c == self._selected_point[0]:
                    cr.set_source_rgba( * accent)
                    w = 2
                elif c == self._hover_point[0]:
                    cr.set_source_rgba( * accent, 0.7)
                    w = 1
                else:
                    cr.set_source_rgba( * accent, 0.5)
                    w = 1
                
                for r, railing in enumerate(channel.railings):
                    pts = [( Tx(p[0], page), Ty(p[1], page) ) for p in railing]
                    
                    cr.move_to(pts[0][0], pts[0][1])

                    for point in pts[1:]:
                        cr.line_to(point[0], point[1])

                    cr.set_line_width(w)
                    cr.stroke()

                    # draw selections
                    for i, p in enumerate(railing):
                        cr.arc( Tx(p[0], page), Ty(p[1], page), 3, 0, 2*pi)
                        if (c, r, i) == self._hover_point:
                            cr.set_source_rgba( * accent, 0.5)
                            cr.fill()
                            cr.set_source_rgba( * accent, 0.7)
                        else:
                            cr.fill()
                        if p[2]:
                            cr.arc( Tx(p[0], page), Ty(p[1], page), 5, 0, 2*pi)
                            cr.set_line_width(1)
                            cr.stroke()
    
            for channel in chain.from_iterable(tract.channels.channels for tract in meredith.mipsy.tracts[1:]):
                page = channel.page
                
                cr.set_source_rgba(0.3, 0.3, 0.3, 0.3)
                
                pts = [( Tx(p[0], page), Ty(p[1], page) ) for p in channel.railings[0] + list(reversed(channel.railings[1]))]
                cr.move_to(pts[0][0], pts[0][1])
                for point in pts[1:]:
                    cr.line_to(point[0], point[1])

                cr.close_path()
                cr.set_line_width(1)
                cr.stroke()

        else:
            for c, channel in enumerate(Tract.tract.channels.channels):
                page = channel.page
                
                color = (0.3, 0.3, 0.3, 0.5)
                if (c, 'entrance') == self._hover_portal:
                    color = (0.3, 0.3, 0.3, 1)
                # draw portals            
                _draw_broken_bar(cr,
                        round( Tx(channel.railings[0][0][0] , page) ), 
                        round( Ty(channel.railings[0][0][1] , page) ),
                        round( Tx(channel.railings[1][0][0] , page) ),
                        color,
                        top = 1
                        )
                if (c, 'portal') == self._hover_portal:
                    color = (1, 0, 0.1, 1)
                else:
                    color = (1, 0, 0.1, 0.5)
                _draw_broken_bar(cr,
                        round( Tx(channel.railings[0][-1][0] , page) ), 
                        round( Ty(channel.railings[1][-1][1] , page) ),
                        round( Tx(channel.railings[1][-1][0] , page) ),
                        color,
                        top = 0
                        )

    def render_grid(self, cr, px, py, p_h, p_k, A):
        self._grid_controls.render(cr, px, py, p_h, p_k, A)

delight = Channels_controls()
