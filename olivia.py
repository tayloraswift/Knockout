import channels
import meredith

def edit_channels(x, y, state, selected = [[None, None, None], None]):
    if state == 'press':
        #clear selection
        meredith.mipsy.tracts[meredith.mipsy.t].channels.clear_selection()
        # target tract
        t, c = meredith.mipsy.target_channel(x, y, 20)
        meredith.mipsy.set_t(t)
        
        c, r, i = meredith.mipsy.tracts[meredith.mipsy.t].channels.target_point(x, y, 20)
        portal = None
        if c is None:
            c = meredith.mipsy.tracts[meredith.mipsy.t].channels.target_channel(x, y, 20)
        print((c, r, i))
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
            
        selected[0] = (c, r, i)
        selected[1] = portal
        print (selected)

    
    elif state == 'press_motion':
        # if point is selected
        if selected[0][2] is not None:
            c, r, i = selected[0]
            meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].move_point_to(r, i, x, y)
        
        # if portal is selected
        elif selected[1] is not None:
            c = selected[0][0]
            xx = x - selected[1][1]
            yy = y - selected[1][2]
            
            if selected[1][0] == 'entrance':
                meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].move_point_unconstrained(0, 0, xx + selected[1][3], yy + selected[1][4])
                meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].move_point_unconstrained(1, 0, xx + selected[1][5], yy + selected[1][4])
            elif selected[1][0] == 'portal':
                meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].move_point_unconstrained(0, -1, xx + selected[1][3], yy + selected[1][4])
                meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].move_point_unconstrained(1, -1, xx + selected[1][5], yy + selected[1][4])   
    
    elif state == 'release':
        # if point is selected
        if selected[0][2] is not None:
            c, r, i = selected[0]
            meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].fix(0)
            meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[c].fix(1)
            meredith.mipsy.tracts[meredith.mipsy.t].deep_recalculate()

        # if portal is selected
        elif selected[1] is not None:
            meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[selected[0][0]].fix(0)
            meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[selected[0][0]].fix(1)
            meredith.mipsy.tracts[meredith.mipsy.t].deep_recalculate()

    elif state == 'key':
        # x is being used at the character
        if x in ['BackSpace', 'Delete']:
            if selected[1] is not None:
                # delete channel
                del meredith.mipsy.tracts[meredith.mipsy.t].channels.channels[selected[0][0]]
            else:
                meredith.mipsy.tracts[meredith.mipsy.t].channels.delete_selection()
            meredith.mipsy.tracts[meredith.mipsy.t].deep_recalculate()
