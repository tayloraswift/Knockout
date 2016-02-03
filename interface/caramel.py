from math import pi
from itertools import chain

from state import noticeboard

from interface.poptarts import accent

from model import meredith, cursor
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
    def __init__(self, ctx, grid):
        self._mode = 'outlines'
        
        self._grid_controls = grid

        self._selected_point = [ctx['c'], None, None]
        self._selected_portal = (None, None, None)

        # these are stateful
        self._hover_point = (None, None, None)
        self._hover_portal = (None, None)
        
        self.PG = ctx['p']
        self.HPG = ctx['p']
        self.TRACT = meredith.mipsy[ctx['t']]
        self._CHANNELS = self.TRACT.channels

    def C(self):
        return self._selected_point[0]

    def target_select(self, x, y):
        xn, yn = meredith.page.normalize_XY(x, y, self.HPG)
        c, r, i = self._CHANNELS.target_point(xn, yn, self.HPG, 20)
        if c is None:
            # try different page
            binned_page = meredith.page.XY_to_page(x, y)
            xn, yn = meredith.page.normalize_XY(x, y, binned_page)
            
            c, r, i = self._CHANNELS.target_point(xn, yn, binned_page, 20)
            if c is not None:
                self.HPG = binned_page

        if c is not None and r is None:
            ptype, dpx, dpy = self._CHANNELS.channels[c].target_portal(xn, yn, radius=5)
            self._hover_portal = (c, ptype)

        self._hover_point = c, r, i

    def target(self, x, y):
        old_c = self._selected_point[0]
        xn, yn = meredith.page.normalize_XY(x, y, self.PG)
        c, r, i = self._CHANNELS.target_point(xn, yn, self.PG, 20)
        self._selected_point = [c, r, i]
        if c is not None:
            if c != old_c:
                noticeboard.refresh_properties_stack.push_change()
            if r is None:
                self._selected_portal = self._CHANNELS.channels[c].target_portal(xn, yn, radius=5)
            else:
                self._selected_portal = (None, 0, 0)
            return xn, yn

        # try different page
        binned_page = meredith.page.XY_to_page(x, y)
        xn, yn = meredith.page.normalize_XY(x, y, binned_page)
        
        c, r, i = self._CHANNELS.target_point(xn, yn, binned_page, 20)
        if c is not None:
            if c != old_c:
                noticeboard.refresh_properties_stack.push_change()
            self.PG = binned_page
            self._selected_point = [c, r, i]
            if r is None:
                self._selected_portal = self._CHANNELS.channels[c].target_portal(xn, yn, radius=5)
            return xn, yn
        
        # try different tract
        for tract in meredith.mipsy:
            c, r, i = tract.channels.target_point(xn, yn, binned_page, 20)
            if c is not None:
                noticeboard.refresh_properties_stack.push_change()
                self.PG = binned_page
                self._selected_point = [c, r, i]
                self.TRACT = tract
                self._CHANNELS = tract.channels
                return xn, yn
        
        self._selected_portal = (None, 0, 0)
        return xn, yn

    def press(self, x, y, name):
        un.history.undo_save(3)
        
        self._grid_controls.clear_selection()
        xn, yn = self.target(x, y)
        c, r, i = self._selected_point
        portal = self._selected_portal
        
        if c is None:
            if name != 'ctrl':
                self._CHANNELS.clear_selection()
            
            if self._grid_controls.press(xn, yn):
                self._mode = 'grid'
                return True
            else:
                return False
            
        else:
            self._mode = 'outlines'
            #clear selection
            if name != 'ctrl' and not self._CHANNELS.is_selected(c, r, i):
                self._CHANNELS.clear_selection()
            
            # MAKE SELECTIONS
            if i is not None:
                self._CHANNELS.make_selected(c, r, i, name)
                self._selected_portal = (None, None, None)

            elif portal[0] == 'entrance':
                self._CHANNELS.make_selected(c, 0, 0, name)
                self._CHANNELS.make_selected(c, 1, 0, name)
                r = 0
                i = 0
            elif portal[0] == 'portal':
                self._CHANNELS.make_selected(c, 0, -1, name)
                self._CHANNELS.make_selected(c, 1, -1, name)
                r = 1
                i = len(self._CHANNELS.channels[c].railings[1]) - 1
            
            elif r is not None:
                # insert point if one was not found
                i = self._CHANNELS.channels[c].insert_point(r, yn)
                self._CHANNELS.make_selected(c, r, i, name)
                self._selected_point[2] = 1

            if i is not None:
                self._sel_locale = tuple(self._CHANNELS.channels[c].railings[r][i][:2])
                self._release_locale = self._sel_locale

            return True
    
    def press_motion(self, x, y):
        x, y = meredith.page.normalize_XY(x, y, self.PG)
        if self._mode == 'outlines':
            c, r, i = self._selected_point
            portal, px, py = self._selected_portal
            
            if i is not None or portal is not None:
                if i is not None:
                    xo, yo = self._CHANNELS.channels[c].railings[r][i][:2]
                    self._CHANNELS.translate_selection(x, y, xo, yo)
                    
                    anchor = tuple(self._CHANNELS.channels[c].railings[r][i][:2])

                elif portal == 'entrance':
                    xo, yo = self._CHANNELS.channels[c].railings[0][0][:2]
                    self._CHANNELS.translate_selection(x - px, y - py, xo, yo)
                    
                    anchor = tuple(self._CHANNELS.channels[c].railings[0][0][:2])

                elif portal == 'portal':
                    xo, yo = self._CHANNELS.channels[c].railings[1][-1][:2]
                    self._CHANNELS.translate_selection(x - px, y - py, xo, yo)
                
                    anchor = tuple(self._CHANNELS.channels[c].railings[1][-1][:2])
                
                if self._sel_locale != anchor:
                        self._sel_locale = anchor
                        noticeboard.redraw_becky.push_change()
 
        elif self._mode == 'grid':
            # translate grid lines
            self._grid_controls.move_grid(x, y)

    def release(self):
        self._grid_controls.release()

        c, r, i = self._selected_point
        portal, px, py = self._selected_portal

        if i is not None or portal is not None:
            self._CHANNELS.channels[c].fix(0)
            self._CHANNELS.channels[c].fix(1)
            
            if i is not None:
                anchor = tuple(self._CHANNELS.channels[c].railings[r][i][:2])

            if portal == 'entrance':
                anchor = tuple(self._CHANNELS.channels[c].railings[0][0][:2])

            elif portal == 'portal':
                anchor = tuple(self._CHANNELS.channels[c].railings[1][-1][:2])

            if self._release_locale != anchor:
                self._release_locale = anchor
                self.TRACT.deep_recalculate()
                return
        
        un.history.pop()
    
    def key_input(self, name):

        if name in ['BackSpace', 'Delete']:
            if self._mode == 'outlines':
                c, r, i = self._selected_point
                portal, px, py = self._selected_portal
                if portal is not None or (c is not None and i is None):
                    un.history.undo_save(3)
                    
                    # delete channel
                    del self._CHANNELS.channels[c]
                    # wipe out entire tract if it's the last one
                    if not self._CHANNELS.channels:
                        old_tract = self.TRACT
                        meredith.mipsy.delete_tract(old_tract)
                        self.TRACT = meredith.mipsy[0]
                        self._CHANNELS = self.TRACT.channels
                        # cursor needs to be informed
                        if cursor.fcursor.TRACT is old_tract:
                            cursor.fcursor.assign_text(self.TRACT)
                            cursor.fcursor.TRACT = self.TRACT
                else:
                    un.history.undo_save(3)
                    if not self._CHANNELS.delete_selection():
                        un.history.pop()
                
                self.TRACT.deep_recalculate()
            
            elif self._mode == 'grid':
                self._grid_controls.del_grid()
                
        elif name == 'All':
            self._CHANNELS.expand_selection(self._selected_point[0])
            
    
    def hover(self, x, y, hovered=[None, None]):
        self.target_select(x, y)
        if self._hover_point != hovered[0]:
            noticeboard.redraw_becky.push_change()
            hovered[0] = self._hover_point
        elif self._hover_portal != hovered[1]:
            noticeboard.redraw_becky.push_change()
            hovered[1] = self._hover_portal

    def render(self, cr, Tx, Ty, show_rails=False):            
            
        if show_rails:
            for c, channel in enumerate(self._CHANNELS.channels):
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
    
            for channel in chain.from_iterable(tract.channels.channels for tract in meredith.mipsy if tract is not self.TRACT):
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
            for c, channel in enumerate(cursor.fcursor.TRACT.channels.channels):
                page = channel.page
                
                color = (0.3, 0.3, 0.3, 0.5)

                # draw portals            
                _draw_broken_bar(cr,
                        round( Tx(channel.railings[0][0][0] , page) ), 
                        round( Ty(channel.railings[0][0][1] , page) ),
                        round( Tx(channel.railings[1][0][0] , page) ),
                        color,
                        top = 1
                        )
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

