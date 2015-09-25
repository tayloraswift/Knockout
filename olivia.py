import channels
import ui
import noticeboard
import meredith
from math import pi

class Channels_controls(object):
    def __init__(self):
        self._selected_point = (None, None, None)
        self._selected_portal = None

        # these are stateful
        self._hover_point = (None, None, None)
        self._hover_portal = (None, None)
    
    def press(self, x, y):
        #clear selection
        meredith.mipsy.tracts[meredith.mipsy.t].channels.clear_selection()
        # target tract
        t, c = meredith.mipsy.target_channel(x, y, 20)
        meredith.mipsy.set_t(t)
        
        c, r, i = meredith.mipsy.tracts[meredith.mipsy.t].channels.target_point(x, y, 20)
        portal = None
        
        # make point selected
        if i is not None:
            meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].railings[r][i][2] = True
        
        elif c is None:
            c = meredith.mipsy.tracts[meredith.mipsy.t].channels.target_channel(x, y, 20)

        # an r of 0 evaluates to 'false' so we need None
        if r is not None and i is None:
            # insert point if one was not found

            i = meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].insert_point(r, y)
        
        elif r is None:
            portal = meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].target_portal(x, y, radius=5)
            # select multiple points
            if portal is not None:
                if portal[0] == 'entrance':
                    print ('ENT')
                    meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].railings[0][0][2] = True
                    meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].railings[1][0][2] = True
                elif portal[0] == 'portal':
                    meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].railings[0][-1][2] = True
                    meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].railings[1][-1][2] = True
        
        self._selected_point = (c, r, i)
        self._selected_portal = portal
        
        print (str(self._selected_point) + ' ' + str(self._selected_portal))
    
    def press_motion(self, x, y):
        # if point is selected
        if self._selected_point[2] is not None:
            c, r, i = self._selected_point
            meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].move_point_to(r, i, x, y)
        
        # if portal is selected
        elif self._selected_portal is not None:
            c = self._selected_point[0]
            xx = x - self._selected_portal[1]
            yy = y - self._selected_portal[2]
            
            if self._selected_portal[0] == 'entrance':
                meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].move_point_unconstrained(0, 0, xx + self._selected_portal[3], yy + self._selected_portal[4])
                meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].move_point_unconstrained(1, 0, xx + self._selected_portal[5], yy + self._selected_portal[4])
            elif self._selected_portal[0] == 'portal':
                meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].move_point_unconstrained(0, -1, xx + self._selected_portal[3], yy + self._selected_portal[4])
                meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].move_point_unconstrained(1, -1, xx + self._selected_portal[5], yy + self._selected_portal[4])

    def release(self):
        # if point is selected
        if self._selected_point[2] is not None:
            c, r, i = self._selected_point
            meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].fix(0)
            meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].fix(1)
            meredith.mipsy.tracts[meredith.mipsy.t].deep_recalculate()

        # if portal is selected
        elif self._selected_portal is not None:
            meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[self._selected_point[0]].fix(0)
            meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[self._selected_point[0]].fix(1)
            meredith.mipsy.tracts[meredith.mipsy.t].deep_recalculate()
    
    def key_input(self, name):

        if name in ['BackSpace', 'Delete']:
            if self._selected_portal is not None:
                # delete channel
                del meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[self._selected_point[0]]
            else:
                meredith.mipsy.tracts[meredith.mipsy.t].channels.delete_selection()
            meredith.mipsy.tracts[meredith.mipsy.t].deep_recalculate()
    
    def hover(self, x, y, hovered=[None, None]):
        
        c, r, i = meredith.mipsy.tracts[meredith.mipsy.t].channels.target_point(x, y, 20)
        portal = None
        if c is None:
            c = meredith.mipsy.tracts[meredith.mipsy.t].channels.target_channel(x, y, 20)

        self._hover_point = (c, r, i)
        
        if r is None:
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


    def render(self, cr, show_rails):

        for c, channel in enumerate(meredith.mipsy.tracts[meredith.mipsy.t].channels.channels):
            bolden = False
            if (c, 'entrance') == self._hover_portal:
                bolden = True
            # draw portals            
            entrance = ui.Broken_bar(round(channel.railings[0][0][0] + 200), 
                    round(channel.railings[0][0][1] - 5 + 100),
                    round(channel.railings[1][0][0] + 200),
                    0.3, 0.3, 0.3, 0.5, bolden)
            if (c, 'portal') == self._hover_portal:
                bolden = True
            else:
                bolden = False
            portal = ui.Broken_bar(round(channel.railings[0][-1][0] + 200), 
                    round(channel.railings[1][-1][1] + 100),
                    round(channel.railings[1][-1][0] + 200),
                    1, 0, 0.1, 0.5, bolden)
            entrance.draw(cr)
            portal.draw(cr)
            
            # draw railings
            if c == self._hover_point[0]:
                cr.set_source_rgba(1, 0.2, 0.6, 1)
            else:
                cr.set_source_rgba(1, 0.2, 0.6, 0.7)
            
            if show_rails:
                for r, railing in enumerate(channel.railings):
                    pts = [(p[0] + 200, p[1] + 100) for p in railing]
                    
                    cr.move_to(pts[0][0], pts[0][1])

                    for point in pts[1:]:
                        cr.line_to(point[0], point[1])

                    cr.set_line_width(2)
                    cr.stroke()

                    # draw selections
                    for i, p in enumerate(railing):
                        cr.arc(p[0] + 200, p[1] + 100, 3, 0, 2*pi)
                        if (c, r, i) == self._hover_point:
                            cr.set_source_rgba(1, 0.2, 0.6, 0.5)
                            cr.fill()
                            cr.set_source_rgba(1, 0.2, 0.6, 1)
                        else:
                            cr.fill()
                        if p[2]:
                            cr.arc(p[0] + 200, p[1] + 100, 5, 0, 2*pi)
                            cr.set_line_width(1)
                            cr.stroke()

dibbles = Channels_controls()
