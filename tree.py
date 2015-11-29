from bisect import bisect

from state import constants

from interface import karlie
from interface import taylor
from interface import menu

UI_CELLS = [taylor.becky, karlie.klossy]

#                                                         click | hover
def take_event(x, y, event, key=False, char=None, region=[  0,      0  ]):

    if key:
        return UI_CELLS[region[0]].key_input(event, char)

                
    else:
        # Changing regions
        OVER = bisect(constants.UI, x) - 1

        if region[1] != OVER:
            UI_CELLS[region[1]].hover(-1, -1)
            region[1] = OVER
        
        if event in ('press', 'press_mid', 'press_right') and region[0] != OVER:
            # if we're going from properties to document, dump properties
            if isinstance(UI_CELLS[region[0]], karlie._Properties_panel):
                UI_CELLS[region[0]].press(-1, -1, None)
            region[0] = OVER


        # MENU
        if menu.menu.menu():
            if event == 'scroll':
                if menu.menu.in_bounds(x, abs(y)):
                    menu.menu.scroll(y)
                    menu.menu.test_change()
                    return
                
            elif menu.menu.in_bounds(x, y):
                if event == 'motion':
                    menu.menu.hover(y)
                    menu.menu.test_change()
                
                elif event == 'press':
                    menu.menu.press(y)
            
                return
        #############
        
        # motion and scrolling operates under the hover context
        if event == 'motion':
            x -= constants.UI[region[1]]
            UI_CELLS[region[1]].hover(x, y)
        
        elif event == 'scroll':
            x -= constants.UI[region[1]]
            UI_CELLS[region[1]].scroll(x, y, char)

        # others operate under the click context
        else:
            x -= constants.UI[region[0]]
            
            if event == 'press':
                menu.menu.destroy()
                UI_CELLS[region[0]].press(x, y, char)
            
            elif event == 'press2':
                UI_CELLS[region[0]].dpress()
            
            elif event == 'press_motion':
                UI_CELLS[region[0]].press_motion(x, y)

            elif event == 'press_mid':
                menu.menu.destroy()
                UI_CELLS[region[0]].press_mid(x, y)
            
            elif event == 'press_right':
                menu.menu.destroy()
                UI_CELLS[region[0]].press_right(x, y)

            elif event == 'drag':
                UI_CELLS[region[0]].drag(x, y)

            elif event == 'release':
                UI_CELLS[region[0]].release(x, y)
            
