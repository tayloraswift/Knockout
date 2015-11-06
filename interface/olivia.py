from math import pi

from state import constants
from state import noticeboard

from model import meredith
from model import channels


class Channels_controls(object):
    def __init__(self):
        self._selected_point = (None, None, None)
        self._selected_portal = None

        # these are stateful
        self._hover_point = (None, None, None)
        self._hover_portal = (None, None)
    
    def press(self, x, y, name):
        
        c, r, i = meredith.mipsy.tracts[meredith.mipsy.t].channels.target_point(x, y, 20)
        portal = None
        
        #clear selection
        if name != 'ctrl' and not meredith.mipsy.tracts[meredith.mipsy.t].channels.is_selected(c, r, i):
            meredith.mipsy.tracts[meredith.mipsy.t].channels.clear_selection()
            
        # switch
        if c is None:
            # target tract
            t, c = meredith.mipsy.target_channel(x, y, 20)
            meredith.mipsy.set_t(t)
        
        # perfect case, make point selected
        if i is not None:
            meredith.mipsy.tracts[meredith.mipsy.t].channels.make_selected(c, r, i)
            
            self._sel_locale = tuple(meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].railings[r][i][:2])
        
        elif c is None:
            c = meredith.mipsy.tracts[meredith.mipsy.t].channels.target_channel(x, y, 20)

        # an r of 0 evaluates to 'false' so we need None
        if r is not None and i is None:
            # insert point if one was not found

            i = meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].insert_point(r, y)
            
            self._sel_locale = tuple(meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].railings[r][i][:2])
        
        elif r is None and c is not None:
            portal = meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].target_portal(x, y, radius=5)
            # select multiple points
            if portal is not None:
                if portal[0] == 'entrance':
                    meredith.mipsy.tracts[meredith.mipsy.t].channels.make_selected(c, 0, 0)
                    meredith.mipsy.tracts[meredith.mipsy.t].channels.make_selected(c, 1, 0)
                elif portal[0] == 'portal':
                    meredith.mipsy.tracts[meredith.mipsy.t].channels.make_selected(c, 0, -1)
                    meredith.mipsy.tracts[meredith.mipsy.t].channels.make_selected(c, 1, -1)
        
        self._selected_point = (c, r, i)
        self._selected_portal = portal
        
        
        print (str(self._selected_point) + ' ' + str(self._selected_portal))
    
    def press_motion(self, x, y):
        # if point is selected
        if self._selected_point[2] is not None:
            c, r, i = self._selected_point
            xo, yo = meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].railings[r][i][:2]
            meredith.mipsy.tracts[meredith.mipsy.t].channels.translate_selection(x, y, xo, yo)
            
            if self._sel_locale != tuple(meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].railings[r][i][:2]):
                self._sel_locale = tuple(meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].railings[r][i][:2])
                noticeboard.refresh.push_change()
        
        # if portal is selected
        elif self._selected_portal is not None:
            c = self._selected_point[0]
            
            if self._selected_portal[0] == 'entrance':
                xo, yo = meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].railings[0][0][:2]
                meredith.mipsy.tracts[meredith.mipsy.t].channels.translate_selection(x - self._selected_portal[1], y - self._selected_portal[2], xo, yo)

            elif self._selected_portal[0] == 'portal':
                xo, yo = meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].railings[1][-1][:2]
                meredith.mipsy.tracts[meredith.mipsy.t].channels.translate_selection(x - self._selected_portal[1], y - self._selected_portal[2], xo, yo)
            
            # it’s too hard to determine this
            noticeboard.refresh.push_change()

    def release(self):
        # if point is selected
        if self._selected_point[0] is not None:
            meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[self._selected_point[0]].fix(0)
            meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[self._selected_point[0]].fix(1)
            meredith.mipsy.tracts[meredith.mipsy.t].deep_recalculate()
    
    def key_input(self, name):

        if name in ['BackSpace', 'Delete']:
            if self._selected_portal is not None:
                # delete channel
                del meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[self._selected_point[0]]
                # wipe out entire tract if it's the last one
                if not meredith.mipsy.tracts[meredith.mipsy.t].channels.channels:
                    del meredith.mipsy.tracts[meredith.mipsy.t]
                    meredith.mipsy.set_t(0)
            else:
                meredith.mipsy.tracts[meredith.mipsy.t].channels.delete_selection()
            meredith.mipsy.tracts[meredith.mipsy.t].deep_recalculate()
        elif name == 'All':
            meredith.mipsy.tracts[meredith.mipsy.t].channels.expand_selection(self._selected_point[0])
            
    
    def hover(self, x, y, hovered=[None, None]):
        
        c, r, i = meredith.mipsy.tracts[meredith.mipsy.t].channels.target_point(x, y, 20)
        portal = None
        if c is None:
            c = meredith.mipsy.tracts[meredith.mipsy.t].channels.target_channel(x, y, 20)

        self._hover_point = (c, r, i)
        
        if r is None and c is not None:
            portal = meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].target_portal(x, y, radius=5)
            # select multiple points
            if portal is not None:
                self._hover_portal = (c, portal[0])
            else:
                self._hover_portal = (None, None)

            

        if self._hover_point != hovered[0]:
            noticeboard.refresh.push_change()
            hovered[0] = self._hover_point
        elif self._hover_portal != hovered[1]:
            noticeboard.refresh.push_change()
            hovered[1] = self._hover_portal

    def _draw_broken_bar(self, cr, highlight, x1, y1, x2, color_rgba):
        
        cr.set_source_rgba( * color_rgba)
        width = x2 - x1
        cr.rectangle(x1, y1, width, 5)
        cr.clip()
        if highlight:
            for f in range( width//5 + 1):
                cr.move_to(x1 + 4*f, y1)

                cr.rel_line_to(2, 0)
                cr.rel_line_to(-4, 7)
                cr.rel_line_to(-2, 0)
        else:
            for f in range( width//4):
                cr.move_to(x1 + 4*f, y1)
                cr.rel_line_to(1.5, 0)
                cr.rel_line_to(-4, 7)
                cr.rel_line_to(-1.5, 0)
        cr.close_path()

        cr.fill()
        cr.reset_clip()

    def render(self, cr, Tx, Ty, show_rails=False):

        for c, channel in enumerate(meredith.mipsy.tracts[meredith.mipsy.t].channels.channels):
            bolden = False
            if (c, 'entrance') == self._hover_portal:
                bolden = True
            # draw portals            
            self._draw_broken_bar(cr, bolden, 
                    round( Tx(channel.railings[0][0][0]) ), 
                    round( Ty(channel.railings[0][0][1] - 5) ),
                    round( Tx(channel.railings[1][0][0]) ),
                    (0.3, 0.3, 0.3, 0.5))
            if (c, 'portal') == self._hover_portal:
                bolden = True
            else:
                bolden = False
            self._draw_broken_bar(cr, bolden, 
                    round( Tx(channel.railings[0][-1][0]) ), 
                    round( Ty(channel.railings[1][-1][1] - 5) ),
                    round( Tx(channel.railings[1][-1][0]) ),
                    (1, 0, 0.1, 0.5))
            
            # draw railings
            if c == self._hover_point[0]:
                cr.set_source_rgba(1, 0.2, 0.6, 1)
            else:
                cr.set_source_rgba(1, 0.2, 0.6, 0.5)
            
            if show_rails:
                for r, railing in enumerate(channel.railings):
                    pts = [( Tx(p[0]), Ty(p[1]) ) for p in railing]
                    
                    cr.move_to(pts[0][0], pts[0][1])

                    for point in pts[1:]:
                        cr.line_to(point[0], point[1])

                    cr.set_line_width(2)
                    cr.stroke()

                    # draw selections
                    for i, p in enumerate(railing):
                        cr.arc( Tx(p[0]), Ty(p[1]), 3, 0, 2*pi)
                        if (c, r, i) == self._hover_point:
                            cr.set_source_rgba(1, 0.2, 0.6, 0.5)
                            cr.fill()
                            cr.set_source_rgba(1, 0.2, 0.6, 1)
                        else:
                            cr.fill()
                        if p[2]:
                            cr.arc( Tx(p[0]), Ty(p[1]), 5, 0, 2*pi)
                            cr.set_line_width(1)
                            cr.stroke()

dibbles = Channels_controls()
